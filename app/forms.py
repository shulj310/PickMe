from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, TextField
from wtforms.validators import (DataRequired, Regexp, ValidationError,
                            Email, Length, EqualTo, URL)

from models import User

def name_exists(form,field):
    if User.select().where(User.email == field.data).exists():
        raise ValidationError('Email already exists.')

def email_exists(form,field):
    if User.select().where(User.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, "
                        "numbers and underscores only.")
            ),
            name_exists
        ])
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=7),
            EqualTo('password2', message='Passwords must match')
        ])
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired()])
    ''' Register as a Writer? Radio Button. If yes, direct user to RegisterFormWriter html doc'''
    # writer = StringField('Register as writer?',validators=[DataRequired()])

class AddWriter(FlaskForm):
    name = StringField(
        'Full Name (as it appears on Website)',
        validators=[DataRequired()])
    company = StringField(
        'Company',
        validators=[
            DataRequired()])
    bio = StringField(
        'bio',
        validators=[
        URL()])
    website = StringField(
        'Website to collect stream',
        validators=[DataRequired()]
    )


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
            DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])

class PostForm(FlaskForm):
    link = TextField('Link',validators=[URL()])
    side = TextField('Buy/Sell',validators=[DataRequired()])
    symbol = TextField('Ticker',validators=[DataRequired()])
    title = TextField('Article Title',validators=[DataRequired()])
