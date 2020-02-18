from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegisterForm
from app.models import User, Image, Weather

links = {'home': 'Home', 'images': 'Images', 'live_feed': 'Live Feed', 'contact': 'Contact Us', \
         'login': 'Login', 'logout': 'Logout'}


@app.route("/")
def home():
    weather1 = Weather.query.filter_by(id=1).first()
    return render_template("Stargazer_website.html", title='Home', links=links, weather=weather1)



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

@app.route("/live_feed")
def live_feed():
    return render_template("Stargazer_live_feed.html", title='Live Feed', links=links)


@app.route("/contact")
def contact():
    return render_template("Stargazer_contact_us.html", title='Contact Us', links=links)


if __name__ == "__main__":
    app.run(debug=True)
