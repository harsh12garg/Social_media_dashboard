# Social Media Dashboard

A simple dashboard to display your Facebook and Twitter social media activity.

## Project Structure

```
social_media_dashboard/
├── dashboard/                 # Main application directory
│   ├── migrations/           # Database migrations
│   ├── templates/            # HTML templates
│   │   └── dashboard/       
│   ├── templatetags/         # Custom template tags
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Database models
│   ├── urls.py              # URL routing
│   └── views.py             # View functions
├── social_dashboard/         # Project settings directory
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── manage.py                # Django management script
├── db.sqlite3               # SQLite database
└── requirements.txt         # Project dependencies
```

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12 or higher
- pip (Python package manager)
- Git

## Setting Up Locally

1. Clone the repository:
   ```powershell
   git clone <repository-url>
   cd social_media_dashboard
   ```

2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install required packages:
   ```powershell
   pip install django==5.2.1 requests tweepy
   pip freeze > requirements.txt
   ```

4. Set up environment variables (create a .env file):
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

5. Initialize the database:
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser (admin account):
   ```powershell
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```powershell
   python manage.py runserver
   ```

8. Open your browser and visit: http://127.0.0.1:8000/

## Setting Up Social Media APIs

### For Facebook:

1. Go to [Facebook for Developers](https://developers.facebook.com/)
2. Create a new app
3. Get your App ID and App Secret from the app dashboard
4. Go to http://127.0.0.1:8000/facebook/config/ after logging in
5. Enter your Facebook credentials:
   - App ID
   - App Secret
   - Access Token (with required permissions)

Required Facebook Permissions:
- email
- public_profile
- user_posts
- user_photos
- user_likes

### For Twitter:

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a project and app
3. Get your API credentials
4. Go to http://127.0.0.1:8000/twitter/config/ after logging in
5. Enter your Twitter credentials:
   - API Key
   - API Secret
   - Access Token
   - Access Token Secret

## Features

- User authentication (register/login/logout)
- Platform selection (Facebook/Twitter)
- Profile information display
- Recent posts and activity feed
- Analytics dashboard
- Secure credential storage

## Development

- The project uses Django 5.2.1
- SQLite database for development
- Template-based views with custom template tags
- User authentication and session management
- Secure credential storage using JSON files

## Safety Tips

- Never commit API keys or credentials to version control
- Use environment variables for sensitive data in production
- Regularly update dependencies for security patches
- Enable DEBUG only in development
- Use HTTPS in production

## Troubleshooting

1. If you get a "No module named 'django'" error:
   - Ensure your virtual environment is activated
   - Reinstall Django: `pip install django`

2. Database migration issues:
   - Delete db.sqlite3 and migrations folders
   - Run `python manage.py makemigrations` and `python manage.py migrate`

3. Social media API connection issues:
   - Verify your API credentials
   - Check your internet connection
   - Ensure required permissions are granted

## License

MIT