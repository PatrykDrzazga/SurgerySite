from flaskproject import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(25), nullable=False)
	surname = db.Column(db.String(35), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	phoneNumber = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"User('{self.email}', '{self.name}', '{self.surname}')"


class Visit(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
	bookerId = db.Column(db.Integer, db.ForeignKey('user.id'))
	doctorId = db.Column(db.Integer, db.ForeignKey('doctor.id')) 
	date = db.Column(db.DateTime, nullable=False)
	startTime = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"Visit('{self.id}', '{self.date}', '{self.startTime}')"


class Doctor(db.Model):
	id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
	name = db.Column(db.String(25), nullable=False)
	surname = db.Column(db.String(35), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	phoneNumber = db.Column(db.Integer, nullable=False)



