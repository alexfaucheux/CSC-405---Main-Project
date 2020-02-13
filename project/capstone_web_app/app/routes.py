from flask import Flask, render_template
from app import app


@app.route("/")
def home():
    return render_template("Stargazer_website.html")


@app.route("/login")
def login():
    return render_template("Stargazer_login.html")


@app.route("/signup")
def signup():
    return render_template("Stargazer_signup.html")


@app.route("/images")
def images():
    return render_template("Stargazer_image_database.html")


@app.route("/live_feed")
def live_feed():
    return render_template("Stargazer_live_feed.html")


@app.route("/contact")
def contact():
    return render_template("Stargazer_contact_us.html")


if __name__ == "__main__":
    app.run(debug=True)
