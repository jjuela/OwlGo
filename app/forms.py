from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, StringField, PasswordField, BooleanField, TextAreaField, SelectField, DateField, TimeField, FieldList, SelectMultipleField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email , Length, EqualTo, ValidationError, RequiredIf
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
    ], validators=[RequiredIf('is_offered')])
    departingFrom = StringField('Departing from', render_kw={"placeholder": "Enter location"}, validators=[DataRequired()])
    departingAt = TimeField('Departing at', render_kw={"placeholder": "Enter time"}, validators=[DataRequired()])
    destination = StringField('Destination', render_kw={"placeholder": "Enter location"}, validators=[DataRequired()])
    arrival = TimeField('Arrival', render_kw={"placeholder": "Arrival"})
    duration = StringField('Duration', render_kw={"placeholder": "Enter time"})
    stops = FieldList(StringField('Stop'), min_entries=1)
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
        # maybe add more?
    ])
    description = TextAreaField('Description', render_kw={"placeholder": "Enter description"}) 
    submit = SubmitField('Post')                        
    # add start_date, end_date maybe?

    def __init__(self, is_offered, *args, **kwargs):
        super(RideForm, self).__init__(*args, **kwargs)
        self.is_offered = is_offered