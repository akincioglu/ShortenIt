from rest_framework import viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import string
import random
from .models import Account, ShortenedURL, URLAccess
from .serializers import AccountSerializer, ShortenedURLSerializer, URLAccessSerializer
from django.core.cache import cache

# Frontend Views
def home(request):
    context = {}
    if request.user.is_authenticated:
        account = Account.objects.get(user=request.user)
        today_count = ShortenedURL.objects.filter(
            account=account,
            created_at__date=timezone.now().date()
        ).count()
        context['daily_limit'] = account.daily_limit - today_count
    return render(request, 'url_shortener/home.html', context)

@login_required
def url_list(request):
    urls = ShortenedURL.objects.filter(account__user=request.user).order_by('-created_at')
    return render(request, 'url_shortener/url_list.html', {'urls': urls})

def validate_and_format_url(url):
    """Add https:// prefix if not present and validate URL format"""
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    return url

@login_required
def shorten_url(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        if original_url:
            # Format and validate URL
            original_url = validate_and_format_url(original_url)
            
            # Check daily limit
            today_count = ShortenedURL.objects.filter(
                account=request.user.account,
                created_at__date=timezone.now().date()
            ).count()

            if today_count >= request.user.account.daily_limit:
                messages.error(request, 'Daily URL shortening limit exceeded')
                return redirect('home')

            # Create shortened URL
            short_code = generate_short_code()
            shortened_url = ShortenedURL.objects.create(
                account=request.user.account,
                original_url=original_url,
                short_code=short_code
            )

            # Get the full shortened URL
            shortened_url_path = request.build_absolute_uri(f'/{short_code}/')
            messages.success(request, f'URL shortened successfully! Your shortened URL is: {shortened_url_path}')
            return redirect('home')

    return redirect('home')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'url_shortener/login.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'url_shortener/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'url_shortener/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        Account.objects.create(user=user)
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'url_shortener/register.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

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
    
    list:
        Kullanıcının hesap bilgilerini listeler.
        
        Dönüş:
            - id: Hesap ID'si
            - api_key: API anahtarı
            - daily_limit: Günlük URL kısaltma limiti
            - created_at: Hesap oluşturulma tarihi
            - updated_at: Son güncelleme tarihi
    
    retrieve:
        Belirli bir hesabın detaylarını döndürür.
    
    update:
        Hesap bilgilerini günceller.
        
        Parametreler:
            - daily_limit: Yeni günlük URL kısaltma limiti
    
    partial_update:
        Hesap bilgilerini kısmen günceller.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Kullanıcının hesap bilgilerini listeler",
        responses={
            200: AccountSerializer(many=True),
            401: "Yetkilendirme hatası"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir hesabın detaylarını döndürür",
        responses={
            200: AccountSerializer,
            401: "Yetkilendirme hatası",
            404: "Hesap bulunamadı"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Hesap bilgilerini günceller",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'daily_limit': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Yeni günlük URL kısaltma limiti'
                ),
            },
        ),
        responses={
            200: AccountSerializer,
            400: "Geçersiz veri",
            401: "Yetkilendirme hatası"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Hesap bilgilerini kısmen günceller",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'daily_limit': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Yeni günlük URL kısaltma limiti'
                ),
            },
        ),
        responses={
            200: AccountSerializer,
            400: "Geçersiz veri",
            401: "Yetkilendirme hatası"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Account.objects.none()
        return Account.objects.filter(user=self.request.user)

class ShortenedURLViewSet(viewsets.ModelViewSet):
    """
    URL kısaltma işlemleri için API endpoint'leri.
    
    list:
        Kısaltılmış URL'lerin listesini döndürür.
    
    create:
        Yeni bir URL kısaltır.
        
        Parametreler:
            - original_url: Kısaltılacak orijinal URL
            
        Dönüş:
            - id: URL ID'si
            - original_url: Orijinal URL
            - short_code: Kısaltılmış kod
            - created_at: Oluşturulma tarihi
            - last_accessed: Son erişim tarihi
            - access_count: Erişim sayısı
    
    retrieve:
        Belirli bir kısaltılmış URL'nin detaylarını döndürür.
    
    delete:
        Belirli bir kısaltılmış URL'yi siler.
    """
    serializer_class = ShortenedURLSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    lookup_field = 'short_code'

    @swagger_auto_schema(
        operation_description="Kısaltılmış URL'lerin listesini döndürür",
        responses={
            200: ShortenedURLSerializer(many=True),
            401: "Yetkilendirme hatası"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Yeni bir URL kısaltır",
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
            400: "Geçersiz URL veya günlük limit aşıldı",
            401: "Yetkilendirme hatası"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir kısaltılmış URL'nin detaylarını döndürür",
        responses={
            200: ShortenedURLSerializer,
            401: "Yetkilendirme hatası",
            404: "URL bulunamadı"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir kısaltılmış URL'yi siler",
        responses={
            204: "URL başarıyla silindi",
            401: "Yetkilendirme hatası",
            404: "URL bulunamadı"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ShortenedURL.objects.none()
        return ShortenedURL.objects.filter(account__user=self.request.user)

    def perform_create(self, serializer):
        account = self.request.user.account
        
        # Check daily limit
        today_count = ShortenedURL.objects.filter(
            account=account,
            created_at__date=timezone.now().date()
        ).count()
        
        if today_count >= account.daily_limit:
            raise serializers.ValidationError(
                {"error": "Daily URL shortening limit exceeded"}
            )
        
        # Generate short code
        short_code = generate_short_code()
        serializer.save(account=account, short_code=short_code)

    def validate_original_url(self, value):
        """Validate and format the URL before saving"""
        return validate_and_format_url(value)

def get_cached_url(short_code):
    cache_key = f'url_{short_code}'
    return cache.get(cache_key)

def cache_url(short_code, original_url):
    cache_key = f'url_{short_code}'
    cache.set(cache_key, original_url, timeout=settings.URL_CACHE_TTL)

@swagger_auto_schema(
    method='get',
    operation_description="Kısa URL'yi kullanarak orijinal URL'ye yönlendir",
    manual_parameters=[
        openapi.Parameter(
            'short_code',
            openapi.IN_PATH,
            description="Kısaltılmış URL kodu",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    responses={
        302: "Orijinal URL'ye yönlendirme",
        404: "URL bulunamadı"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def redirect_to_original(request, short_code):
    shortened_url = get_object_or_404(ShortenedURL, short_code=short_code)
    
    # Log access
    URLAccess.objects.create(
        url=shortened_url,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Update access count and last accessed time
    shortened_url.access_count += 1
    shortened_url.last_accessed = timezone.now()
    shortened_url.save()
    
    return redirect(shortened_url.original_url)

class URLAccessViewSet(viewsets.ReadOnlyModelViewSet):
    """
    URL erişim istatistikleri için API endpoint'leri.
    
    list:
        Tüm URL erişim kayıtlarını listeler.
        
        Dönüş:
            - id: Erişim kaydı ID'si
            - accessed_at: Erişim tarihi
            - ip_address: Erişim yapan IP adresi
            - user_agent: Erişim yapan tarayıcı bilgisi
    
    retrieve:
        Belirli bir erişim kaydının detaylarını döndürür.
    """
    serializer_class = URLAccessSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    @swagger_auto_schema(
        operation_description="Tüm URL erişim kayıtlarını listeler",
        responses={
            200: URLAccessSerializer(many=True),
            401: "Yetkilendirme hatası"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Belirli bir erişim kaydının detaylarını döndürür",
        responses={
            200: URLAccessSerializer,
            401: "Yetkilendirme hatası",
            404: "Erişim kaydı bulunamadı"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return URLAccess.objects.none()
        return URLAccess.objects.filter(url__account__user=self.request.user)
