from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os

app = Flask(__name__)

login = LoginManager(app)
login.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:beholders_db08@35.185.60.149/beholdersDB'
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

app.config['UPLOAD_FOLDER'] = 'app/static/uploads'

from app import routes
