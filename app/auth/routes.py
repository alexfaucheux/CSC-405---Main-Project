from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegisterForm
from app.models import User

''' ENDPOINT FOR LOGIN PAGE '''

html_files = {
    "/images": "Stargazer_image_database.html",
    "/live_feed": "Stargazer_live_feed.html",
    "/contact": "Stargazer_contact_us.html",
    "/about": "about.html",
    "/weather": "Stargazer_weather.html",

}


def get_html_file(url):
    html_file = ""
    for route in html_files:
        if route in url:
            html_file = html_files[route]

    return html_file


@bp.route("/login", methods=['GET', 'POST'])
def login():
    html_file = get_html_file(request.referrer)

    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    # If user fills form and clicks submit
    # Attempts to log user in
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.home'))

    # Displays login page
    return render_template("auth/login_popup.html", title="Login", form=form, prev_temp=html_file)


''' ENDPOINT FOR LOGGING OUT '''


@bp.route('/logout')
@login_required
def logout():
    logout_user()

    # Go to home page
    return redirect(url_for("main.home"))


''' ENDPOINT FOR SIGNUP PAGE'''


@bp.route("/signup", methods=['GET', 'POST'])
def signup():
    html_file = get_html_file(request.referrer)

    # Form used to register user.
    form = RegisterForm()

    # When form is submitted with all fields correctly filled
    # NOTE: username verification uses a method inside the class RegisterForm in forms.py
    if form.validate_on_submit():
        # Create new user entry
        user = User(username=form.username.data, fname=form.fname.data, lname=form.lname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        # Does not automatically login user
        # User is redirected to login page to officially login
        return redirect(url_for('auth.login'))

    # Display signup page
    return render_template("auth/signup_popup.html", title='Create Account', form=form, prev_temp=html_file)
