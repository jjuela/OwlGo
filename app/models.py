from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

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

    def set_password(self, password):
        self.password = generate_password_hash(password)

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

    user = db.relationship('User', backref='user_profile')

class Ride(db.Model):
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ridetype = db.Column(db.String(50))  
    occupants = db.Column(db.Integer)
    vehicle_type = db.Column(db.String(50))
    departingFrom = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    reccuring = db.Column(db.Boolean)
    recurring_days = db.Column(db.String(50))
    accessibility = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    ride_description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    departingAt = db.Column(db.Time)
    arrival = db.Column(db.Time)
    stops = db.Column(db.String(500))
    duration = db.Column(db.String(50))
    is_offered = db.Column(db.Boolean)

    ratings = db.relationship('Rating', backref='rated_ride')

class Ride_Passenger(db.Model):
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

    ride = db.relationship('Ride', backref='passengers')
    passenger = db.relationship('User', backref='ridden_rides')

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

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
    announcement_text = db.Column(db.Text)
    announcement_date = db.Column(db.DateTime)

    user = db.relationship('User', backref='created_announcements')

@login.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))