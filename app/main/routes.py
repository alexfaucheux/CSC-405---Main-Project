from flask import render_template, redirect, url_for, flash, request, Response
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.main import bp
from app.main.forms import ContactUsForm, AccountForm
from app.models import User, Image, Weather, ObjectOfInterest
from app.camera_opencv import Camera
from app.email_server import Email
from datetime import datetime, timedelta
from app.API_Readers import darkskyrequest, OOIreader
import calendar

weatherlinks = {"1": "Today", "2": "Tomorrow"}

today = datetime.now()

for i in range(3, 8):
    day = today + timedelta(days=i-1)
    weatherlinks[str(i)] = calendar.day_name[day.weekday()]

''' ENDPOINT FOR HOME PAGE '''


@bp.route("/")
@bp.route("/<up>")
def home(up=None):
    # If weather not not updated yet, attempt to update it
    if up is None:
        return redirect(url_for("main.update"))
    return redirect(url_for("main.weather", day=1))


@bp.route("/weather/day/<day>")
def weather(day):
    currentCon = Weather.query.get(int(day))

    #In addition to updating the weather, update the OOI Table
    OOIreader.parseISS()
    object1 = ObjectOfInterest.query.get(0)
    object2 = ObjectOfInterest.query.get(1)
    object3 = ObjectOfInterest.query.get(2)
    object4 = ObjectOfInterest.query.get(3)
    object5 = ObjectOfInterest.query.get(4)

    # Display home page
    return render_template("Stargazer_weather.html", currentday=day, title='Weather',
                           weatherlinks=weatherlinks, weather=currentCon, object1=object1, object2=object2, object3=object3, object4=object4, object5=object5)


@bp.route("/about")
def about():
    return render_template("about.html", title="About")


''' ENDPOINT FOR UPDATING WEATHER '''


@bp.route("/update-weather/")
def update():
    # Updates the weather data on the page for the current requested day
    weather = Weather.query.get(1)
    if weather is None:
        darkskyrequest.parseRequest()

    else:
        date_stored = weather.date_stored
        date = datetime.now()

        # Only allowed to update within a time frame
        if (20 > date.hour > 7 and date >= date_stored + timedelta(hours=1)) or \
                ((date.hour >= 20 or date.hour <= 7) and date >= date_stored + timedelta(minutes=20)):
            darkskyrequest.parseRequest()

    # Redirects to home page
    return redirect(url_for("main.home", up="success"))


''' ENDPOINT FOR IMAGE GALLERY PAGE '''


@bp.route("/images")
def images():
    # query all images from database
    imgs = Image.query.all()
    len_of_imgs = len(imgs)

    # displays image gallery page
    return render_template("Stargazer_image_database.html", title='Images', images=imgs,
                           num_imgs=len_of_imgs)


''' ENDPOINT FOR LIKING/DISLIKING AN IMAGE '''


@bp.route("/like/<int:image_id>/<action>")
@login_required
def like_action(image_id, action):
    image = Image.query.get(image_id)
    if action == "like":
        if current_user.has_liked_image(image):
            current_user.unlike_image(image)

        elif current_user.has_disliked_image(image):
            current_user.unlike_image(image)
            current_user.like_image(image)

        else:
            current_user.like_image(image)
        db.session.commit()

    elif action == "dislike":
        if current_user.has_disliked_image(image):
            current_user.unlike_image(image)
        elif current_user.has_liked_image(image):
            current_user.unlike_image(image)
            current_user.dislike_image(image)
        else:
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


@bp.route("/live_feed")
def live_feed():
    # Display Live Feed page
    return render_template("Stargazer_live_feed.html", title='Live Feed')


''' ENDPOINT FOR VIDEO FEED '''


@bp.route("/video_feed")
def video_feed():
    # a continuous response from the generator function
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


''' ENDPOINT FOR CONTACT US PAGE '''


@bp.route("/contact", methods=["GET", "POST"])
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
        return redirect(url_for("main.home"))

    # Displays contact page
    return render_template("Stargazer_contact_us.html", title='Contact Us', form=form)


def check_current_password(password):
    return current_user.check_password(password)

''' ENDPOINT FOR ACCOUNT PAGE '''


@bp.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()

    if form.validate_on_submit():
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
        if form.new_username.data:
            current_user.username = form.new_username.data
        db.session.commit()
        return redirect(url_for("main.home"))

    # Displays profile page
    return render_template("account.html", title="Account Settings", form=form)


''' END POINT FOR PROFILE PAGE '''


@bp.route("/profile/<username>")
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user)


# Testing code
if __name__ == "__main__":
    print(User)
    # app.run(debug=True)
