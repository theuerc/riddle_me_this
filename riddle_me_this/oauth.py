"""OAuth 2.0 authentication for Google."""
import os

import dotenv
import requests
from flask import current_app, session
from flask_oauthlib.client import OAuth

dotenv.load_dotenv()


def init_oauth():
    """
    Initializes the OAuth 2.0 authentication process for Google.

    This function sets the necessary credentials
    for the authentication process and returns an OAuth object for further use.

    Returns:
    OAuth object -- an object representing the Google OAuth 2.0 authentication process.
    """
    # Use current_app instead of app
    current_app.config["OAUTH_CREDENTIALS"] = {
        "google": {"id": os.getenv("CLIENT_ID"), "secret": os.getenv("CLIENT_SECRET")}
    }

    oauth = OAuth(current_app)
    google = oauth.remote_app(
        "google",
        consumer_key=current_app.config["OAUTH_CREDENTIALS"]["google"]["id"],
        consumer_secret=current_app.config["OAUTH_CREDENTIALS"]["google"]["secret"],
        request_token_params={
            "scope": (
                "https://www.googleapis.com/auth/userinfo.email "
                "https://www.googleapis.com/auth/userinfo.profile "
                "https://www.googleapis.com/auth/youtube "
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ),
            "access_type": "offline",
            "prompt": "consent",
        },
        base_url="https://www.googleapis.com/oauth2/v1/",
        request_token_url=None,
        access_token_method="POST",
        access_token_url="https://accounts.google.com/o/oauth2/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
    )
    return google


def refresh_access_token(refresh_token):
    """
    Refreshes the access token for Google OAuth 2.0 authentication.

    This function sends a POST request to
    the Google OAuth 2.0 token endpoint with the necessary
    parameters to refresh the access token.

    Args:
    refresh_token -- str -- the refresh token used to obtain a new access token.

    Returns:
    tuple -- a tuple of two strings representing the new
    access token and the new refresh token.
    """
    payload = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post("https://accounts.google.com/o/oauth2/token", data=payload)
    response_data = response.json()

    if response.status_code == 200:
        new_access_token = response_data.get("access_token")
        new_refresh_token = response_data.get("refresh_token", refresh_token)
        return new_access_token, new_refresh_token
    else:
        return None, None


def get_google_token(token=None):
    """
    Retrieves the Google access token from the current session.

    If the token has expired, this function attempts
    to refresh it with the refresh token. If the refresh token is also invalid,
    both tokens are removed from the
    session and None is returned.

    Args:
    token -- str (default None) -- a token to be used in place of the one in the session.
    This is used when the token has just been refreshed and the
    new token needs to be stored in the session.

    Returns:
    tuple -- a tuple of two strings representing the current
    access token and an empty string.
    """
    google_token = session.get("google_token")
    google_refresh_token = session.get("google_refresh_token")

    if google_token and google_refresh_token:
        access_token, refresh_token = refresh_access_token(google_refresh_token)
        if access_token and refresh_token:
            session["google_token"] = (access_token, "")
            session["google_refresh_token"] = refresh_token
            return access_token, ""
        else:
            session.pop("google_token", None)
            session.pop("google_refresh_token", None)
            return None, None
    else:
        return None, None
