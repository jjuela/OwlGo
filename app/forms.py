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
    location = StringField('', reder_kw={"placeholder": "Location"})
    destination = StringField('', render_kw={"placeholder": "Destination"})
    departing = StringField('', render_kw={"placeholder": "Departing"})
    arrival = StringField('', render_kw={"placeholder": "Arrival"})
    duration = StringField('', render_kw={"placeholder": "Duration"})
    pickup = StringField('', render_kw={"placeholder": "Pick up"})
    stops = StringField('', render_kw={"placeholder": "Stops"})
    reccuring = BooleanField('Recurring')
    accessibility = StringField('', render_kw={"placeholder": "Accessibility"})
    description = TextAreaField('', render_kw={"placeholder": "Description"}) 
    submit = SubmitField('Post')                        
