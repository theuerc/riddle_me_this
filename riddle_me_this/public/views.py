# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
import logging

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from riddle_me_this.extensions import login_manager
from riddle_me_this.oauth import get_google_token, init_oauth
from riddle_me_this.public.forms import LoginForm
from riddle_me_this.user.models import User
from riddle_me_this.utils import flash_errors

google = None

blueprint = Blueprint("public", __name__, static_folder="../static")

logging.basicConfig(
    filename="record.log",
    level=logging.DEBUG,
    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",  # noqa: F541
)


@login_manager.user_loader
def load_user(user_id):
    """
    Load user by ID.

    This function is used by the login manager to retrieve a User object
    corresponding to a given user ID. It is called whenever Flask-Login needs
    to look up a User object for a specific user.

    Args:
    user_id (int): The ID of the user to be retrieved.

    Returns:
    User: A User object corresponding to the given user ID, or None if no
    such user exists.
    """
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """
    Home page.

    This function handles the rendering and processing of the home page. It
    displays the login form and handles user authentication. If a user is
    already logged in, they are redirected to the logged-in homepage.

    Returns:
    str: Rendered HTML template of the home page, or a redirect to the
    logged-in homepage if the user is already authenticated.
    """
    global google
    if not google:
        google = init_oauth()
        google.tokengetter(get_google_token)

    form = LoginForm(request.form)
    current_app.logger.info("Hello from the home page!")
    # Handle logging in
    if current_user.is_authenticated:
        return redirect(
            url_for("user.home_logged_in")
        )  # Redirect logged-in users to the new homepage

    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            redirect_url = url_for("user.home_logged_in")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    google_login_url = url_for("public.login_google")
    return render_template(
        "public/home.html", form=form, google_login_url=google_login_url
    )


@blueprint.route("/logout/")
@login_required
def logout():
    """
    Logout.

    This function logs out the currently authenticated user and displays a
    flash message indicating that they have been logged out. It then redirects
    the user to the home page.

    Returns:
    str: A redirect to the home page with a flash message.
    """
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/login/google")
def login_google():
    """
    Initiate Google login.

    This function initiates the OAuth2 flow for Google authentication. It
    redirects the user to the Google authorization page.

    Returns:
    str: A redirect to the Google authorization page.
    """
    return google.authorize(callback=url_for("public.authorized", _external=True))


@blueprint.route("/login/authorized")
def authorized():
    """
    Handle Google login authorization.

    This function processes the response from the Google OAuth2 flow. If the
    user grants access, their Google account information is used to log them in
    or create a new account in the application. If access is denied, an error
    message is displayed.

    Returns:
    str: A redirect to the logged-in homepage if access is granted, or an
    error message if access is denied.
    """
    resp = google.authorized_response()
    if resp is None:
        return "Access denied: reason=%s error=%s" % (
            request.args["error_reason"],
            request.args["error_description"],
        )
    # It would probably be better to store the tokens in the database
    # rather than in the session.
    session["google_token"] = (resp["access_token"], "")
    session["google_refresh_token"] = resp.get("refresh_token")
    me = google.get("userinfo")

    # Check if the user exists, create one if not
    user = User.query.filter_by(email=me.data["email"]).first()
    if not user:
        user = User.create(
            username=me.data["name"], email=me.data["email"], active=True
        )
    else:
        # Update the user information
        user.username = me.data["name"]
        user.active = True
        user.save()

    # Log the user in
    login_user(user)
    flash("You are logged in.", "success")
    redirect_url = request.args.get("next") or url_for("user.home_logged_in")
    return redirect(redirect_url)


@blueprint.route("/about/")
def about():
    """
    About page.

    This function renders the about page, which contains information about the
    application and its purpose.

    Returns:
    str: Rendered HTML template of the about page.
    """
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)
