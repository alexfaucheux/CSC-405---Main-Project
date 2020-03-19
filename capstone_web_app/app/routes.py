from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegisterForm, ContactUsForm
from app.models import User, Image, Weather
from app.camera_opencv import Camera
from app.email_server import Email
from datetime import datetime, timedelta
from API_Readers import darkskyrequest

# Names and links used for different pages in website
links = {'home': 'Home', 'images': 'Images', 'live_feed': 'Live Feed', 'contact': 'Contact Us', 'profile': 'Profile', \
         'login': 'Login', 'logout': 'Logout'}

''' ENDPOINT FOR HOME PAGE '''


@app.route("/")
@app.route("/<up>")
def home(up=None):
    weather1 = Weather.query.get(1)

    # If weather not not updated yet, attempt to update it
    if up is None:
        return redirect(url_for("update"))

    # Display home page
    return render_template("Stargazer_website.html", title='Home', links=links, weather=weather1)


''' ENDPOINT FOR UPDATING WEATHER '''


@app.route("/update-weather/")
def update():
    date_stored = Weather.query.get(1).date_stored
    date = datetime.now()

    # Only allowed to update within a time frame
    if (20 > date.hour > 7 and date >= date_stored + timedelta(hours=1)) or \
            ((date.hour >= 20 or date.hour <= 7) and date >= date_stored + timedelta(minutes=20)):
        darkskyrequest.parseRequest()

    # Redirects to home page
    return redirect(url_for("home", up="index"))


''' ENDPOINT FOR LOGIN PAGE '''


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

    # Displays login page
    return render_template("Stargazer_login.html", title='Sign In', links=links, form=form)


''' ENDPOINT FOR LOGGING OUT '''


@app.route('/logout')
def logout():
    logout_user()

    # Go to home page
    return redirect(url_for("home"))


''' ENDPOINT FOR SIGNUP PAGE'''


@app.route("/signup", methods=['GET', 'POST'])
def signup():
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
        return redirect(url_for('login'))

    # Display signup page
    return render_template("Stargazer_signup.html", title='Create Account', links=links, form=form)


''' ENDPOINT FOR IMAGE GALLERY PAGE '''


@app.route("/images")
def images():
    # query all images from database
    imgs = Image.query.all()

    # displays image gallery page
    return render_template("Stargazer_image_database.html", title='Images', links=links, images=imgs)


''' ENDPOINT FOR LIKING/DISLIKING AN IMAGE '''


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


# GENERATOR FUNCTION USED IN @video_feed
def gen(camera):
    # Continuously catch frames form camera and
    # return the frames as jpeg images
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


''' ENDPOINT FOR LIVE FEED PAGE '''
@app.route("/live_feed")
def live_feed():
    # Display Live Feed page
    return render_template("Stargazer_live_feed.html", title='Live Feed', links=links)


''' ENDPOINT FOR VIDEO FEED '''
@app.route("/video_feed")
def video_feed():
    # a continuous response from the generator function
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


''' ENDPOINT FOR CONTACT US PAGE '''
@app.route("/contact", methods=["GET", "POST"])
def contact():
    # Create contact form
    form = ContactUsForm()

    # When form is submitted with all fields correctly filled
    if form.validate_on_submit():
        # Extract info from form
        first_name = form.fname.data
        last_name = form.lname.data
        email = form.username.data
        text = form.text.data

        # Creates email server and sends the message from the form
        user_email = Email(first_name + " " + last_name, email)
        user_email.send_customer_email(text)

        flash("Successfully sent!")  # Displays on bottom of home page

        # Redirect to home page
        return redirect(url_for("home"))

    # Displays contact page
    return render_template("Stargazer_contact_us.html", title='Contact Us', links=links, form=form)


''' ENDPOINT FOR PROFILE PAGE '''
@app.route("/profile")
def profile():
    # Displays profile page
    return render_template("Profile.html", title="Profile", links=links)


# Testing code
if __name__ == "__main__":
    app.run(debug=True)
