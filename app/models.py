from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
from hashlib import md5


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), index=True, unique=True)  # Username is Email
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))

    owned_images = db.relationship('Image', back_populates='owner')
    images_liked = db.relationship('UserImage', back_populates='user', lazy='dynamic')
    images_disliked = db.relationship('DisUserImage', back_populates='user', lazy='dynamic')
    comments = db.relationship('UserComments', back_populates='user', lazy='dynamic')
    comments_liked = db.relationship('LikeUserComment', back_populates='user', lazy='dynamic')
    comments_disliked = db.relationship('DislikeUserComment', back_populates='user', lazy='dynamic')

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

    # here comment is a string
    def add_comment(self, image, comments):
        comment = UserComments(
            user_id=self.id,
            image_id=image.id,
            comment=comments
        )
        db.session.add(comment)
        db.session.commit()

    def delete_comment(self, comment):
        comment = UserComments.query.filter_by(
            user_id=self.id,
            comment=comment.id
        ).first()

        print(comment)
        if comment is not None:
            db.session.delete(comment)
            db.session.commit()

    def has_liked_comment(self, comment):
        return LikeUserComment.query.filter_by(
            user_id=self.id,
            comment_id=comment.id
        ).count() > 0

    def has_disliked_comment(self, comment):
        return DislikeUserComment.query.filter_by(
            user_id=self.id,
            comment_id=comment.id
        ).count() > 0

    def like_comment(self, comment):
        if not self.has_liked_comment(comment):
            liked_comment = LikeUserComment(
                user_id=self.id,
                comment_id=comment.id
            )
            db.session.add(liked_comment)
            db.session.commit()

    def dislike_comment(self, comment):
        if not self.has_disliked_comment(comment):
            disliked_comment = DislikeUserComment(
                user_id=self.id,
                comment_id=comment.id
            )
            db.session.add(disliked_comment)
            db.session.commit()

    def unlike_comment(self, comment):
        if self.has_liked_comment(comment):
            liked_comment = LikeUserComment.query.filter_by(
                user_id=self.id,
                comment_id=comment.id
            ).first()
            db.session.delete(liked_comment)

        elif self.has_disliked_comment(comment):
            disliked_comment = DislikeUserComment.query.filter_by(
                user_id=self.id,
                comment_id=comment.id
            ).first()
            db.session.delete(disliked_comment)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_name = db.Column(db.String(64))
    image_url = db.Column(db.String, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    owner = db.relationship('User', back_populates='owned_images')
    likes = db.relationship('UserImage', back_populates='image', lazy='dynamic')
    dislikes = db.relationship('DisUserImage', back_populates='image', lazy='dynamic')
    comments = db.relationship('UserComments', back_populates='image', lazy='dynamic')

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


class UserComments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), index=True)

    user = db.relationship("User", back_populates="comments")
    image = db.relationship("Image", back_populates="comments")
    likes = db.relationship("LikeUserComment", back_populates="comment")
    dislikes = db.relationship("DislikeUserComment", back_populates="comment")


class LikeUserComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('user_comments.id'), index=True)

    user = db.relationship("User", back_populates="comments_liked")
    comment = db.relationship("UserComments", back_populates="likes")


class DislikeUserComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('user_comments.id'), index=True)

    user = db.relationship("User", back_populates="comments_disliked")
    comment = db.relationship("UserComments", back_populates="dislikes")


class ObjectOfInterest(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True)  # id ranges are reserved for specific types of OOI. 0-4 = Visible ISS Passes
    type = db.Column(db.String)
    date_stored = db.Column(db.DateTime, index=True, default=datetime.now)
    vis_start = db.Column(db.DateTime, index=True, default=datetime.now)
    vis_end = db.Column(db.DateTime, index=True, default=datetime.now)


class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_stored = db.Column(db.DateTime, index=True, default=datetime.now)
    sunset = db.Column(db.DateTime)
    sunrise = db.Column(db.DateTime)
    high = db.Column(db.Numeric(3, 2))
    low = db.Column(db.Numeric(3, 2))
    m_phase = db.Column(db.String)
    clouds = db.Column(db.Numeric(3, 2))
    wind = db.Column(db.Numeric(3, 2))
    wind_dir = db.Column(db.Numeric(3, 2))
    vis = db.Column(db.Numeric(3, 2))
    current = db.Column(db.String)

    def __repr__(self):
        return '<id {}, Date {}>'.format(self.id, self.date_stored)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
