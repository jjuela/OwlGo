from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:beholders_db08@35.185.60.149/beholdersDB'
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run(debug=True)
