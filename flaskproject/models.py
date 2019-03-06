from flaskproject import db, login_manager
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