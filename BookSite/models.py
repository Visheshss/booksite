from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	__tablename_ = "users"
	id = db.Column(db.Integer, primary_key=True) 
	name = db.Column(db.String, nullable=False) 
	password = db.Column(db.String, nullable=False) 