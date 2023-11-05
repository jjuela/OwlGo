from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, StringField, PasswordField, BooleanField, TextAreaField, SelectField, DateField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email , Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
     email = StringField('', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
     password = PasswordField('', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "Password"})
     submit = SubmitField('Log in')
     
class RegistrationForm(FlaskForm):
     email = StringField('', validators=[DataRequired(), Email()], render_kw={"placeholder": "Email"})
     password = PasswordField('', validators=[DataRequired(), Length(min=8)], render_kw={"placeholder": "Password"})
     confirm_password = PasswordField('', validators=[DataRequired(), EqualTo('password')], render_kw={"placeholder": "Confirm Password"})
     submit = SubmitField('Next')
     def validate_email(self, email):
         user = User.query.filter_by(email=email.data).first()
         if user:
             raise ValidationError('An account with that email already exists. Please log in or use a different email.')
         elif not email.data.endswith('@southernct.edu'):
             raise ValidationError('Please use a valid SCSU email address.')          

class ProfileForm(FlaskForm):
    firstname = StringField('', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "First name"})
    lastname = StringField('', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Last name"})
    hometown = StringField('', validators=[DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Hometown"})
    image = FileField('Profile picture', validators=[FileAllowed(['jpg', 'png'])])
    about = TextAreaField('', validators=[DataRequired()], render_kw={"placeholder": "About me"})
    submit = SubmitField('Create')

class AnnouncementForm(FlaskForm):
    announcetext = TextAreaField('Announcement', validators=[DataRequired()])
    announcedate = DateField('Date', validators=[DataRequired()])

class RideForm(FlaskForm):
    ridetype = SelectField('Ride Type', choices=[('1', 'Leisure'), ('2', 'Commute'), ('3', 'Errand')])
    location = StringField('Location')
    destination = StringField('Destination')
    arrival = StringField('Arrival')
    duration = StringField('Duration')
    pickup = StringField('Pickup')
    stops = StringField('Stops')
    reccuring = BooleanField('Reccuring')
    accessibility = StringField('Accessibility')
    description = StringField('Description')
    submit = SubmitField('Submit')                        
