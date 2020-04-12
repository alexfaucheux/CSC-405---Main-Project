from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegisterForm, ContactUsForm, AccountForm
from app.models import User, Image, Weather
from app.camera_opencv import Camera
from app.email_server import Email
from datetime import datetime, timedelta
from API_Readers import darkskyrequest

# Names and links used for different pages in website
links = {'about': 'About', 'home': 'Weather', 'images': 'Images', 'live_feed': 'Live Feed', 'contact': 'Contact Us',
         'login': 'Login', 'profile': 'Profile', 'account': 'Account Settings', 'logout': 'Logout'}

''' ENDPOINT FOR HOME PAGE '''


@app.route("/")
@app.route("/<up>")
def home(up=None):
    #Each id corresponds to a different time. 1 = current, 2= tonight, 3= tomorrow night, 4 = day after that night, etc.
    currentCon = Weather.query.filter_by(id=1).first()
    nightCon = Weather.query.filter_by(id=2).first()
    weather2 = Weather.query.filter_by(id=3).first()
    weather3 = Weather.query.filter_by(id=4).first()
    weather4 = Weather.query.filter_by(id=5).first()
    weather5 = Weather.query.filter_by(id=6).first()
    weather6 = Weather.query.filter_by(id=7).first()


    # If weather not not updated yet, attempt to update it
    if up is None:
        return redirect(url_for("update"))

    # Display home page
    return render_template("Stargazer_website.html", title='Weather', links=links, weather=currentCon, weatherN=nightCon,
                           weather2=weather2, weather3=weather3, weather4=weather4, weather5=weather5, weather6=weather6)


@app.route("/about")
def about():
    return render_template("about.html", title="About", links=links)


''' ENDPOINT FOR UPDATING WEATHER '''


@app.route("/update-weather/")
def update():
    date_stored = Weather.query.filter_by(id=0).first().date_stored
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
    return render_template("Stargazer_login.html", title="Login", links=links, form=form)


''' ENDPOINT FOR LOGGING OUT '''


@app.route('/logout')
@login_required
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


''' ENDPOINT FOR ACCOUNT PAGE '''


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()

    if form.validate_on_submit():
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        if form.new_username.data:
            current_user.username = form.new_username.data
        db.session.commit()
        return redirect(url_for("home"))

    # Displays profile page
    return render_template("account.html", title="Account Settings", links=links, form=form)


''' END POINT FOR PROFILE PAGE '''


@app.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user, links=links)


''' ENDPOINT FOR IMAGE GALLERY PAGE '''


@app.route("/images")
def images():
    # query all images from database
    imgs = Image.query.all()
    len_of_imgs = len(imgs)

    # displays image gallery page
    return render_template("Stargazer_image_database.html", title='Images', links=links, images=imgs,
                           num_imgs=len_of_imgs)


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


def check_current_password(password):
    return current_user.check_password(password)


# Testing code
if __name__ == "__main__":
    print(User)
    # app.run(debug=True)
