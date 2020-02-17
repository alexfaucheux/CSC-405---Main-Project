from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)  # Username is Email
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    images_liked = db.relationship('UserImage', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    users_liked = db.relationship('UserImage', lazy='dynamic')


class UserImage(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True, primary_key=True)


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_stored = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    sunset = db.Column(db.DateTime)
    sunrise = db.Column(db.DateTime)
    temp = db.Column(db.DECIMAL)
    m_phase = db.Column(db.DECIMAL)
    clouds = db.Column(db.DECIMAL)
    wind = db.Column(db.DECIMAL)
    wind_dir = db.Column(db.DECIMAL)
    vis = db.Column(db.DECIMAL)
    current = db.Column(db.String)

    def __repr__(self):
        return '<Date {}>'.format(self.date)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))
