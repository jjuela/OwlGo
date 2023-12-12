# flask imports
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message as MailMessage, Mail
from flask_wtf import FlaskForm

# sqlalchemy imports
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError

# app imports
from app import app, db, mail
from app.models import User, Profile, Ride, RidePassenger, Message, Rating, Review, Announcement, RideRequest, RideReport, UserReport
from app.forms import RegistrationForm, LoginForm, ProfileForm, AnnouncementForm, RideForm, SignUpForm, SearchForm, VerificationForm, PasswordResetRequestForm, PasswordResetForm, ReportForm, ConfirmRideForm, MessageForm, RejectRideForm, TakeActionForm, ReviewForm, RatingForm
from app.utils import generate_verification_code, send_password_reset_email, send_ride_driver_email, send_ride_passenger_email, send_ride_confirmation_email, send_new_message_email, send_ride_rejection_email

# other imports
from datetime import datetime
from smtplib import SMTPException
from werkzeug.utils import secure_filename
from pytz import timezone, utc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from collections import defaultdict
import calendar
import time
import re
import os
import glob

@app.context_processor
def context_processor():
    if current_user.is_authenticated:
        # Fetch unconfirmed ride requests made to the current user's rides
        user_ride_ids = [ride.ride_id for ride in current_user.rides]
        ride_requests = RideRequest.query.filter(RideRequest.ride_id.in_(user_ride_ids), RideRequest.confirmed == False).all()

        # Fetch unread messages for the current user
        unread_messages = Message.query.filter_by(recipient_id=current_user.user_id, is_read=False).all()

        # Determine if there are any pending requests or unread messages
        has_pending_requests = len(ride_requests) > 0
        has_unread_messages = len(unread_messages) > 0
    else:
        has_pending_requests = False
        has_unread_messages = False

    return dict(has_pending_requests=has_pending_requests, has_unread_messages=has_unread_messages)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        # Check if the email domain is 'southernct.edu'
        if '@southernct.edu' not in email:
            flash('Sorry, only southern emails are allowed.')
            return render_template('reset_password_request.html', form=form)
        user = User.query.filter_by(email=email).first()
        # Check if the user exists
        if user:
            token = user.get_reset_password_token()
            send_password_reset_email(user, token)
            # Return the full URL with the token in the response along with instructions
            return f'<p>Copy this link and paste it in your browser to change your password:</p><p>104.198.140.100:8080/reset_password/{token}</p>'
        else:
            flash('No account with this email exists. Please click the sign up button to create an account.')
            return render_template('reset_password_request.html', form=form)
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('landing'))  # redirect to landing page if user is authenticated
    # Verify the token
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('landing'))  # redirect to landing page if token is invalid
    form = PasswordResetForm()
    if form.validate_on_submit():
        # Set the new password
        user.set_password(form.password.data)
        db.session.commit()
        session.pop('_flashes', None)  # clear all flash messages
        flash('Your password has been reset.')
        return redirect(url_for('landing'))  # redirect to landing page after resetting password
    return render_template('reset_password.html', form=form)

