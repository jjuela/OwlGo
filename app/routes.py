from app.models import User, Profile, Ride, RidePassenger, Message, Rating, Review, Post, Announcement

@app.route('/') # landing
# user registration and log in

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
