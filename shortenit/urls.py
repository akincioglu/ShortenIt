"""
URL configuration for shortenit project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from url_shortener.urls import api_urlpatterns, frontend_urlpatterns, redirect_urlpatterns

schema_view = get_schema_view(
    openapi.Info(
        title="URL Shortener API",
        default_version='v1',
        description="API for shortening and managing URLs",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@shortenit.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='http://127.0.0.1:8000',
    patterns=[path('api/', include(api_urlpatterns))],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs including Swagger
    path('api/', include([
        path('', include(api_urlpatterns)),
        path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ])),
    
    # Frontend URLs
    path('', include(frontend_urlpatterns)),
    
    # URL Shortener redirect (keep this last)
    path('', include(redirect_urlpatterns)),
]
