from app.models import User, Profile, Ride, Ride_Passenger, Message, Rating, Review, Announcement, Ride_Request
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.forms import RegistrationForm, LoginForm,  ProfileForm, AnnouncementForm, RideForm, SignUpForm, SearchForm, FilterForm
from flask import request
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func
from sqlalchemy import and_

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

@app.route('/create_profile', methods=['GET','POST'])
def create_profile():
    form = ProfileForm()
    if form.validate_on_submit():
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
        return "Profile created!"
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

@app.route('/start_ride/')
def start_ride():
    return render_template('start_ride.html')

@app.route('/start_ride/offer', methods=['GET', 'POST'])
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
        db.session.commit()
    return render_template('start_ride_offer.html', form=form)

@app.route('/start_ride/request', methods=['GET', 'POST'])
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
        db.session.commit()
    return render_template('start_ride_request.html', form=form)

# @app.route('/find_ride')

@app.route('/view_profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return "User profile unavailable", 404
    
    profile = user.profile_backref[0]  # get the Profile instance associated with the User. have to do [0] since i don't want to change the backref
    home_town = profile.home_town
    about = profile.about

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
                           ratings=average_ratings, home_town=home_town, about=about)

@app.route('/view_post/<int:ride_id>', methods=['GET','POST'])
#@login_required 
def view_post(ride_id):
    post = Ride.query.get_or_404(ride_id)
    if post is None:
        return "Post not found", 404
    profile = post.user.user_profile
    user_img_url = url_for('static', filename='uploads/' + profile.user_img)
    form = SignUpForm()
    if form.validate_on_submit():
        existing_request = Ride_Request.query.filter_by(ride_id=ride_id, passenger_id=current_user.user_id).first()
        if existing_request:
            print('You are already signed up for this ride.')
            return redirect(url_for('view_post', ride_id=ride_id))
        
        new_request = Ride_Request(
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

    return render_template('view_post.html', post=post, profile=profile, user_img_url=user_img_url)

@app.route('/confirm_ride/<int:ride_id>/<int:passenger_id>', methods=['GET', 'POST'])
@login_required 
def confirm_ride(ride_id, passenger_id):
    ride = Ride.query.get_or_404(ride_id)
    passenger = User.query.get_or_404(passenger_id)

    if request.method == 'POST':
        if current_user.user_id != ride.user_id:
            print('You are not authorized to confirm this ride.')
            return redirect(url_for('view_post', ride_id=ride_id))

        ride_request = Ride_Request.query.filter_by(ride_id=ride_id, passenger_id=passenger_id).order_by(Ride_Request.timestamp).first()
        if ride_request:
            ride_passenger = Ride_Passenger(
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

            print('The ride has been confirmed.')
            return redirect(url_for('view_post', ride_id=ride_id))

    return render_template('confirm_ride.html', ride=ride, passenger=passenger)

@app.route('/view_announcement/<int:announcement_id>', methods=['GET'])
def view_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    if announcement is None:
        return "Announcement not found", 404
    return render_template('view_announcement.html', announcement=announcement)

@app.route('/Find_A_Ride', methods=['GET', 'POST'])
def find_a_ride():
    search_form = SearchForm()
    filter_form = FilterForm()

    if search_form.validate_on_submit():
        rides = Ride.query.filter_by(
            ridetype=search_form.ridetype.data,
            departingFrom=search_form.departingFrom.data,
            destination=search_form.destination.data
        )

        if search_form.time_start.data and search_form.time_end.data:
            start = datetime.strptime(search_form.time_start.data, "%I:%M%p")
            end = datetime.strptime(search_form.time_end.data, "%I:%M%p")
            if search_form.time_choice.data == 'Departing':
                rides = rides.filter(and_(Ride.departingAt >= start, Ride.departingAt <= end))
            elif search_form.time_choice.data == 'Arriving':
                rides = rides.filter(and_(Ride.arrival >= start, Ride.arrival <= end))

        if filter_form.validate_on_submit():
            rides = rides.filter_by(
                vehicle_type=filter_form.vehicle_type.data,
                duration=filter_form.duration.data,
                stops=filter_form.stops.data,
                reccuring=filter_form.reccuring.data,
                recurring_days=filter_form.recurring_days.data,
                accessibility=filter_form.accessibility.data,
                description=filter_form.description.data
            )

        rides = rides.all()

    else:
        rides = []

    return render_template('find_a_ride.html', search_form=search_form, filter_form=filter_form, rides=rides)

@app.route('/my_rides')
def my_rides():
    return render_template('my_rides.html')
    # after someone signs up for a ride and is accepted, 
    # they should be able to see it here
    # this should have active rides and history of rides
    # this should also have an option to cancel a ride

