from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import string
import random
from .models import Account, ShortenedURL, URLAccess
from .serializers import AccountSerializer, ShortenedURLSerializer, URLAccessSerializer

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Kullanıcı adı'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Şifre'),
        },
    ),
    responses={
        200: openapi.Response(
            description="Başarılı giriş",
            examples={
                "application/json": {
                    "token": "your-auth-token",
                    "user_id": 1,
                    "username": "example",
                    "daily_limit": 50
                }
            }
        ),
        400: "Geçersiz istek",
        401: "Geçersiz kimlik bilgileri"
    },
    operation_description="Kullanıcı adı ve şifre ile API token'ı alın"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def obtain_auth_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if username is None or password is None:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get or create token
    token, created = Token.objects.get_or_create(user=user)
    
    # Create account if it doesn't exist
    account, created = Account.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.pk,
        'username': user.username,
        'daily_limit': account.daily_limit
    })

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if not ShortenedURL.objects.filter(short_code=code).exists():
            return code

class AccountViewSet(viewsets.ModelViewSet):
    """
    Account yönetimi için API endpoint'leri.
    
    * Hesap bilgilerini görüntüleme
    * Günlük URL kısaltma limitini güncelleme
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Account.objects.none()
        return Account.objects.filter(user=self.request.user)

class ShortenedURLViewSet(viewsets.ModelViewSet):
    """
    URL kısaltma işlemleri için API endpoint'leri.
    
    * URL kısaltma
    * Kısaltılmış URL'leri listeleme
    * URL detaylarını görüntüleme
    """
    serializer_class = ShortenedURLSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShortenedURL.objects.none()
        return ShortenedURL.objects.filter(account__user=self.request.user)

    @swagger_auto_schema(
        operation_description="Yeni bir URL kısalt. Günlük limit: 50 URL",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['original_url'],
            properties={
                'original_url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_URI,
                    description='Kısaltılacak orijinal URL'
                ),
            },
        ),
        responses={
            201: ShortenedURLSerializer,
            400: "Geçersiz URL veya günlük limit aşıldı"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        account = self.request.user.account
        account.reset_daily_usage()  # Reset if it's a new day

        if account.daily_limit <= 0:
            raise serializers.ValidationError(
                {"error": "Daily URL shortening limit exceeded"}
            )

        short_code = generate_short_code()
        serializer.save(account=account, short_code=short_code)
        account.increment_usage()

@swagger_auto_schema(
    method='get',
    operation_description="Kısa URL'yi kullanarak orijinal URL'ye yönlendir",
    responses={
        302: "Orijinal URL'ye yönlendirme",
        404: "URL bulunamadı"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def redirect_to_original(request, short_code):
    url = get_object_or_404(ShortenedURL, short_code=short_code)
    
    # Log access
    URLAccess.objects.create(
        url=url,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT'),
        referer=request.META.get('HTTP_REFERER')
    )
    
    # Update stats
    url.update_access_stats()
    
    return redirect(url.original_url)

class URLAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    URL erişim istatistikleri için API endpoint'leri.
    
    * URL'lere yapılan erişimleri görüntüleme
    * Erişim detaylarını (IP, User Agent, vb.) görüntüleme
    """
    serializer_class = URLAccessSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return URLAccess.objects.none()
        return URLAccess.objects.filter(url__account__user=self.request.user)