@app.route('/', methods=['GET', 'POST'])
def landing():
    logout_user()
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        if not register_form.email.data.endswith('@southernct.edu'):
            flash('Only southernct.edu emails are allowed.')
            return redirect(url_for('landing'))

        user = User.query.filter_by(email=login_form.email.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login failed')

    if register_form.validate_on_submit():
        existing_user = User.query.filter_by(email=register_form.email.data).first()
        if existing_user:
            flash('An account with this email already exists.')
            return redirect(url_for('landing'))

        user = User(email=register_form.email.data)
        user.set_password(register_form.password.data)

        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.is_verified = False

        try:
            db.session.add(user)
            db.session.commit()

            subject = "OwlGo Verification Code"
            recipient = user.email
            body = f"Your verification code is: {verification_code}"
            msg = Message(subject=subject, recipients=[recipient], body=body)
            
            try:
                mail.send(msg)
            except SMTPException:
                flash('Failed to send verification email. Please try again.')
                db.session.delete(user)
                db.session.commit()
                return redirect(url_for('landing'))

            msg = MailMessage(subject=subject, recipients=recipient, body=body)
            # ...
            flash('Please check your email for the verification code in order to create a profile.')
            return redirect(url_for('verify', user_id=user.user_id))

        except IntegrityError:
            db.session.rollback()
            flash('An error occurred. Please try again.')
            return redirect(url_for('landing'))

    return render_template('landing.html', login_form=login_form, register_form=register_form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/verify/<int:user_id>', methods=['GET', 'POST'])
def verify(user_id):
    user = User.query.get(user_id)

    if user.is_verified or not user.verification_code:
        flash('No verification needed or already verified.')
        return redirect(url_for('landing'))

    form = VerificationForm()
    if form.validate_on_submit():
        if user.verification_code == form.verification_code.data:
            user.is_verified = True
            user.verification_code = None  # Clear the verification code
            db.session.commit()
            login_user(user)  # Log in the user
            flash('Account verified please create profile.')
            return redirect(url_for('create_profile'))
        else:
            flash('Invalid verification code. Please try again.')

    return render_template('verify.html', form=form)

@app.route('/pending_requests_page', methods=['GET'])
@login_required
def pending_requests_page():
    # Fetch unconfirmed ride requests made to the current user's rides
    user_ride_ids = [ride.ride_id for ride in current_user.rides]
    ride_requests = RideRequest.query.filter(RideRequest.ride_id.in_(user_ride_ids), RideRequest.confirmed == False).order_by(RideRequest.timestamp).all()

    # Fetch unread messages for the current user
    unread_messages = Message.query.filter_by(recipient_id=current_user.user_id, is_read=False).all()

    # Set all unread messages to read
    for message in unread_messages:
        message.is_read = True
    db.session.commit()

    # Determine if there are any pending requests or unread messages
    has_pending_requests = len(ride_requests) > 0
    has_unread_messages = len(unread_messages) > 0

    return render_template('pending_requests.html', ride_requests=ride_requests, unread_messages=unread_messages, has_pending_requests=has_pending_requests, has_unread_messages=has_unread_messages)

@app.route('/view_messages', methods=['GET'])
@login_required
def view_messages():
    # Fetch all messages for the current user
    messages = Message.query.filter_by(recipient_id=current_user.user_id).order_by(Message.timestamp.desc()).all()

    # Set all unread messages to read
    for message in messages:
        message.is_read = True
    db.session.commit()

    return render_template('view_messages.html', messages=messages)

@app.route('/home')
def home():
    newest_rides = Ride.query.order_by(Ride.ride_timestamp.desc()).limit(3).all()
    newest_announcements = Announcement.query.order_by(Announcement.announcement_timestamp.desc()).limit(4).all()

    # Calculate has_pending_requests
    user_ride_ids = [ride.ride_id for ride in current_user.rides]
    has_pending_requests = RideRequest.query.filter(RideRequest.ride_id.in_(user_ride_ids)).count() > 0

    return render_template('home.html', rides=newest_rides, newest_announcements=newest_announcements, has_pending_requests=has_pending_requests)

@app.route('/view_more_requests')
def view_more_requests():
    return render_template('view_more_requests.html')

@app.route('/create_profile', methods=['GET','POST'])
def create_profile():
    if current_user.is_authenticated and not current_user.is_verified:
        flash('Please verify your account first.')
        return redirect(url_for('verify'))
    
    form = ProfileForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            if form.image.data:
                filename = secure_filename(form.image.data.filename)
                upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                form.image.data.save(upload_path)
                profile = Profile(user_id=current_user.user_id, first_name=form.firstname.data, last_name=form.lastname.data, home_town=form.hometown.data, about=form.about.data, user_img=filename)
            else:
                profile = Profile(user_id=current_user.user_id, first_name=form.firstname.data, last_name=form.lastname.data, home_town=form.hometown.data, about=form.about.data)
            db.session.add(profile)
            db.session.commit()
            return redirect(url_for('home'))  # Redirect to home page after profile creation
    return render_template('create_profile.html', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    profile = current_user.profile_backref[0]  # get the first (and only) Profile instance
    if form.validate_on_submit():
        profile.first_name = form.firstname.data
        profile.last_name = form.lastname.data
        profile.home_town = form.hometown.data
        profile.about = form.about.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)  # create directory if it does not exist
            form.image.data.save(upload_path)
            profile.user_img = filename
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.firstname.data = profile.first_name
        form.lastname.data = profile.last_name
        form.hometown.data = profile.home_town
        form.about.data = profile.about
    return render_template('edit_profile.html', form=form)

@app.route('/create_announcement' , methods=['GET', 'POST'])
@login_required
def create_announcement():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        form = AnnouncementForm()
    if form.validate_on_submit():
        announcement = Announcement(user_id=current_user.user_id, announcement_title=form.announcement_title.data, announcement_text=form.announcement_text.data)
        db.session.add(announcement)
        db.session.commit()
        return redirect(url_for('view_announcement', announcement_id=announcement.announcement_id))
    return render_template('create_announcement.html', form=form)

@app.route('/start_ride/')
def start_ride():
    return render_template('start_ride.html')

@app.route('/start_ride/offer', methods=['GET', 'POST'])
@login_required
def start_ride_offer():
    form = RideForm(is_offer_route=True)
    if form.validate_on_submit():
        # if form.accessibility.data is None, set it to an empty list
        if form.accessibility.data is None:
            form.accessibility.data = []
        stops = ','.join([stop.data for stop in form.stops.entries])  # process stops data

        # manually convert departingAt and arrival to datetime.time objects if they're not empty
        departingAt = datetime.strptime(form.departingAt.data, '%I:%M %p').time() if form.departingAt.data else None
        arrival = datetime.strptime(form.arrival.data, '%I:%M %p').time() if form.arrival.data else None

        ride = Ride(
            user_id=current_user.user_id,
            is_offered=True,
            vehicle_type=form.vehicle_type.data,
            ridetype=form.ridetype.data,
            departingFrom=form.departingFrom.data,
            destination=form.destination.data,
            departingAt=departingAt,
            arrival=arrival,
            duration=form.duration.data,
            stops=stops,
            reccuring=form.reccuring.data,
            recurring_days=','.join(form.recurring_days.data),
            accessibility = ','.join(form.accessibility.data),
            ride_description=form.description.data
        )
        db.session.add(ride)
        db.session.commit()

        driver = RidePassenger(
        ride_id=ride.ride_id,
        passenger_id=current_user.user_id,
        confirmed=True,
        is_driver=True,
        role='Driver'
        )
        db.session.add(driver)

        db.session.commit()
        return redirect(url_for('view_post', ride_id=ride.ride_id))
    return render_template('start_ride_offer.html', form=form)

@app.route('/start_ride/request', methods=['GET', 'POST'])
@login_required
def start_ride_request():
    form = RideForm(is_offer_route=True)
    if form.validate_on_submit():
        # if form.accessibility.data is None, set it to an empty list
        if form.accessibility.data is None:
            form.accessibility.data = []
        stops = ','.join([stop.data for stop in form.stops.entries])  # process stops data

        # manually convert departingAt and arrival to datetime.time objects if they're not empty
        departingAt = datetime.strptime(form.departingAt.data, '%I:%M %p').time() if form.departingAt.data else None
        arrival = datetime.strptime(form.arrival.data, '%I:%M %p').time() if form.arrival.data else None

        ride = Ride(
            user_id=current_user.user_id,
            is_offered=False,
            vehicle_type=form.vehicle_type.data,
            ridetype=form.ridetype.data,
            departingFrom=form.departingFrom.data,
            destination=form.destination.data,
            departingAt=departingAt,
            arrival=arrival,
            duration=form.duration.data,
            stops=stops,
            reccuring=form.reccuring.data,
            recurring_days=','.join(form.recurring_days.data),
            accessibility = ','.join(form.accessibility.data),
            ride_description=form.description.data
        )
        db.session.add(ride)
        db.session.commit()

        passenger = RidePassenger(
        ride_id=ride.ride_id,
        passenger_id=current_user.user_id,
        confirmed=True,
        is_driver=False,
        role='passenger'
        )
        db.session.add(passenger)

        db.session.commit()
        return redirect(url_for('view_post', ride_id=ride.ride_id))
    return render_template('start_ride_request.html', form=form)

@app.route('/view_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return "User profile unavailable", 404
    
    profile = user.profile_backref[0]
    home_town = profile.home_town
    about = profile.about

    completed_rides = len([ride for ride in user.rides if ride.completed])
    review_count = Review.query.filter_by(recipient_id=user_id).count()
    reviews = Review.query.filter_by(recipient_id=user_id).all()
    ratings = Rating.query.filter_by(recipient_id=user_id).all()
    categories = ['communication', 'safety', 'punctuality', 'cleanliness']
    average_ratings = {}
    for category in categories:
        category_ratings = [getattr(rating, category) for rating in ratings]
        average_ratings[category] = round(sum(category_ratings) / len(category_ratings), 1) if category_ratings else 0

    ratings_sum = 0
    total_count = 0
    for category in categories:
        category_ratings = [getattr(rating, category) for rating in ratings]
        if category_ratings:
            ratings_sum += sum(category_ratings)
            total_count += len(category_ratings)

    overall_average = round(ratings_sum / total_count, 1) if total_count else 0

    message_form = MessageForm()
    if message_form.validate_on_submit():
        message = Message(user_id=current_user.user_id, recipient_id=user.user_id, content=message_form.content.data, is_read=False)
        db.session.add(message)
        db.session.commit()
        send_new_message_email(current_user, user, message_form.content.data)
        flash('Your message has been sent.', 'success')
        return redirect(url_for('view_profile', user_id=user.user_id))

    form = ReportForm()
    if form.validate_on_submit():
        report = UserReport(reporter_id=current_user.user_id, reported_user_id=user.user_id, report_text=form.report_text.data)
        db.session.add(report)
        db.session.commit()
        flash('Your report has been submitted.', 'success')
        return redirect(url_for('view_profile', user_id=user.user_id))

    return render_template('view_profile.html', user=user, completed_rides=completed_rides, 
                       review_count=review_count, 
                       ratings=average_ratings, home_town=home_town, about=about, overall_average=overall_average, 
                       form=form, message_form=message_form, reviews = reviews)

@app.route('/view_post/<int:ride_id>', methods=['GET','POST'])
@login_required 
def view_post(ride_id):
    post = Ride.query.get_or_404(ride_id)
    if post is None:
        return "Post not found", 404
    profile = post.user.user_profile
    user_img_url = url_for('static', filename='uploads/' + profile.user_img)
    form = SignUpForm()
    report_form = ReportForm()

    if report_form.validate_on_submit():
        report = RideReport(user_id=current_user.user_id, ride_id=ride_id, report_text=report_form.report_text.data)
        db.session.add(report)
        db.session.commit()
        flash('Your report has been submitted.', 'success')
        return redirect(url_for('view_post', ride_id=ride_id))
    
    if form.validate_on_submit():
        existing_request = RideRequest.query.filter_by(ride_id=ride_id, passenger_id=current_user.user_id).first()
        if existing_request:
            flash('You are already signed up for this ride.')
            return redirect(url_for('view_post', ride_id=ride_id))
        
        new_request = RideRequest(
            ride_id=ride_id,
            passenger_id=current_user.user_id,
            role=form.role.data,
            commute_days=','.join(form.commute_days.data),
            accessibility=','.join(form.accessibility.data),
            custom_message=form.custom_message.data,
            requested_stops=','.join(form.requested_stops.data)
        )
        db.session.add(new_request)
        db.session.commit()

        send_ride_driver_email(post.user, current_user, post, new_request)
        send_ride_passenger_email(current_user, post, new_request)

        sender_name = current_user.user_profile.first_name
        ride_details = f"Ride from {post.departingFrom} to {post.destination} on {post.ride_timestamp.strftime('%m/%d/%Y')}"
        custom_message = f"{sender_name} has a special request for the {ride_details}: {form.custom_message.data}" if form.custom_message.data else ""

        if custom_message:  
            message = Message(
                user_id=current_user.user_id,
                recipient_id=post.user.user_id,
                content=custom_message
            )
            db.session.add(message)
            db.session.commit()
        # Create request message
        request_message = f"Your ride request from {post.departingFrom} to {post.destination} has been sent."
        message = Message(
            user_id=current_user.user_id,
            recipient_id=post.user.user_id,
            content=request_message
        )
        db.session.add(message)
        db.session.commit()

        flash('Your request to join the ride has been sent.')
        return redirect(url_for('view_post', ride_id=ride_id))

    return render_template('view_post.html', post=post, profile=profile, user_img_url=user_img_url, form=form, report_form=report_form)

@app.route('/confirm_ride/<int:ride_id>/<int:passenger_id>', methods=['GET', 'POST'])
@login_required
def confirm_ride(ride_id, passenger_id):
    ride = Ride.query.get_or_404(ride_id)
    passenger = User.query.get_or_404(passenger_id)
    form = ConfirmRideForm()
    ride_passenger = None

    # Fetch the ride_request
    ride_request = RideRequest.query.filter_by(ride_id=ride_id, passenger_id=passenger_id).first()

    if current_user.user_id != ride.user_id:
        flash('You are not authorized to confirm this ride.')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        if ride_request:
            existing_ride_passenger = RidePassenger.query.filter_by(ride_id=ride_id, passenger_id=passenger_id).first()
            if existing_ride_passenger:
                flash('A ride passenger with this ride ID and passenger ID already exists.')
            return redirect(url_for('pending_requests_page'))
        else:
            ride_passenger = RidePassenger(
                ride_id=ride_id,
                passenger_id=passenger_id,
                role=ride_request.role,
                commute_days=ride_request.commute_days,
                accessibility=ride_request.accessibility,
                custom_message=ride_request.custom_message,
                requested_stops=ride_request.requested_stops,
                confirmed=True 
            )
            db.session.add(ride_passenger)
            ride.occupants += 1  # increment the occupants field
            db.session.delete(ride_request)
            db.session.commit()
            send_ride_confirmation_email(ride.user, ride, ride_passenger)  # send email to the driver
            send_ride_confirmation_email(passenger, ride, ride_passenger)  # send email to the passenger

            # Create confirmation message
            confirmation_message = f"Your ride request from {ride.departingFrom} to {ride.destination} on {ride.ride_timestamp.strftime('%m/%d/%Y')} has been confirmed."
            message = Message(
                user_id=current_user.user_id,
                recipient_id=passenger.user_id,
                content=confirmation_message
            )
            db.session.add(message)
            db.session.commit()

            flash('The ride has been confirmed.')
            return redirect(url_for('view_post', ride_id=ride_id))

    # Pass the ride to the template
    return render_template('confirm_ride.html', ride=ride, passenger=passenger, ride_passenger=ride_passenger, form=form, request=ride_request)

@app.route('/reject_ride/<int:ride_id>/<int:passenger_id>', methods=['GET', 'POST'])
@login_required
def reject_ride(ride_id, passenger_id):
    form = RejectRideForm()
    ride = Ride.query.get_or_404(ride_id)
    ride_request = RideRequest.query.filter_by(ride_id=ride_id, passenger_id=passenger_id).first()
    passenger = User.query.get_or_404(passenger_id)
    if form.validate_on_submit():
        sender_name = current_user.user_profile.first_name
        rejection_reason = f"Your ride request from {ride.departingFrom} to {ride.destination} on {ride.ride_timestamp.strftime('%m/%d/%Y')} has been rejected by {sender_name} for the following reason: {form.rejection_reason.data}"
        message = Message(
            user_id=current_user.user_id,
            recipient_id=passenger.user_id,
            content=rejection_reason
        )
        db.session.add(message)
        db.session.delete(ride_request)  
        db.session.commit()
        send_ride_rejection_email(passenger, ride, rejection_reason)  # send email to the passenger
        flash('The ride request has been rejected and the passenger has been notified.', 'success')
        return redirect(url_for('pending_requests_page'))
    return render_template('reject_ride.html', title='Reject Ride', form=form, passenger=passenger, ride=ride, request=ride_request)

@app.route('/view_announcement/<int:announcement_id>', methods=['GET'])
@login_required
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    if announcement is None:
        return "Announcement not found", 404
    return render_template('view_announcement.html', announcement=announcement)

@app.route('/find_ride', methods=['GET', 'POST'])
@login_required
def find_ride():
    form = SearchForm()
    rides = Ride.query

    if form.validate_on_submit():
        if form.ridetype.data:
            rides = rides.filter(Ride.ridetype == form.ridetype.data)
        if form.departingFrom.data:
            rides = rides.filter(Ride.departingFrom == form.departingFrom.data)
        if form.destination.data:
            rides = rides.filter(Ride.destination == form.destination.data)

        if form.time_start.data != "12:00AM" and form.time_end.data != "12:00AM":  # only apply filter if time_start and time_end are not equal to their default values
            start = datetime.strptime(form.time_start.data, "%I:%M%p")
            end = datetime.strptime(form.time_end.data, "%I:%M%p")
            if form.time_choice.data == 'Departing':
                rides = rides.filter(and_(Ride.departingAt >= start, Ride.departingAt <= end))
            elif form.time_choice.data == 'Arriving':
                rides = rides.filter(and_(Ride.arrival >= start, Ride.arrival <= end))

        if form.vehicle_type.data:
            rides = rides.filter(Ride.vehicle_type == form.vehicle_type.data)
        if form.duration.data:
            rides = rides.filter(Ride.duration == form.duration.data)
        if form.is_offered.data:
            rides = rides.filter(Ride.is_offered == form.is_offered.data)
        if form.is_requested.data:
            rides = rides.filter(Ride.is_offered != form.is_requested.data)
        if form.stops.data:
            rides = rides.filter(Ride.stops.in_(form.stops.data))
        if form.reccuring.data:
            rides = rides.filter(Ride.reccuring == form.reccuring.data)
        if form.recurring_days.data:
            rides = rides.filter(Ride.recurring_days.in_(form.recurring_days.data))
        if form.accessibility.data:
            rides = rides.filter(Ride.accessibility.in_(form.accessibility.data))

        rides = rides.all()
    else:
        rides = rides.all()

    return render_template('find_ride.html', form=form, rides=rides)

@app.route('/my_rides')
@login_required
def my_rides():
    form = FlaskForm()
    originalPosterRides = Ride.query.filter_by(user_id=current_user.user_id).all()
    passengerRides = RidePassenger.query.filter_by(passenger_id=current_user.user_id).all()
    allRides = originalPosterRides + [ridePassenger.ride for ridePassenger in passengerRides]
    rideDriver = [ride for ride in allRides if any(rp.is_driver and rp.passenger_id == current_user.user_id for rp in ride.passengers)]
    ridePassenger = [ride for ride in allRides if any(not rp.is_driver and rp.passenger_id == current_user.user_id for rp in ride.passengers)]
    currentRides = [ride for ride in allRides if not ride.completed]
    pastRides = [ride for ride in allRides if ride.completed]
    return render_template('my_rides.html', currentRides=currentRides, pastRides=pastRides, ridePassenger=ridePassenger, originalPosterRides=originalPosterRides, rideDriver=rideDriver, form=form)
    
@app.route('/rate_ride/<int:ride_id>', methods=['GET', 'POST'])
def rate_ride(ride_id):
    rating_form = RatingForm()
    review_form = ReviewForm()
    ride = Ride.query.get_or_404(ride_id)
    ride_passenger = RidePassenger.query.filter_by(ride_id=ride_id, passenger_id=current_user.user_id).first()
    
    if ride_passenger is None:
        flash('You were not a passenger on this ride.')
        return redirect(url_for('home'))

    if rating_form.validate_on_submit():
        rating = Rating(
            ride_id=ride_id,
            user_id=current_user.user_id,
            recipient_id=ride.user_id,
            cleanliness=rating_form.cleanliness.data,
            punctuality=rating_form.punctuality.data,
            safety=rating_form.safety.data,
            communication=rating_form.communication.data
            )
        db.session.add(rating)
        db.session.commit()

        if review_form.review_text.data:
            review = Review(
                rating_id=rating.rating_id,
                user_id=current_user.user_id,
                recipient_id=ride.user_id,
                review_text=review_form.review_text.data
            )
            db.session.add(review)
            db.session.commit()

        return redirect(url_for('view_profile', user_id=ride.user_id))

    return render_template('rate_ride.html', rating_form=rating_form, review_form=review_form)

@app.route('/complete_ride/<int:ride_id>', methods=['POST'])
@login_required
def complete_ride(ride_id):
    ride = Ride.query.get(ride_id)
    if ride is None:
        return "No ride found", 404
    if ride.user_id != current_user.user_id:
        return "Not authorized", 403
    ride.completed = True
    db.session.commit()
    return redirect(url_for('my_rides'))

@app.route('/delete_ride/<int:ride_id>', methods=['POST'])
@login_required
def delete_ride(ride_id):
    ride = Ride.query.get(ride_id)
    if ride and ride.user_id == current_user.user_id:
        ratings = Rating.query.filter_by(ride_id=ride_id).all()
        for rating in ratings:
            Review.query.filter_by(rating_id=rating.rating_id).delete()
        Rating.query.filter_by(ride_id=ride_id).delete()
        RidePassenger.query.filter_by(ride_id=ride_id).delete()
        RideRequest.query.filter_by(ride_id=ride_id).delete()
        RideReport.query.filter_by(ride_id=ride_id).delete()
        db.session.delete(ride)
        db.session.commit()
    return redirect(url_for('my_rides'))

@app.route('/cancel_ride/<int:ride_id>', methods=['POST'])
@login_required
def cancel_ride(ride_id):
    ride_passenger = RidePassenger.query.filter_by(ride_id=ride_id, passenger_id=current_user.user_id).first()
    if ride_passenger:
        db.session.delete(ride_passenger)
        db.session.commit()
    return redirect(url_for('my_rides'))

@app.route('/admin_hub', methods=['GET', 'POST'])
@login_required
def admin_hub():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        return render_template('admin_hub.html')

@app.route('/admin_hub/view_reports', methods=['GET', 'POST'])
@login_required
def view_reports():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        user_reports = UserReport.query.all()
        ride_reports = RideReport.query.all()
        return render_template('view_reports.html', user_reports=user_reports, ride_reports=ride_reports)

@app.route('/admin_hub/view_reports/user/<int:report_id>', methods=['GET', 'POST'])
@login_required
def view_user_report(report_id):
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        report = UserReport.query.get_or_404(report_id)
        if report is None:
            return "Report not found", 404
        else:
            reporter = User.query.get_or_404(report.reporter_id)
            reported_user = User.query.get_or_404(report.reported_user_id)
            reporter_user_profile = reporter.profile_backref[0]
            reported_user_profile = reported_user.profile_backref[0]
            form = TakeActionForm()
            form.action.choices = [
                ('select', 'Select an action'),
                ('ban', 'Ban user'),
                ('warn', 'Warn user'),
                ('ignore', 'Ignore report')
            ]
            if form.validate_on_submit():
                if form.action.data == "ban":
                    reported_user.banned = True
                    db.session.delete(report)
                    db.session.commit()

                    subject = "OwlGo Ban"
                    recipient = reported_user.email
                    body = f"You have been banned from OwlGo for violating OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send ban email. Please try again."
                if form.action.data == "warn":
                    db.session.delete(report)
                    db.session.commit()

                    subject = "OwlGo Warning"
                    recipient = reported_user.email
                    body = f"You have been warned for violating OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send warning email. Please try again."
                    
                if form.action.data == "ignore":
                    db.session.delete(report)
                    db.session.commit()

                    subject = "OwlGo Report"
                    recipient = reporter.email
                    body = f"We've decided your report doesn't violate OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send ignore email. Please try again."
                return render_template('action_taken.html', report_id=report_id, form=form, reporter=reporter, reported_user=reported_user, reporter_user_profile=reporter_user_profile, reported_user_profile=reported_user_profile, action=form.action.data)
        return render_template('view_user_report.html', report=report, reporter=reporter, reported_user=reported_user, reported_user_profile=reported_user_profile, reporter_user_profile=reporter_user_profile, form=form)
    
@app.route('/admin_hub/view_reports/ride/<int:report_id>', methods=['GET', 'POST'])
@login_required
def view_ride_report(report_id):
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        report = RideReport.query.get_or_404(report_id)
        if report is None:
            return "Report not found", 404
        else:
            reporter = User.query.get_or_404(report.user_id)
            reporter_user_profile = reporter.profile_backref[0]
            reported_ride = Ride.query.get_or_404(report.ride_id)
            reported_user = User.query.get(reported_ride.user_id)
            reported_user_profile = reported_user.profile_backref[0]
            form = TakeActionForm()
            moreActionForm = TakeActionForm()
            moreActionForm.action.choices = [
                ('select', 'Select an action'),
                ('ban', 'Ban user'),
                ('warn', 'Warn user')
            ]

            form.action.choices = [
                ('select', 'Select an action'),
                ('delete', 'Delete ride'),
                ('ignore', 'Ignore report')
            ]

            if moreActionForm.validate_on_submit():
                if moreActionForm.action.data == "ban":
                    reported_user.banned = True
                    db.session.commit()

                    subject = "OwlGo Ban"
                    recipient = reported_user.email
                    body = f"You have been banned from OwlGo for violating OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send ban email. Please try again."
                if moreActionForm.action.data == "warn":
                    db.session.delete(report)
                    db.session.commit()

                    subject = "OwlGo Warning"
                    recipient = reported_user.email
                    body = f"You have been warned for violating OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send warning email. Please try again."
                return render_template('action_taken.html', report_id=report_id, reporter=reporter, action=moreActionForm.action.data, reported_user_profile=reported_user_profile, reported_user=reported_user, reporter_user_profile=reporter_user_profile)

            if form.validate_on_submit():
                if form.action.data == "delete":
                    RideReport.query.filter_by(ride_id=reported_ride.ride_id).delete()
                    db.session.delete(reported_ride)
                    db.session.commit() 

                    subject = "OwlGo Report"
                    recipient = reported_user.email
                    body = f"Your ride has been deleted for violating OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send delete email. Please try again."
                    
                    redirect(url_for('view_reports'))
                    
                if form.action.data == "ignore":
                    db.session.delete(report)
                    db.session.commit()

                    subject = "OwlGo Report"
                    recipient = reporter.email
                    body = f"We've decided your report doesn't violate OwlGo's terms of service."
                    msg = MailMessage(subject=subject, recipients=[recipient], body=body)

                    try:
                        mail.send(msg)
                    except SMTPException:
                        return "Failed to send ignore email. Please try again."
                    
                    redirect(url_for('view_reports'))
                return render_template('view_reports.html', report_id=report_id, moreActionForm=moreActionForm, reporter=reporter, reported_ride=reported_ride, action=form.action.data, reported_user_profile=reported_user_profile, reported_user=reported_user, reporter_user_profile=reporter_user_profile)
            return render_template('view_ride_report.html', report=report, reporter=reporter, reported_ride=reported_ride, form=form, reported_user_profile=reported_user_profile, reported_user=reported_user, reporter_user_profile=reporter_user_profile)

@app.route('/admin_hub/view_usage', methods=['GET', 'POST'])
@login_required
def view_usage():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        totalUsers = User.query.count()
        totalRides = Ride.query.count()
        totalCompletedRides = Ride.query.filter_by(completed=True).count()
        totalAnnouncements = Announcement.query.count()
        totalReviews = Review.query.count()
        totalRatings = Rating.query.count()
        totalMessages = Message.query.count()
        totalRideRequests = RideRequest.query.count()
        totalCommuteRides = Ride.query.filter_by(ridetype='commute').count()
        totalErrandRides = Ride.query.filter_by(ridetype='errand').count()
        totalLeisureRides = Ride.query.filter_by(ridetype='leisure').count()
        totalOfferedRides = Ride.query.filter_by(is_offered=True).count()
        totalRequestedRides = Ride.query.filter_by(is_offered=False).count()
        
        averageRidesPerUser = totalRides / totalUsers
        averageCompletedRidesPerUser = totalCompletedRides / totalUsers
        averageReviewsPerUser = totalReviews / totalUsers
        averageRatingsPerUser = totalRatings / totalUsers
        averageRidesPerDay = totalRides / 365
        averageMessagesPerUser = totalMessages / totalUsers
        averageRideRequestsPerUser = totalRideRequests / totalUsers
        averagePassengers = Ride.query.with_entities(func.avg(Ride.occupants)).first()[0]

        ratingToReviewRatio = totalRatings / totalReviews if totalReviews != 0 else 0
        rideToCompletedRatio = totalRides / totalCompletedRides if totalCompletedRides != 0 else 0
        offerToRequestedRatio = totalOfferedRides / totalRequestedRides if totalRequestedRides != 0 else 0

        rides_list = Ride.query.all() 
        sorted_rides_list = sorted(rides_list, key=lambda ride: ride.ride_timestamp or datetime.min)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = str(time.time())

        # creating a new directory for graphs
        graph_dir = os.path.join(current_dir, 'static/img/graphs')
        os.makedirs(graph_dir, exist_ok=True)

        # ride over time
        ridesPerDate = defaultdict(int)
        for ride in rides_list:
            if ride.ride_timestamp is not None:
                date = ride.ride_timestamp.date()
                ridesPerDate[date] += 1
        dates, counts = zip(*sorted(ridesPerDate.items()))

        plt.plot(dates, counts)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        plt.xlabel('Date')
        plt.ylabel('Number of Rides')
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        plt.title('Total Rides Over Time')
        img_path = os.path.join(graph_dir, f'total_rides_over_time_{timestamp}.png')
        plt.savefig(img_path)
        plt.clf()

        # tides per weekday
        ridesPerWeekday = defaultdict(int)
        for ride in sorted_rides_list:
            if ride.ride_timestamp is not None:
                weekday = ride.ride_timestamp.weekday()  # This will be an integer
                ridesPerWeekday[weekday] += 1

        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        counts = [ridesPerWeekday[weekday] for weekday in range(7)]  # Use integers as indices
        plt.bar(weekdays, counts)
        plt.xlabel('Weekday')
        plt.ylabel('Number of Rides')
        plt.title('Total Rides Per Weekday')
        img_path = os.path.join(graph_dir, f'total_rides_per_weekday_{timestamp}.png')
        plt.savefig(img_path)
        plt.clf()

        # ride types
        ride_types = ['Commute', 'Errand', 'Leisure']
        counts = [totalCommuteRides, totalErrandRides, totalLeisureRides]
        plt.pie(counts, labels=ride_types, autopct='%1.1f%%')
        plt.title('Ride Types')
        img_path = os.path.join(graph_dir, f'ride_types_{timestamp}.png')
        plt.savefig(img_path)
        plt.clf()

        # ratings and reviews
        if totalReviews > 0 and totalRatings > 0:
            plt.bar(['Total Ratings', 'Total Reviews'], [totalRatings, totalReviews])
            plt.ylabel('Count')
            plt.title('Ratings and Reviews')
            img_path = os.path.join(graph_dir, f'rating_to_review_{timestamp}.png')
            plt.savefig(img_path)
            plt.clf()

        # offered and requested
        if totalOfferedRides > 0 and totalRequestedRides > 0:
            plt.bar(['Total Offered Rides', 'Total Requested Rides'], [totalOfferedRides, totalRequestedRides])
            plt.ylabel('Count')
            plt.title('Offered and Requested Rides')
            img_path = os.path.join(graph_dir, f'offer_to_requested_{timestamp}.png')
            plt.savefig(img_path)
            plt.clf()

        # rides and completed Rides
        if totalRides > 0:
            plt.bar(['Total Rides', 'Total Completed Rides'], [totalRides, totalCompletedRides])
            plt.ylabel('Count')
            plt.title('Rides and Completed Rides')
            img_path = os.path.join(graph_dir, f'ride_to_completed_{timestamp}.png')
            plt.savefig(img_path)
            plt.clf()

        # delete old images
        image_files = glob.glob(os.path.join(graph_dir, '*.png'))

        # group the files by type
        image_files_by_type = defaultdict(list)
        for image_file in image_files:
            # get type from the file name
            match = re.match(r'.*/(.*?)_\d+\.\d+\.png$', image_file)
            if match:
                image_type = match.group(1)
                image_files_by_type[image_type].append(image_file)

        # sort the files by creation time and delete all except most recent
        for image_type, image_files in image_files_by_type.items():
            image_files.sort(key=os.path.getctime)
            for image_file in image_files[:-1]:
                os.remove(image_file)

        return render_template('view_usage.html', totalUsers=totalUsers, totalRides=totalRides, totalCompletedRides=totalCompletedRides, 
                               totalAnnouncements=totalAnnouncements, totalReviews=totalReviews, totalRatings=totalRatings, 
                               totalMessages=totalMessages, totalRideRequests=totalRideRequests, totalCommuteRides=totalCommuteRides, 
                               totalErrandRides=totalErrandRides, totalLeisureRides=totalLeisureRides, totalOfferedRides=totalOfferedRides, 
                               totalRequestedRides=totalRequestedRides, averageRidesPerUser=averageRidesPerUser, 
                               averageCompletedRidesPerUser=averageCompletedRidesPerUser, averageReviewsPerUser=averageReviewsPerUser, 
                               averageRatingsPerUser=averageRatingsPerUser, averageRidesPerDay=averageRidesPerDay, 
                               averageMessagesPerUser=averageMessagesPerUser, averageRideRequestsPerUser=averageRideRequestsPerUser, 
                               averagePassengers=averagePassengers, ratingToReviewRatio=ratingToReviewRatio, rideToCompletedRatio=rideToCompletedRatio, 
                               offerToRequestedRatio=offerToRequestedRatio, timestamp=timestamp)
    