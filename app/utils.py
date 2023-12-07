from flask import url_for, current_app
from flask_mail import Message as MailMessage
from app import mail
import random
import string
from flask import current_app as app

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