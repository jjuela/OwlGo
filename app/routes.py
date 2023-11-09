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
        return redirect(url_for('home'))

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

# @app.route('/start_ride')

@app.route('/start_ride_offer', methods=['GET', 'POST'])
def start_ride_offer():
    form = RideForm()
    if form.validate_on_submit():
        # if form.accessibility.data is None, set it to an empty list
        if form.accessibility.data is None:
            form.accessibility.data = []
        ride = Ride(
            ridetype=form.ridetype.data,
            departingFrom=form.departingFrom.data,
            destination=form.destination.data,
            departingAt=form.departingAt.data,
            arrival=form.arrival.data,
            duration=form.duration.data,
            stops=form.stops.data,
            reccuring=form.reccuring.data,
            recurring_days=form.recurring_days.data,
            accessibility=form.accessibility.data,
            description=form.description.data
        )
        db.session.add(ride)
        db.session.commit()
        return "Ride created!"
    return render_template('start_ride_offer.html', form=form)

# @app.route('/start_ride/request')

# @app.route('/find_ride')

@app.route('/view_profile/<int:user_id>', methods=['GET', 'POST'])
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user is None:
        return "User profile unavailable", 404
    return render_template('view_profile.html', user=user)

@app.route('/view_post/<post_type>/<int:id>', methods=['GET'])
def view_post(post_type, id):
    if post_type == 'announcement':
        post = Announcement.query.get(id)
    elif post_type == 'ride':
        post = Ride.query.get(id)
    else:
        return "Invalid post type", 400

    if post is None:
        return "Post not found", 404

    return render_template('view_post.html', post=post)
