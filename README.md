# URL Shortener

A modern Django-based URL shortening service with a beautiful UI and powerful features.

## Features

- User account management with authentication
- Modern and responsive UI with Bootstrap
- URL shortening with custom short codes
- Daily URL shortening quota (default: 50)
- URL usage statistics and analytics
- Copy to clipboard functionality
- Real-time remaining quota display
- Relative time display (e.g., "5 minutes ago")
- Redis caching for faster URL serving
- Swagger API documentation

## Installation

1. Clone the repository:

```bash
git clone https://github.com/akincioglu/shortenit.git
cd shortenit
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Install and start Redis server (for caching):

   - Windows: Download and install from [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
   - Linux/Mac: `sudo apt-get install redis-server` or `brew install redis`

5. Apply database migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Start the development server:

```bash
python manage.py runserver
```

## Usage

1. Register a new account or login with existing credentials
2. Enter a URL to shorten in the input field
3. Click "Shorten" to generate a shortened URL
4. Use the copy button to copy the shortened URL
5. View your URLs and their statistics in the URL list
6. Delete URLs you no longer need

## API Documentation

The API documentation is available through Swagger UI at `/swagger/` endpoint. You can:

- Test API endpoints directly
- View request/response schemas
- Get detailed information about each endpoint

## API Endpoints

### Authentication

- `POST /api/token/` - Obtain authentication token
- `POST /api/register/` - Register new user
- `POST /api/login/` - User login

### URL Operations

- `POST /api/urls/` - Shorten a URL
- `GET /api/urls/` - List shortened URLs
- `GET /api/urls/{id}/` - Get URL details
- `DELETE /api/urls/{id}/` - Delete a shortened URL

### Redirection

- `GET /{short_code}/` - Redirect to original URL

## Quota Limits

- Daily URL shortening limit: 50 URLs per user
- Real-time quota display in the UI
- Appropriate error messages when quota is exceeded

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## Testing

Run the test suite:

```bash
pytest
```

Tests cover:

- URL shortening functionality
- User authentication
- Daily quota limits
- URL redirection
- API endpoints

## Technologies Used

- Django & Django REST Framework
- Redis for caching
- Bootstrap for UI
- Font Awesome for icons
- Pytest for testing
- Swagger for API documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.
