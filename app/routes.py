from app.models import User, Profile, Ride, RidePassenger, Message, Rating, Review, Post, Announcement
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import RegistrationForm, LoginForm, ChangePasswordForm

@app.route('/') # landing
# user registration and log in
@app.route('/register')
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
         user=User(username=form.username.data, email=form.email.data, password=form.username.password)
         db.session.add(user)
         db.session commit
         print('Registration_successful',file=sys.stderr)
@app.route('/login')
def login():
    form =LoginForm()
    if form.validate_on_submit():
        user=db.session.query(User).filter_by(username=form.username.data)
        if user is None or not user.check_password(form.password.data):
             print('Login failed', file=sys.stderr)
        return redirect(url_for('login'))
        login_user(user)
         print('Login successful', file=sys.stderr)
# example data insertion
#   user = User(username='john_doe', email='john@example.com')
#   db.session.add(user)
#   db.session.commit()

@app.route('/home')

@app.route('/create_profile')

@app.route('/home_admin')

@app.route('/create_announcement')

@app.route('/start_ride')

@app.route('/start_ride/offer')

@app.route('/start_ride/request')

@app.route('/find_ride')

@app.route('/view_profile')

@app.route('/view_post')
