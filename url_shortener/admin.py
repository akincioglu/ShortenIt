from django.contrib import admin
from .models import Account, ShortenedURL, URLAccess

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'api_key', 'daily_limit', 'created_at')
    search_fields = ('user__username', 'api_key')

@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'original_url', 'account', 'created_at', 'access_count')
    search_fields = ('short_code', 'original_url')
    list_filter = ('created_at',)

@admin.register(URLAccess)
class URLAccessAdmin(admin.ModelAdmin):
    list_display = ('url', 'accessed_at', 'ip_address')
    list_filter = ('accessed_at',)
    search_fields = ('ip_address', 'user_agent')
