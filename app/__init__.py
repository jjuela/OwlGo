from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
import os
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:beholders_db08@35.185.60.149/beholdersDB'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# CSRF Protection
csrf = CSRFProtect(app)

# Login Configuration
login = LoginManager(app)
login.login_view = 'landing'

# Secret Key Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Upload Folder Configuration
app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

# Mail Configuration
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_APP_PASSWORD = os.environ.get('MAIL_APP_PASSWORD')
MAIL_SENDER_NAME = os.environ.get('MAIL_SENDER_NAME')

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_TLS=False,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_APP_PASSWORD,
    MAIL_DEFAULT_SENDER=(MAIL_SENDER_NAME, MAIL_USERNAME),
    ADMINS=[MAIL_USERNAME]
)

# Initialize Flask-Mail, Flask-Moment, and Flask-Bootstrap
mail = Mail(app)
moment = Moment(app)
bootstrap = Bootstrap(app)

# Create database tables within the application context
with app.app_context():
    db.create_all()

# Import routes
from app import routes

if __name__ == '__main__':
    app.run()
