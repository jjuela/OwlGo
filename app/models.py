from app import db

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(256))
    email = db.Column(db.String(320), unique=True, nullable=False)
    admin = db.Column(db.Boolean, default=False)
    banned = db.Column(db.Boolean, default=False)

class Profile(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    home_town = db.Column(db.String(50))
    about = db.Column(db.Text)
    user_img = db.Column(db.String(255))
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'))
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'))
    review_id = db.Column(db.Integer, db.ForeignKey('review.review_id'))

    ride = db.relationship('Ride', back_populates='profiles')
    rating = db.relationship('Rating', back_populates='profiles')
    review = db.relationship('Review', back_populates='profiles')

class Ride(db.Model):
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    occupants = db.Column(db.Integer)
    vehicle_type = db.Column(db.String(50))
    start_location = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    accessibility_categories = db.Column(db.String(100))
    completed = db.Column(db.Boolean, default=False)
    ride_description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    pickup_time = db.Column(db.Time)
    dropoff_time = db.Column(db.Time)
    repeating = db.Column(db.Boolean, default=False)

    profiles = db.relationship('Profile', back_populates='ride')
    user = db.relationship('User', back_populates='rides')

class RidePassenger(db.Model):
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)

    ride = db.relationship('Ride', backref='passengers')
    passenger = db.relationship('User', backref='rides')

class Message(db.Model):
    message_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    user = db.relationship('User', foreign_keys=[user_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')

class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable=False)
    cleanliness = db.Column(db.SmallInteger(unsigned=True))
    punctuality = db.Column(db.SmallInteger(unsigned=True))
    safety = db.Column(db.SmallInteger(unsigned=True))
    communication = db.Column(db.SmallInteger(unsigned=True))
    average = db.Column(db.Numeric(3, 2))

    user = db.relationship('User', foreign_keys=[user_id], backref='given_ratings')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_ratings')
    ride = db.relationship('Ride', back_populates='ratings')

class Review(db.Model):
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rating_id = db.Column(db.Integer, db.ForeignKey('rating.rating_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('rating.recipient_id'), nullable=False)
    review_text = db.Column(db.Text)

    rating = db.relationship('Rating', back_populates='review')
    user = db.relationship('User', back_populates='reviews')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='reviewed_ratings')

class Announcement(db.Model):
    announcement_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    announcement_text = db.Column(db.Text)
    announcement_date = db.Column(db.DateTime)

    user = db.relationship('User', backref='announcements')
    ride = db.relationship('Ride', backref='announcements')