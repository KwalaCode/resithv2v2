from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class BookingForm(FlaskForm):
    opponent = SelectField('Opponent', validators=[DataRequired()])
    time_slot = SelectField('Time Slot', validators=[DataRequired()])
    submit = SubmitField('Book the Game')

class AdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    action = SelectField('Action', choices=[('add', 'Add'), ('remove', 'Remove')])
    submit = SubmitField('Submit')