# door_access/views.py

from django.shortcuts import render
from django.utils import timezone
from .models import AccessToken
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

import uuid
import logging
import requests

logger = logging.getLogger(__name__)


def home(request):
    token_data = get_active_token(request)
    context = {}
    if token_data:
        context['token'] = token_data['token']
        context['expires_at'] = token_data['expires_at']
    return render(request, 'door_access/home.html', context)



@require_http_methods(["GET", "POST"])
def generate_access(request):
    existing_token = get_active_token(request)
    if request.method == "POST":
        if existing_token:
            return JsonResponse({'error': 'Active token already exists'}, status=400)

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key or 'unknown'

        expiration = timezone.now() + settings.TOKEN_EXPIRATION
        token = AccessToken.objects.create(expires_at=expiration, session_key=session_key)
        token_data = {
            'token': str(token.token),
            'expires_at': expiration.isoformat()
        }
        request.session['token_data'] = token_data
        return JsonResponse(token_data)
    else:  # GET request
        if existing_token:
            return JsonResponse(existing_token)
        else:
            return JsonResponse({'error': 'No active token'}, status=404)

def unlock_door(request):
    token_data = get_active_token(request)
    if not token_data:
        return JsonResponse({'success': False, 'message': 'No active token'}, status=400)

    try:
        token = uuid.UUID(token_data['token'])
        access_token = AccessToken.objects.get(token=token)

        # Call the webhook
        try:
            response = requests.get(settings.WEBHOOK_URL, timeout=10)
            response.raise_for_status()

            if response.status_code == 200:
                # Instead of deleting the token, mark it as used
                access_token.is_used = True
                access_token.save()
                return JsonResponse({'success': True, 'message': 'Door unlocked successfully!'})
            else:
                logger.error(f"Webhook returned unexpected status code: {response.status_code}")
                return JsonResponse(
                    {'success': False, 'message': f'Unexpected response from door system: {response.status_code}'},
                    status=500)

        except requests.RequestException as e:
            logger.error(f"Error calling webhook: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Error communicating with door system: {str(e)}'},
                                status=500)
    except (ValueError, AccessToken.DoesNotExist):
        if 'token_data' in request.session:
            del request.session['token_data']
        return JsonResponse({'success': False, 'message': 'Invalid token'}, status=400)

def get_active_token(request):
    token_data = request.session.get('token_data')
    if token_data:
        now = timezone.now()
        expires_at = timezone.datetime.fromisoformat(token_data['expires_at'])
        if now < expires_at:
            return token_data
        else:
            # Token has expired, remove it from the session
            del request.session['token_data']

    # If no valid token in session, check the database
    session_key = request.session.session_key
    if session_key:
        active_token = AccessToken.objects.filter(session_key=session_key, expires_at__gt=timezone.now()).first()
        if active_token:
            token_data = {
                'token': str(active_token.token),
                'expires_at': active_token.expires_at.isoformat()
            }
            request.session['token_data'] = token_data
            return token_data

    return None