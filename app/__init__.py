from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import routes

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:beholders_db08@35.185.60.149/beholdersDB'
# m0e]`;PT\h**~$C$
db = SQLAlchemy(app)

# Define a simple model (table) for testing
class TestModel(db.Model):
    __tablename__ = 'test_table'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(255))

@app.route('/test_database')
def test_database():
    try:
        # Try to query the test table
        result = TestModel.query.first()
        if result:
            return f"Connection to the database was successful. Retrieved data: {result.data}"
        else:
            return "No data found in the test table."
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)

