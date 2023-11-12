from app.models import User, Profile, Ride, Ride_Passenger, Message, Rating, Review, Announcement
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.forms import RegistrationForm, LoginForm,  ProfileForm, AnnouncementForm, RideForm
from flask import request
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func

@app.route('/', methods=['GET', 'POST'])
def landing():
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
        user = User(email=register_form.email.data)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('create_profile'))

    return render_template('landing.html', login_form=login_form, register_form=register_form)

@app.route('/home')
def home():
    return "home"

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

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.profile_backref.first_name = form.firstname.data
        current_user.profile_backref.last_name = form.lastname.data
        current_user.profile_backref.home_town = form.hometown.data
        current_user.profile_backref.about = form.about.data
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)  # create directory if it does not exist
            form.image.data.save(upload_path)
            current_user.profile_backref.user_img = filename
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.firstname.data = current_user.profile_backref.first_name
        form.lastname.data = current_user.profile_backref.last_name
        form.hometown.data = current_user.profile_backref.home_town
        form.about.data = current_user.profile_backref.about
    return render_template('edit_profile.html', form=form)
        
# @app.route('/home_admin')

@app.route('/create_announcement' , methods=['POST'])
def create_announcement():
    if current_user.admin == False:
        return "You are not an admin!"
    else:
        form = AnnouncementForm()
        if form.validate_on_submit():
            announcement = Announcement(announcement_text=form.announcetext.data, announcement_date=form.announcedate.data)
            db.session.add(announcement)
            db.session.commit()
            return "Announcement created!"
    return render_template('create_announcement.html', form=form)

@app.route('/start_ride')
def start_ride():
    return render_template('start_ride.html')

@app.route('/start_ride/offer', methods=['GET', 'POST'])
def start_ride_offer():
    form = RideForm(is_offer_route=True)
    print(request.form)
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
            departingAt=departingAt,  # use the converted departingAt
            arrival=arrival,  # use the converted arrival
            duration=form.duration.data,
            stops=stops,  # processed stops
            reccuring=form.reccuring.data,
            recurring_days=','.join(form.recurring_days.data),  # process recurring_days data
            accessibility = ','.join(form.accessibility.data),
            ride_description=form.description.data
        )
        db.session.add(ride)
        try:
            db.session.commit()
            print("Ride committed to database")
        except Exception as e:
            print("Error committing ride to database:", e)
        return "Ride created!"
    else:
        print("Form did not validate on submit")
        print(form.errors)
    return render_template('start_ride_offer.html', form=form)

# @app.route('/start_ride/request')

# @app.route('/find_ride')

@app.route('/view_profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return "User profile unavailable", 404
    
    completed_rides = len([ride for ride in user.rides if ride.completed])
    review_count = len(user.received_reviews)  # get the number of received reviews
    ratings = user.received_ratings

    # calculate average for each category
    categories = ['communication', 'safety', 'punctuality', 'cleanliness']
    average_ratings = {}
    for category in categories:
        category_ratings = [getattr(rating, category) for rating in ratings]
        average_ratings[category] = sum(category_ratings) / len(category_ratings) if category_ratings else 0

    return render_template('view_profile.html', user=user, completed_rides=completed_rides, 
                           review_count=review_count, reviews=user.received_reviews, 
                           ratings=average_ratings)

@app.route('/view_post/<int:ride_id>', methods=['GET']) 
def view_post(ride_id):
    post = Ride.query.get_or_404(ride_id)
    if post is None:
        return "Post not found", 404
    profile = post.user.user_profile
    user_img_url = url_for('static', filename='uploads/' + profile.user_img)
    return render_template('view_post.html', post=post, profile=profile, user_img_url=user_img_url)

@app.route('/view_announcement/<int:announcement_id>', methods=['GET'])
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    if announcement is None:
        return "Announcement not found", 404
    return render_template('view_announcement.html', announcement=announcement)

@app.route('/my_rides')
def my_rides():
    return render_template('my_rides.html')
    # after someone signs up for a ride and is accepted, 
    # they should be able to see it here
    # this should have active rides and history of rides
    # this should also have an option to cancel a ride

