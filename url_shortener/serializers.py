from rest_framework import serializers
from .models import Account, ShortenedURL, URLAccess

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'api_key', 'daily_limit', 'created_at', 'updated_at']
        read_only_fields = ['api_key']

class ShortenedURLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortenedURL
        fields = ['id', 'original_url', 'short_code', 'created_at', 'last_accessed', 'access_count']
        read_only_fields = ['short_code', 'last_accessed', 'access_count']

class URLAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = URLAccess
        fields = ['id', 'accessed_at', 'ip_address', 'user_agent'] 