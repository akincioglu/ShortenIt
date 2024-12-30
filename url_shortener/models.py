from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.conf import settings

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    daily_limit = models.IntegerField(default=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Account"

class ShortenedURL(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='urls')
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

class URLAccess(models.Model):
    url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name='access_logs')
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-accessed_at']
