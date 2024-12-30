from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'accounts', views.AccountViewSet, basename='account')
router.register(r'urls', views.ShortenedURLViewSet, basename='shortenedurl')
router.register(r'analytics', views.URLAccessViewSet, basename='urlaccess')

urlpatterns = [
    # Frontend URLs
    path('', views.home, name='home'),
    path('urls/', views.url_list, name='url_list'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/token/', views.obtain_auth_token, name='api_token'),
    
    # Redirect URL (keep this last)
    path('<str:short_code>/', views.redirect_to_original, name='redirect'),
] 