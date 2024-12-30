import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from url_shortener.models import Account, ShortenedURL, URLAccess
from django.utils import timezone

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def account(user):
    return Account.objects.create(user=user)

@pytest.fixture
def auth_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_login(user)
    return api_client

@pytest.fixture
def api_authenticated_client(api_client, auth_token):
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {auth_token.key}')
    return api_client

@pytest.mark.django_db
class TestAuthViews:
    def test_register(self, api_client):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == 302  # Redirect after successful registration
        assert User.objects.filter(username='newuser').exists()
        assert Account.objects.filter(user__username='newuser').exists()

    def test_login(self, api_client, user):
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == 302  # Redirect after successful login

@pytest.mark.django_db
class TestURLShortenerViews:
    def test_shorten_url_authenticated(self, authenticated_client, account):
        url = reverse('shorten_url')
        data = {'original_url': 'https://example.com'}
        response = authenticated_client.post(url, data)
        assert response.status_code == 302  # Changed to 302 since it redirects
        assert ShortenedURL.objects.filter(original_url='https://example.com').exists()

    def test_shorten_url_unauthenticated(self, api_client):
        url = reverse('shorten_url')
        data = {'original_url': 'https://example.com'}
        response = api_client.post(url, data)
        assert response.status_code == 302  # Redirect to login

    def test_url_list(self, authenticated_client, account):
        # Create some test URLs
        ShortenedURL.objects.create(
            account=account,
            original_url='https://example.com',
            short_code='abc123'
        )
        url = reverse('url_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200  # Should be 200 since user is authenticated
        assert b'abc123' in response.content

    def test_redirect_to_original(self, api_client, account):
        shortened = ShortenedURL.objects.create(
            account=account,
            original_url='https://example.com',
            short_code='abc123'
        )
        response = api_client.get(f'/abc123/')
        assert response.status_code == 302  # Redirect to original URL
        
        # Check if access was logged
        assert URLAccess.objects.filter(url=shortened).exists()
        shortened.refresh_from_db()
        assert shortened.access_count == 1

    def test_daily_limit_frontend(self, authenticated_client, account):
        # Set daily limit to 2
        account.daily_limit = 2
        account.save()

        url = reverse('shorten_url')
        
        # First URL - should succeed
        response1 = authenticated_client.post(url, {'original_url': 'https://example1.com'})
        assert response1.status_code == 302  # Redirect after success
        assert ShortenedURL.objects.filter(original_url='https://example1.com').exists()
        
        # Second URL - should succeed
        response2 = authenticated_client.post(url, {'original_url': 'https://example2.com'})
        assert response2.status_code == 302  # Redirect after success
        assert ShortenedURL.objects.filter(original_url='https://example2.com').exists()
        
        # Third URL - should fail
        response3 = authenticated_client.post(url, {'original_url': 'https://example3.com'})
        assert response3.status_code == 302  # Redirect after error
        assert not ShortenedURL.objects.filter(original_url='https://example3.com').exists()
        
        # Verify total count
        today_count = ShortenedURL.objects.filter(
            account=account,
            created_at__date=timezone.now().date()
        ).count()
        assert today_count == 2  # Should not exceed daily limit

@pytest.mark.django_db
class TestAPIViews:
    def test_obtain_auth_token(self, api_client, user):
        url = reverse('api_token')  # Changed from 'obtain-auth-token' to 'api_token'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data)
        assert response.status_code == 200
        assert 'token' in response.json()

    def test_create_shortened_url_api(self, api_authenticated_client, account):
        url = reverse('shortenedurl-list')
        data = {'original_url': 'https://example.com'}
        response = api_authenticated_client.post(url, data)
        assert response.status_code == 201
        assert ShortenedURL.objects.filter(original_url='https://example.com').exists()

    def test_daily_limit(self, api_authenticated_client, account):
        url = reverse('shortenedurl-list')
        # Set daily limit to 1
        account.daily_limit = 1
        account.save()

        # First request should succeed
        response1 = api_authenticated_client.post(url, {'original_url': 'https://example1.com'})
        assert response1.status_code == 201

        # Second request should fail due to limit
        response2 = api_authenticated_client.post(url, {'original_url': 'https://example2.com'})
        assert response2.status_code == 400
        assert 'error' in response2.json()

    def test_url_analytics(self, api_authenticated_client, account):
        # Create a URL and some access logs
        shortened = ShortenedURL.objects.create(
            account=account,
            original_url='https://example.com',
            short_code='abc123'
        )
        URLAccess.objects.create(
            url=shortened,
            ip_address='127.0.0.1',
            user_agent='test-agent'
        )

        url = reverse('urlaccess-list')
        response = api_authenticated_client.get(url)
        assert response.status_code == 200
        assert len(response.json()) == 1 