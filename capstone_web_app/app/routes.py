from flask import render_template, redirect, url_for, flash
from app import app
from app.forms import LoginForm, RegisterForm
from app.user_management.User import User

links = ["home", "images", "live_feed", "contact", "login"]
button_names = ["Home", "Images", "Live Feed", "Contact Us", "Login"]


@app.route("/")
def home():
    return render_template("Stargazer_website.html", title='Home', buttons=zip(links, button_names))


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    links_copy, names_copy = links.copy(), button_names.copy()
    links_copy.pop(4)
    names_copy.pop(4)
    if form.validate_on_submit():
        return redirect(url_for(home))
    return render_template("Stargazer_login.html", title='Login', buttons=zip(links_copy, names_copy), form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        return redirect(url_for(home))
    return render_template("Stargazer_signup.html", title='Signup', buttons=zip(links, button_names), form=form)


@app.route("/images")
def images():
    return render_template("Stargazer_image_database.html", title='Images', buttons=zip(links, button_names))


@app.route("/live_feed")
def live_feed():
    return render_template("Stargazer_live_feed.html", title='Live Feed', buttons=zip(links, button_names))


@app.route("/contact")
def contact():
    return render_template("Stargazer_contact_us.html", title='Contact Us', buttons=zip(links, button_names))


if __name__ == "__main__":
    app.run(debug=True)
