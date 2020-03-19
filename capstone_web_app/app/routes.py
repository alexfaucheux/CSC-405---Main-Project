from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegisterForm, ContactUsForm
from app.models import User, Image, Weather
from app.camera_opencv import Camera
from app.email_server import Email
from datetime import datetime, timedelta
from API_Readers import darkskyrequest


links = {'home': 'Home', 'images': 'Images', 'live_feed': 'Live Feed', 'contact': 'Contact Us', 'profile': 'Profile', \
         'login': 'Login', 'logout': 'Logout'}


@app.route("/")
@app.route("/<up>")
def home(up=None):
    weather1 = Weather.query.get(1)
    if up is None:
        return redirect(url_for("update"))
    return render_template("Stargazer_website.html", title='Home', links=links, weather=weather1)


@app.route("/update-weather/")
def update():
    date_stored = Weather.query.get(1).date_stored
    date = datetime.now()

    if (20 > date.hour > 7 and date >= date_stored + timedelta(hours=1)) or \
            ((date.hour >= 20 or date.hour <= 7) and date >= date_stored + timedelta(minutes=20)):
        darkskyrequest.parseRequest()

    return redirect(url_for("home", up="index"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    # If user fills form and clicks submit
    # Attempts to log user in
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))

    return render_template("Stargazer_login.html", title='Sign In', links=links, form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, fname=form.fname.data, lname=form.lname.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template("Stargazer_signup.html", title='Create Account', links=links, form=form)


@app.route("/images")
def images():
    imgs = Image.query.all()
    return render_template("Stargazer_image_database.html", title='Images', links=links, images=imgs)


@app.route("/like/<int:image_id>/<action>")
@login_required
def like_action(image_id, action):
    image = Image.query.filter_by(id=image_id).first()
    if action == "like":
        current_user.like_image(image)
        db.session.commit()

    elif action == "dislike":
        current_user.dislike_image(image)
        db.session.commit()

    return redirect(request.referrer)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route("/live_feed")
def live_feed():
    return render_template("Stargazer_live_feed.html", title='Live Feed', links=links)


@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactUsForm()

    if form.validate_on_submit():
        first_name = form.fname.data
        last_name = form.lname.data
        email = form.username.data
        text = form.text.data

        user_email = Email(first_name + " " + last_name, email)
        user_email.send_customer_email(text)

        flash("Successfully sent!")  # Displays on bottom of home page
        return redirect(url_for("home"))
    return render_template("Stargazer_contact_us.html", title='Contact Us', links=links, form=form)


@app.route("/profile")
def profile():
    return render_template("Profile.html", title="Profile", links=links)


if __name__ == "__main__":
    app.run(debug=True)
