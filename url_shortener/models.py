from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from django.conf import settings

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    api_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    daily_limit = models.IntegerField(default=50)
    daily_usage = models.IntegerField(default=0)
    last_usage_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Account"

    def reset_daily_usage(self):
        """Reset daily usage if it's a new day"""
        today = timezone.now().date()
        if self.last_usage_date != today:
            self.daily_usage = 0
            self.last_usage_date = today
            self.daily_limit = settings.URL_SHORTENER_SETTINGS['DAILY_LIMIT']
            self.save()

    def increment_usage(self):
        """Increment daily usage and check limit"""
        self.reset_daily_usage()  # Reset if it's a new day
        self.daily_usage += 1
        self.daily_limit = settings.URL_SHORTENER_SETTINGS['DAILY_LIMIT'] - self.daily_usage
        self.save()

class ShortenedURL(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='urls')
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

    def update_access_stats(self):
        self.access_count += 1
        self.last_accessed = timezone.now()
        self.save()

class URLAccess(models.Model):
    url = models.ForeignKey(ShortenedURL, on_delete=models.CASCADE, related_name='access_logs')
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referer = models.URLField(max_length=2048, null=True, blank=True)

    class Meta:
        ordering = ['-accessed_at']
