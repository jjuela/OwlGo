from datetime import time
from app.models import User, Profile, Ride, Ride_Passenger, Message, Rating, Review, Announcement
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.forms import RegistrationForm, LoginForm,  ProfileForm, AnnouncementForm, RideForm
from flask import request

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
        profile = Profile(user_id = current_user.user_id, first_name=form.firstname.data, last_name=form.lastname.data, home_town=form.hometown.data, about=form.about.data, user_img=form.image.data)
        db.session.add(profile)
        db.session.commit()
        return "Profile created!"
    return render_template('create_profile.html', form=form)
        
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
        ride = Ride(
            user_id=current_user.id,
            is_offered=True,
            vehicle_type=form.vehicle_type.data,
            ridetype=form.ridetype.data,
            departingFrom=form.departingFrom.data,
            destination=form.destination.data,
            departingAt=form.departingAt.data,
            arrival=form.arrival.data,
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
    return render_template('view_profile.html', user=user)

@app.route('/view_post/<int:ride_id>', methods=['GET']) # removed '<post_type>/<int:id>' temporarily for dummy post
def view_post(ride_id):
    post = Ride.query.get_or_404(ride_id)
    if post is None:
        return "Post not found", 404
    profile = Profile.query.get_or_404(post.user_id)
    return render_template('view_post.html', post=post, profile=profile)

    # dummy post
    # post = Ride(
    #     user_id=1,
    #     ridetype='commute',
    #     occupants=1,
    #     vehicle_type='Sedan',
    #     departingFrom='Location A',
    #     destination='Location B',
    #     reccuring=True,
    #     recurring_days='Monday, Wednesday, Friday',
    #     accessibility='Wheelchair accessible',
    #     completed=False,
    #     ride_description='This is a test post.',
    #     departingAt=time(10, 0),  # 10:00 AM
    #     arrival=time(11, 0),  # 11:00 AM
    #     stops=None,
    #     duration=None,
    #     is_offered=True
    # )

    # # dummy profile
    # profile = Profile(
    #     user_id=1,
    #     first_name='John',
    #     last_name='Doe',
    #     home_town='Location A',
    #     about='This is a test user.',
    #     user_img='img/pfp.png'  # replace with the actual path
    # )

    # return render_template('view_post.html', post=post, profile=profile)

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