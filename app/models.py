from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app

class User(UserMixin, db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(256))
    email = db.Column(db.String(320), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)

    rides = db.relationship('Ride', backref='user')
    sent_messages = db.relationship('Message', foreign_keys='Message.user_id', backref='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='received')
    given_ratings = db.relationship('Rating', foreign_keys='Rating.user_id', backref='rater')
    received_ratings = db.relationship('Rating', foreign_keys='Rating.recipient_id', backref='rated')
    given_reviews = db.relationship('Review', foreign_keys='Review.user_id', backref='reviewer')
    received_reviews = db.relationship('Review', foreign_keys='Review.recipient_id', backref='reviewed')
    announcements = db.relationship('Announcement', backref='announcer')
    user_profile = db.relationship('Profile', backref='user_profile_backref', uselist=False)

    verification_code = db.Column(db.String(20))  
    is_verified = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_reset_password_token(self, expires_in=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'reset_password': self.user_id}).decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['reset_password'])

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_id(self):
        return str(self.user_id)

class Profile(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    home_town = db.Column(db.String(50))
    about = db.Column(db.Text)
    user_img = db.Column(db.String(255))

    user = db.relationship('User', backref='profile_backref')

class Ride(db.Model):
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ridetype = db.Column(db.String(50))  
    occupants = db.Column(db.Integer, default=1)
    vehicle_type = db.Column(db.String(50))
    departingFrom = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    reccuring = db.Column(db.Boolean)
    recurring_days = db.Column(db.String(50))
    accessibility = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    ride_description = db.Column(db.Text)
    departingAt = db.Column(db.Time)
    arrival = db.Column(db.Time)
    stops = db.Column(db.String(500))
    duration = db.Column(db.String(50))
    is_offered = db.Column(db.Boolean)
    ride_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    ratings = db.relationship('Rating', backref='rated_ride')

class RidePassenger(db.Model):
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    is_driver = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(255))
    commute_days = db.Column(db.String(255))
    accessibility = db.Column(db.String(255))
    custom_message = db.Column(db.String(255))
    requested_stops = db.Column(db.String(255))  # Add this line
    
    ride = db.relationship('Ride', backref='passengers')
    passenger = db.relationship('User', backref='ridden_rides')

class RideRequest(db.Model):
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    ride = db.relationship('Ride', backref='requests')
    passenger = db.relationship('User', backref='ride_requests')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(10))
    commute_days = db.Column(db.String(50))
    accessibility = db.Column(db.String(100))
    custom_message = db.Column(db.String(500))
    requested_stops = db.Column(db.String(100))
    confirmed = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship('User', foreign_keys=[user_id], backref='user_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='receiver_messages')

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable=False)
    cleanliness = db.Column(db.SmallInteger)
    punctuality = db.Column(db.SmallInteger)
    safety = db.Column(db.SmallInteger)
    communication = db.Column(db.SmallInteger)
    average = db.Column(db.Numeric(3, 2))

    user = db.relationship('User', foreign_keys=[user_id], backref='user_ratings')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='receiver_ratings')
    ride = db.relationship('Ride', backref='ride_ratings')

class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    review_text = db.Column(db.Text)

    rating = db.relationship('Rating', backref='review')
    user = db.relationship('User', foreign_keys=[user_id], backref='reviews')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='receiver_reviews')

class Announcement(db.Model):
    announcement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    announcement_title = db.Column(db.String(100))
    announcement_text = db.Column(db.Text)
    announcement_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='created_announcements')

class RideReport(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable=False)
    report_text = db.Column(db.Text)
    report_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='created_ride_reports')
    ride = db.relationship('Ride', backref='ride_reports')

class UserReport(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    reported_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    report_text = db.Column(db.Text)
    report_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='created_user_reports')
    reported_user = db.relationship('User', foreign_keys=[reported_user_id], backref='user_reports')

@login.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))