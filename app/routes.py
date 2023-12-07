# flask imports
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message as MailMessage, Mail

# sqlalchemy imports
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError

# app imports
from app import app, db, mail
from app.models import User, Profile, Ride, RidePassenger, Message, Rating, Review, Announcement, RideRequest, RideReport, UserReport
from app.forms import RegistrationForm, LoginForm, ProfileForm, AnnouncementForm, RideForm, SignUpForm, SearchForm, VerificationForm, PasswordResetRequestForm, PasswordResetForm, ReportForm
from app.utils import generate_verification_code, send_password_reset_email

# other imports
from datetime import datetime
from smtplib import SMTPException
from werkzeug.utils import secure_filename
from pytz import timezone, utc
import os

@app.template_filter('datetimefilter')
def datetimefilter(value, format='%B %d, %Y %I:%M %p'):
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = utc.localize(value)
    eastern = timezone('US/Eastern')
    value = value.astimezone(eastern)
    return value.strftime(format)

@app.context_processor # this is so templates can use utility functions
def utility_functions():
    def get_full_day_names(recurring_days):
        day_names = {'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday', 'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'}
        return ', '.join(day_names[day] for day in recurring_days.split(','))

    def get_full_accessibility_names(accessibility_keys):
        accessibility_names = {
            'wheelchair': 'Wheelchair',
            'visual': 'Visual impairment',
            'hearing': 'Hearing impairment',
            'service_dog': 'Service dog friendly',
            'quiet': 'Quiet ride',
            'step_free': 'Step-free access',
        }
        return ', '.join(accessibility_names[key] for key in accessibility_keys.split(','))

    return dict(get_full_day_names=get_full_day_names, get_full_accessibility_names=get_full_accessibility_names)

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

            subject = "Sign up verification code"
            recipient = [user.email]
            body = "Your verification code is: " + verification_code + "\n\n" + "Please enter this code on the verification page to create your profile."

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
            flash('Account verified and logged in successfully.')
            return redirect(url_for('create_profile'))
        else:
            flash('Invalid verification code. Please try again.')

    return render_template('verify.html', form=form)

@app.route('/home')
def home():
    newest_rides = Ride.query.order_by(Ride.ride_timestamp.desc()).limit(3).all()
    newest_announcements = Announcement.query.order_by(Announcement.announcement_timestamp.desc()).limit(5).all()

    return render_template('home.html', rides=newest_rides, newest_announcements=newest_announcements)

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
    review_count = len(user.received_reviews)
    ratings = user.received_ratings

    categories = ['communication', 'safety', 'punctuality', 'cleanliness']
    average_ratings = {}
    for category in categories:
        category_ratings = [getattr(rating, category) for rating in ratings]
        average_ratings[category] = sum(category_ratings) / len(category_ratings) if category_ratings else 0

    total_ratings = 0
    total_count = 0
    for category in categories:
        category_ratings = [getattr(rating, category) for rating in ratings]
        if category_ratings:
            total_ratings += sum(category_ratings)
            total_count += len(category_ratings)

    average_rating = total_ratings / total_count if total_count else 0

    form = ReportForm()
    if form.validate_on_submit():
        report = UserReport(reporter_id=current_user.user_id, reported_user_id=user.user_id, report_text=form.report_text.data)
        db.session.add(report)
        db.session.commit()
        flash('Your report has been submitted.', 'success')
        return redirect(url_for('view_profile', user_id=user.user_id))

    return render_template('view_profile.html', user=user, completed_rides=completed_rides, 
                           review_count=review_count, reviews=user.received_reviews, 
                           ratings=average_ratings, home_town=home_town, about=about, average_rating=average_rating, form=form)

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
            print('You are already signed up for this ride.')
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

        custom_message = f" Message: {form.custom_message.data}" if form.custom_message.data else ""
        message = Message(user_id=current_user.user_id, recipient_id=post.user_id, content=f"{current_user.username} has requested to join your ride.{custom_message}")
        db.session.add(message)
        db.session.commit()

        print('Your request to join the ride has been sent.')
        return redirect(url_for('view_post', ride_id=ride_id))

    return render_template('view_post.html', post=post, profile=profile, user_img_url=user_img_url, form=form, report_form=report_form)

@app.route('/confirm_ride/<int:ride_id>/<int:passenger_id>', methods=['GET', 'POST'])
@login_required 
def confirm_ride(ride_id, passenger_id):
    ride = Ride.query.get_or_404(ride_id)
    passenger = User.query.get_or_404(passenger_id)

    if request.method == 'POST':
        if current_user.user_id != ride.user_id:
            flash('You are not authorized to confirm this ride.')
            return redirect(url_for('view_post', ride_id=ride_id))

        ride_request = RideRequest.query.filter_by(ride_id=ride_id, passenger_id=passenger_id).order_by(Ride_Request.timestamp).first()
        if ride_request:
            ride_passenger = RidePassenger(
                ride_id=ride_id,
                passenger_id=passenger_id,
                role=ride_request.role,
                commute_days=ride_request.commute_days,
                accessibility=ride_request.accessibility,
                custom_message=ride_request.custom_message,
                requested_stops=ride_request.requested_stops
            )
            db.session.add(ride_passenger)
            db.session.delete(ride_request)
            db.session.commit()

            flash('The ride has been confirmed.')
            return redirect(url_for('view_post', ride_id=ride_id))

    return render_template('confirm_ride.html', ride=ride, passenger=passenger)

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
        if form.is_offered.data is not None and form.is_offered.data != False:  # only apply filter if is_offered is not equal to its default value
            rides = rides.filter(Ride.is_offered == form.is_offered.data)
        if form.is_requested.data is not None:
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
    return render_template('my_rides.html')
    # after someone signs up for a ride and is accepted, 
    # they should be able to see it here
    # this should have active rides and history of rides
    # this should also have an option to cancel a ride

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
        return render_template('view_user_report.html', report=report)

@app.route('/admin_hub/view_reports/ride/<int:report_id>', methods=['GET', 'POST'])
@login_required
def view_ride_report(report_id):
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        report = RideReport.query.get_or_404(report_id)
        if report is None:
            return "Report not found", 404
        return render_template('view_ride_report.html', report=report)

@app.route('/admin_hub/ban_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def ban_user(user_id):
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        user = User.query.get_or_404(user_id)
        if user is None:
            return "User not found", 404
        user.banned = True
        db.session.commit()
        return "User has been banned"

@app.route('/admin_hub/delete_post/<int:ride_id>', methods=['GET', 'POST'])
@login_required
def delete_post(ride_id):
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        ride = Ride.query.get_or_404(ride_id)
        if ride is None:
            return "Ride not found", 404
        db.session.delete(ride)
        db.session.commit()
        return "Ride has been deleted"

@app.route('/admin_hub/view_usage', methods=['GET', 'POST']) # where usage statistics will go
@login_required
def view_usage():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        return render_template('view_usage.html')
    