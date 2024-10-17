# ewelink_smart_relay

A Django-based web application that manages access control for a door system using Ewelink smart relays. This project allows users to generate time-limited access tokens and use them to unlock a door via a webhook integration.

## Background

The ewelink_smart_relay project is designed to provide a flexible and secure solution for managing access to doors equipped with Ewelink smart relays. It bridges the gap between digital access control and physical door locks, offering a web-based interface for token generation and management.

Key features include:
- Generation of time-limited access tokens
- Secure storage and validation of tokens
- Integration with Ewelink smart relays through webhooks
- User-friendly web interface for token management and door unlocking

This system is ideal for environments where temporary or controlled access is required, such as office spaces, co-working areas, or smart home setups.

## Hardware Requirements

This project is designed to work with the following smart relay model:

- **Model Name**: EWELINK-1CH 10A

Ensure you have this specific model or a compatible eWeLink smart relay for optimal performance.

## eWeLink Account Setup

To use this application, you need to set up an eWeLink account and configure your smart relay. Follow these steps:

1. Create an eWeLink account at [https://www.ewelink.cc/en/](https://www.ewelink.cc/en/)
2. Add your EWELINK-1CH 10A smart relay to your account following the manufacturer's instructions
3. In your eWeLink account settings, locate the webhook information. This typically includes a URL and possibly an API key or token
4. Use this webhook information in your project's `.env` file (see Setup Instructions below)

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/furkanzkafka/ewelink_smart_relay.git
   cd ewelink_smart_relay
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root and add the following environment variables:
   ```
   DJANGO_SECRET_KEY=your_secret_key_here
   DEBUG=True
   WEBHOOK_URL=your_ewelink_webhook_url_here
   ```
   Replace `your_ewelink_webhook_url_here` with the webhook URL from your eWeLink account.

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

## Project Structure

- `ewelink_smart_relay/`: Main project directory
  - `settings.py`: Project settings
  - `urls.py`: Main URL configuration
- `door_access/`: App directory
  - `views.py`: Contains the main logic for door access
  - `urls.py`: URL patterns for the door_access app
  - `models.py`: Database models for access tokens

## Key Features

- Home page with active token display
- Token generation with expiration
- Door unlocking mechanism using eWeLink webhooks
- Session-based token management
- Compatible with EWELINK-1CH 10A smart relay

## Configuration

- `TOKEN_EXPIRATION`: Set to 60 minutes in `settings.py`
- `WEBHOOK_URL`: Configure in your `.env` file with the URL from your eWeLink account

## API Endpoints

- `/`: Home page
- `/generate/`: Generate or retrieve access token
- `/unlock/`: Unlock the door using an active token

## Models

The project uses a single model, `AccessToken`, defined in `door_access/models.py`:

```python
class AccessToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    session_key = models.CharField(max_length=40, default='legacy')
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return timezone.now() < self.expires_at and not self.is_used
```

This model stores access tokens with their creation time, expiration time, associated session key, and usage status.

## Dependencies

Key dependencies include:
- Django 5.0.7
- Requests library for webhook calls
- python-dotenv for environment variable management

For a full list of dependencies, refer to the `requirements.txt` file.

## Development

This project uses SQLite as the database for development. For production, consider using a more robust database system like PostgreSQL.

## .gitignore

Ensure that you don't commit sensitive information or unnecessary files to your repository.

## Security Notes

- Ensure `DEBUG` is set to `False` in production
- Keep your `DJANGO_SECRET_KEY` and `WEBHOOK_URL` secure
- Implement proper authentication and authorization for production use
- Consider implementing rate limiting to prevent abuse of token generation and door unlocking endpoints
- Regularly update your eWeLink account password and check for any suspicious activities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
