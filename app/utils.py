from flask import url_for, current_app
from flask_mail import Message as MailMessage
from app import mail
from .models import Profile
from .common import datetimefilter, utility_functions
import random
import string
from flask import current_app as app
import logging

def generate_verification_code(length=6):
    """Generate a random string of letters and digits """
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_password_reset_email(user, token):
    sender = app.config['ADMINS'][0]
    msg = MailMessage('Reset Your Password', sender=sender, recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_password', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

def send_ride_driver_email(driver, passenger, ride, ride_request):
    driver_profile = Profile.query.get(driver.user_id)
    passenger_profile = Profile.query.get(passenger.user_id)
    sender = app.config['ADMINS'][0]
    confirm_url = url_for('confirm_ride', ride_id=ride.ride_id, passenger_id=passenger.user_id, _external=True)
    requests_url = url_for('pending_requests_page', _external=True)
    vehicle_type_line = f"Vehicle Type: {ride.vehicle_type.capitalize()}\n" if ride.vehicle_type else ''
    commute_days_line = f"Commute Days: {utility_functions()['get_full_day_names'](ride_request.commute_days)}\n" if ride.ridetype.lower() == 'commute' else ''
    msg = MailMessage(f'New Ride Request to {ride.destination} with {passenger_profile.first_name}', sender=sender, recipients=[driver.email])
    custom_message_line = f"Custom Message: {ride_request.custom_message}\n" if ride_request.custom_message else ''
    msg.body = f'''Hello {driver_profile.first_name},

{passenger_profile.first_name} has requested to join your ride from {ride.departingFrom} to {ride.destination} on {datetimefilter(ride.ride_timestamp)}.
Ride Type: {ride.ridetype.capitalize()}
{vehicle_type_line}Occupants: {ride.occupants}
{commute_days_line}Accessibility: {utility_functions()['get_full_accessibility_names'](ride_request.accessibility)}
{custom_message_line}'''
    mail.send(msg)

def send_ride_passenger_email(passenger, ride, ride_request):
    passenger_profile = Profile.query.get(passenger.user_id)
    ride_user_profile = Profile.query.get(ride.user.user_id)
    sender = app.config['ADMINS'][0]
    vehicle_type_line = f"Vehicle Type: {ride.vehicle_type.capitalize()}\n" if ride.vehicle_type else ''
    commute_days_line = f"Commute Days: {utility_functions()['get_full_day_names'](ride_request.commute_days)}\n" if ride.ridetype.lower() == 'commute' else ''
    msg = MailMessage(f'Ride Request Sent to {ride.destination} with {ride_user_profile.first_name}', sender=sender, recipients=[passenger.email])
    msg.body = f'''Hello {passenger_profile.first_name},

Your request to join the ride from {ride.departingFrom} to {ride.destination} on {datetimefilter(ride.ride_timestamp)} has been sent.
Ride Type: {ride.ridetype.capitalize()}
{vehicle_type_line}Occupants: {ride.occupants}
{commute_days_line}Accessibility: {utility_functions()['get_full_accessibility_names'](ride_request.accessibility)}

You will receive an email once your request is confirmed.
'''
    mail.send(msg)

def send_ride_confirmation_email(user, ride, ride_request):
    user_profile = Profile.query.get(user.user_id)
    ride_user_profile = Profile.query.get(ride.user.user_id)
    sender = app.config['ADMINS'][0]
    vehicle_type_line = f"Vehicle Type: {ride.vehicle_type.capitalize()}\n" if ride.vehicle_type else ''
    commute_days_line = f"Commute Days: {utility_functions()['get_full_day_names'](ride_request.commute_days)}\n" if ride.ridetype.lower() == 'commute' else ''
    msg = MailMessage(f'Ride Confirmation to {ride.destination} with {ride_user_profile.first_name}', sender=sender, recipients=[user.email])
    msg.body = f'''Hello {user_profile.first_name},

The ride from {ride.departingFrom} to {ride.destination} on {datetimefilter(ride.ride_timestamp)} has been confirmed.
Ride Type: {ride.ridetype.capitalize()}
{vehicle_type_line}Occupants: {ride.occupants}
{commute_days_line}Accessibility: {utility_functions()['get_full_accessibility_names'](ride_request.accessibility)}
'''
    mail.send(msg)

def send_new_message_email(sender, recipient, message_content):
    sender_profile = Profile.query.get(sender.user_id)
    recipient_profile = Profile.query.get(recipient.user_id)
    sender_email = app.config['ADMINS'][0]
    msg = MailMessage('New Message from ' + sender_profile.first_name, sender=sender_email, recipients=[recipient.email])
    msg.body = f'''Hello {recipient_profile.first_name},

You have received a new message from {sender_profile.first_name}.

Here is the message:

{message_content}

You can reply to this message by logging into your account.
'''
    mail.send(msg)

def send_ride_rejection_email(user, ride, rejection_reason):
    user_profile = Profile.query.get(user.user_id)
    sender = app.config['ADMINS'][0]
    msg = MailMessage('Ride Rejection', sender=sender, recipients=[user.email])
    msg.body = f'''Hello {user_profile.first_name},

Your request to join the ride from {ride.departingFrom} to {ride.destination} on {datetimefilter(ride.ride_timestamp)} has been rejected.
Reason: {rejection_reason}
'''
    mail.send(msg)