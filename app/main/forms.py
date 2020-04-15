from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, optional
from app.models import User
from app.main.routes import current_user


class AccountForm(FlaskForm):
    new_username = StringField('New email: ', validators=[optional(), Email()])
    new_password = PasswordField('New password: ', validators=[optional()])
    confirm_password = PasswordField('Confirm new password: ', validators=[EqualTo('new_password')])
    current_password = PasswordField('Current password: ', validators=[DataRequired()])
    submit = SubmitField('Submit')

    # Used to see if username is unique
    def validate_new_username(self, new_username):
        user = User.query.filter_by(username=new_username.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    # Used to validate if new password is not current password
    def validate_new_password(self, new_password):
        if current_user.check_password(new_password.data):
            raise ValidationError('Cannot reuse old password.')

    # Used to validate if password entered is correct
    def validate_current_password(self, current_password):
        if not current_user.check_password(current_password.data):
            raise ValidationError('Incorrect password')


class ContactUsForm(FlaskForm):
    fname = StringField('First Name', validators=[DataRequired()])
    lname = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Email', validators=[DataRequired(), Email()])
    text = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')
