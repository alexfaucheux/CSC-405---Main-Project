from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
import pytz

tz = pytz.timezone('US/Central')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)  # Username is Email
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    images_liked = db.relationship('UserImage', back_populates='user', lazy='dynamic')
    images_disliked = db.relationship('DisUserImage', back_populates='user', lazy='dynamic')

    def like_image(self, image):
        if not self.has_liked_image(image):
            liked_image = UserImage(user_id=self.id, image_id=image.id)
            db.session.add(liked_image)

    def dislike_image(self, image):
        if not self.has_disliked_image(image):
            disliked_image = DisUserImage(user_id=self.id, image_id=image.id)
            db.session.add(disliked_image)

    def unlike_image(self, image):
        if self.has_liked_image(image):
            liked_image = UserImage.query.filter_by(
                user_id=self.id,
                image_id=image.id
            ).first()
            db.session.delete(liked_image)

        elif self.has_disliked_image(image):
            disliked_image = DisUserImage.query.filter_by(
                user_id=self.id,
                image_id=image.id
            ).first()
            db.session.delete(disliked_image)

    def has_liked_image(self, image):
        return UserImage.query.filter_by(
            user_id=self.id,
            image_id=image.id
        ).count() > 0

    def has_disliked_image(self, image):
        return DisUserImage.query.filter_by(
            user_id=self.id,
            image_id=image.id
        ).count() > 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(64), unique=True)
    image_url = db.Column(db.String, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.now(tz))
    likes = db.relationship('UserImage', back_populates='image', lazy='dynamic')
    dislikes = db.relationship('DisUserImage', back_populates='image', lazy='dynamic')

    def __repr__(self):
        return '<Image {}>'.format(self.image_name)


class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True)
    user = db.relationship("User", back_populates="images_liked")
    image = db.relationship("Image", back_populates="likes")


class DisUserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True)
    user = db.relationship("User", back_populates="images_disliked")
    image = db.relationship("Image", back_populates="dislikes")


class ObjectOfInterest(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)  # id ranges are reserved for specific types of OOI. 0-4 = Visible ISS Passes
    type = db.Column(db.String)
    date_stored = db.Column(db.DateTime, index=True, default=datetime.now(tz))
    vis_start = db.Column(db.DateTime, index=True, default=datetime.now(tz))
    vis_end = db.Column(db.DateTime, index=True, default=datetime.now(tz))


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_stored = db.Column(db.DateTime, index=True, default=datetime.now(tz))
    sunset = db.Column(db.DateTime)
    sunrise = db.Column(db.DateTime)
    high = db.Column(db.FLOAT)
    low = db.Column(db.FLOAT)
    m_phase = db.Column(db.String)
    clouds = db.Column(db.FLOAT)
    wind = db.Column(db.FLOAT)
    wind_dir = db.Column(db.FLOAT)
    vis = db.Column(db.FLOAT)
    current = db.Column(db.String)

    def __repr__(self):
        return '<id {}, Date {}>'.format(self.id, self.date_stored)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
