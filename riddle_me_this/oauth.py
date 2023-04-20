from flask_oauthlib.client import OAuth
import dotenv
import os
import requests
from flask import current_app, session  # Import the existing Flask app instance

dotenv.load_dotenv()


def init_oauth():
    # Use current_app instead of app
    current_app.config['OAUTH_CREDENTIALS'] = {
        'google': {
            'id': os.getenv('CLIENT_ID'),
            'secret': os.getenv('CLIENT_SECRET')
        }
    }

    oauth = OAuth(current_app)
    google = oauth.remote_app(
        'google',
        consumer_key=current_app.config['OAUTH_CREDENTIALS']['google']['id'],
        consumer_secret=current_app.config['OAUTH_CREDENTIALS']['google']['secret'],
        request_token_params={'scope': ('https://www.googleapis.com/auth/userinfo.email '
                                        'https://www.googleapis.com/auth/userinfo.profile '
                                        'https://www.googleapis.com/auth/youtube '
                                        'https://www.googleapis.com/auth/youtube.force-ssl'),
                              'access_type': 'offline',
                              'prompt': 'consent'},
        base_url="https://www.googleapis.com/oauth2/v1/",
        request_token_url=None,
        access_token_method='POST',
        access_token_url="https://accounts.google.com/o/oauth2/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth"
    )
    return google


def refresh_access_token(refresh_token):
    payload = {
        'client_id': os.getenv('CLIENT_ID'),
        'client_secret': os.getenv('CLIENT_SECRET'),
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    response = requests.post('https://accounts.google.com/o/oauth2/token', data=payload)
    response_data = response.json()

    if response.status_code == 200:
        new_access_token = response_data.get('access_token')
        new_refresh_token = response_data.get('refresh_token', refresh_token)
        return new_access_token, new_refresh_token
    else:
        return None, None


def get_google_token(token=None):
    google_token = session.get('google_token')
    google_refresh_token = session.get('google_refresh_token')

    if google_token and google_refresh_token:
        access_token, refresh_token = refresh_access_token(google_refresh_token)
        if access_token and refresh_token:
            session['google_token'] = (access_token, '')
            session['google_refresh_token'] = refresh_token
            return access_token, ''
        else:
            session.pop('google_token', None)
            session.pop('google_refresh_token', None)
            return None, None
    else:
        return None, None
