from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, StringField, PasswordField, BooleanField, TextAreaField, SelectField, DateField, TimeField, FieldList, SelectMultipleField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email , Length, EqualTo, ValidationError, Optional
from app.models import User

class RequiredIf(DataRequired):
    """validator which makes a field required if another field is set and has a truthy value."""

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)

class VerificationForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify')
class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class PasswordResetForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
class SendEmail(FlaskForm):
    email = StringField('Recipient: ', validators=[DataRequired()])
    message = TextAreaField('Your message:', validators=[DataRequired()])
    submit = SubmitField('Send')
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
    announcement_title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    announcement_text = TextAreaField('Announcement', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RideForm(FlaskForm):
    ridetype = SelectField('Ride Type', choices=[
    ('', 'Select one'),
    ('commute', 'Commute'),
    ('errand', 'Errand'),
    ('leisure', 'Leisure'),
    ], validators=[DataRequired()])
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('', 'Select one'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('pickup', 'Pickup Truck'),
        ('minivan', 'Minivan')
    ])
    departingFrom = StringField('Departing from', render_kw={"placeholder": "Enter location"}, validators=[DataRequired()])
    departingAt = StringField('Departing At', validators=[Optional()], render_kw={"placeholder": "Enter time in format HH:MM AM/PM"})
    destination = StringField('Destination', render_kw={"placeholder": "Enter location"})
    arrival = StringField('Arrival', validators=[Optional()], render_kw={"placeholder": "Enter time in format HH:MM AM/PM"})
    duration = StringField('Duration', render_kw={"placeholder": "Enter time in minutes or hours"})
    stops = FieldList(StringField('Stop'), min_entries=0, render_kw={"placeholder": "Enter a stop"})
    reccuring = BooleanField('Recurring')
    recurring_days = SelectMultipleField('Recurring on days:', choices=[
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ])
    accessibility = SelectMultipleField('Accessibility', choices=[
        ('wheelchair', 'Wheelchair'),
        ('visual', 'Visual impairment'),
        ('hearing', 'Hearing impairment'),
        ('service_dog', 'Service dog friendly'),
        ('quiet', 'Quiet ride'),
        ('step_free', 'Step-free access'),
    ])
    description = TextAreaField('Description', render_kw={"placeholder": "Enter description"}) 
    submit = SubmitField('Post')                        

class SignUpForm(FlaskForm):

    role = SelectField('Role', choices=[
        ('driver', 'Driver'),
        ('passenger', 'Passenger'),
    ], validators=[DataRequired()])

    # Specific fields for commute ride
    commute_days = SelectMultipleField('Recurring days', choices=[
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ])

    accessibility = SelectMultipleField('Accessibility', choices=[
        ('wheelchair', 'Wheelchair'),
        ('visual', 'Visual impairment'),
        ('hearing', 'Hearing impairment'),
        ('service_dog', 'Service dog friendly'),
        ('quiet', 'Quiet ride'),
        ('step_free', 'Step-free access'),
    ])
    custom_message = TextAreaField('Message to poster', validators=[Length(max=500)], render_kw={"placeholder": " Custom dropoff location, etc."})
    
    # Specific field for errands ride
    requested_stops = FieldList(StringField('Requested stops'), min_entries=0)

    submit = SubmitField('Sign Up')

class SearchForm(FlaskForm):
    # Fields from the original SearchForm
    ridetype = SelectField('Ride Type', choices=[
        ('', 'Select one'),
        ('commute', 'Commute'),
        ('errand', 'Errand'),
        ('leisure', 'Leisure')
    ], validators=[Optional()])
    departingFrom = StringField('Departing from', validators=[Optional()])
    destination = StringField('Destination', validators=[Optional()])
    time_choice = SelectField('Time range', choices=[('Departing', 'Departing'), ('Arriving', 'Arriving')], validators=[Optional()])
    # specify range of times that the user can choose from
    time_start = SelectField('from', choices=[("12:00AM", "12:00AM")] + [(f"{i}:00AM", f"{i}:00AM") if i != 12 else ("12:00PM", "12:00PM") for i in range(1, 13)] + [(f"{i}:00PM", f"{i}:00PM") if i != 12 else ("12:00AM", "12:00AM") for i in range(1, 12)])
    time_end = SelectField('to', choices=[("12:00AM", "12:00AM")] + [(f"{i}:00AM", f"{i}:00AM") if i != 12 else ("12:00PM", "12:00PM") for i in range(1, 13)] + [(f"{i}:00PM", f"{i}:00PM") if i != 12 else ("12:00AM", "12:00AM") for i in range(1, 12)])

    # Fields from the FilterForm
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('', 'Select one'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('hatchback', 'Hatchback'),
        ('pickup', 'Pickup Truck'),
        ('minivan', 'Minivan')
    ], validators=[Optional()])
    duration = StringField('Duration', validators=[Optional()])
    stops = StringField('Stop', validators=[Optional()]) # changed from fieldlist to stringfield, also put in searchform
    reccuring = BooleanField('Recurring')
    is_offered = BooleanField('Offered only') # added is_offered
    is_requested = BooleanField('Requested only') # added is_requested
    recurring_days = SelectMultipleField('Recurring on days:', choices=[
        ('mon', 'Monday'),
        ('tue', 'Tuesday'),
        ('wed', 'Wednesday'),
        ('thu', 'Thursday'),
        ('fri', 'Friday'),
        ('sat', 'Saturday'),
        ('sun', 'Sunday'),
    ], validators=[Optional()])
    accessibility = SelectMultipleField('Accessibility', choices=[
        ('wheelchair', 'Wheelchair'),
        ('visual', 'Visual impairment'),
        ('hearing', 'Hearing impairment'),
        ('service_dog', 'Service dog friendly'),
        ('quiet', 'Quiet ride'),
        ('step_free', 'Step-free access'),
    ], validators=[Optional()])

    submit = SubmitField('Search')

class ReportForm(FlaskForm):
    report_text = TextAreaField('Write your report', validators=[DataRequired()])
    submit = SubmitField('Report')

def validate(self):
    # original validate fn
    initial_validation = super(RideForm, self).validate()

    # if initial validation fails, don't bother
    if not initial_validation:
        return False

    # check if vehicle_type is required and not filled out
    if self.is_offer_route and not self.vehicle_type.data:
        self.vehicle_type.errors.append("Vehicle type is required when offering a ride")
        return False

    # validate according to ride type
    if self.ridetype.data == 'commute':
        if not self.departingFrom.data or not self.destination.data or not self.arrival.data:
            self.errors.append("All fields for commute ride type must be filled out")
            return False
    elif self.ridetype.data == 'errand':
        if not self.departingFrom.data or not self.departingAt.data or not self.stops.data:
            self.errors.append("All fields for errand ride type must be filled out")
            return False
    elif self.ridetype.data == 'leisure':
        if not self.departingFrom.data or not self.departingAt.data or not self.destination.data or not self.arrival.data or not self.duration.data:
            self.errors.append("All fields for leisure ride type must be filled out")
            return False

    # all validations passed
    return True