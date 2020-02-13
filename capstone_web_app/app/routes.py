from flask import render_template, redirect
from app import app
from app.forms import LoginForm, RegisterForm
from app.user_management.User import User


@app.route("/")
def home():
    return render_template("Stargazer_website.html", title='Home')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template("Stargazer_login.html", title='Login', form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template("Stargazer_signup.html", title='Signup', form=form)


@app.route("/images")
def images():
    return render_template("Stargazer_image_database.html", title='Images')


@app.route("/live_feed")
def live_feed():
    return render_template("Stargazer_live_feed.html", title='Live Feed')


@app.route("/contact")
def contact():
    return render_template("Stargazer_contact_us.html", title='Contact Us')


if __name__ == "__main__":
    app.run(debug=True)
