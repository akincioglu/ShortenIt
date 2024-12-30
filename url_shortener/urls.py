from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'urls', views.ShortenedURLViewSet, basename='shortenedurl')
router.register(r'analytics', views.URLAccessViewSet, basename='urlaccess')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', views.obtain_auth_token, name='api_token'),
    path('<str:short_code>/', views.redirect_to_original, name='redirect'),
] 