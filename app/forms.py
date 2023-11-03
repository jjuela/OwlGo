from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, StringField, PasswordField
from wtforms.validators import DataRequired, Email , Length, EqualTo, ValidationError
from app.models import User
class LoginForm(FlaskForm):
     email = StringField('Email', validators=[DataRequired(), Email()])
     password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
     submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
     email = StringField('Email', validators=[DataRequired(), Email()])
     password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
     submit = SubmitField('Create Account')
     def validate_email(self, email):
         user = User.query.filter_by(email=email.data).first()
         if user:
             raise ValidationError('An account with that email already exists. Please log in or use a different email.')
         elif not email.data.endswith('@southernct.edu'):
             raise ValidationError('Please use a valid SCSU email address.')                            
