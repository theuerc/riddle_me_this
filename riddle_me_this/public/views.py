# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    session
)
from flask_login import login_required, login_user, logout_user, current_user
from riddle_me_this.extensions import login_manager
from riddle_me_this.public.forms import LoginForm
from riddle_me_this.user.forms import RegisterForm
from riddle_me_this.user.models import User
from riddle_me_this.utils import flash_errors
import logging
from flask import current_app
from riddle_me_this.oauth import init_oauth, get_google_token

google = None

blueprint = Blueprint("public", __name__, static_folder="../static")

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route("/", methods=["GET", "POST"])
def home():
    """Home page."""
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
            redirect_url = request.args.get("next") or url_for("user.members")
            return redirect(redirect_url)
        else:
            flash_errors(form)
    google_login_url = url_for('public.login_google')  # Add this line
    return render_template("public/home.html", form=form, google_login_url=google_login_url)


@blueprint.route("/logout/")
@login_required
def logout():
    """Logout."""
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.home"))


@blueprint.route("/register/", methods=["GET", "POST"])
def register():
    """Register new user."""

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        User.create(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        flash("Thank you for registering. You can now log in.", "success")
        return redirect(url_for("public.home"))
    else:
        flash_errors(form)
    return render_template("public/register.html", form=form)


@blueprint.route('/login/google')
def login_google():
    return google.authorize(callback=url_for('public.authorized', _external=True))


@blueprint.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    session['google_refresh_token'] = resp.get('refresh_token')  # Save the refresh token
    me = google.get('userinfo')

    # Check if the user exists, create one if not
    user = User.query.filter_by(email=me.data['email']).first()
    if not user:
        user = User.create(
            username=me.data['name'],
            email=me.data['email'],
            active=True
        )
    else:
        # Update the user information
        user.username = me.data['name']
        user.active = True
        user.save()

    # Log the user in
    login_user(user)
    flash("You are logged in.", "success")
    redirect_url = request.args.get("next") or url_for("user.members")
    return redirect(redirect_url)


@blueprint.route("/about/")
def about():
    """About page."""
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)

