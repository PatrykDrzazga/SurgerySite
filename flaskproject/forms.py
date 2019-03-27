from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import datetime
from flaskproject.models import User, Doctor, Visit
from wtforms.fields.html5 import TimeField


class RegistrationForm(FlaskForm):
	name = StringField("Imię", validators=[DataRequired(), Length(min=2, max=25)])
	surname = StringField("Nazwisko", validators=[DataRequired(), Length(min=2, max=35)])
	email = StringField("Email", validators=[DataRequired(), Email()])
	password = PasswordField("Hasło", validators=[DataRequired()])
	confirm_password = PasswordField("Potwierdź hasło", validators=[DataRequired(), EqualTo("password")])
	phoneNumber = IntegerField("Numer telefonu", validators=[DataRequired()])
	submit = SubmitField("Załóż konto")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Podany adres email jest już zajęty!')




class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired()])
	password = PasswordField("Hasło", validators=[DataRequired()])
	submit = SubmitField("Zaloguj")

class DoctorChoiceIter(object):
	def __iter__(self):
		doctors = Doctor.query.all()
		choice = [(doctor.id, doctor.name) for doctor in doctors]
		for element in choice:
			yield element



class BookingForm(FlaskForm):
	doctor=SelectField('Wybierz lekarza',coerce=int,choices=DoctorChoiceIter())
	date=DateField('Wybierz date', format="%m/%d/%Y")
	time=TimeField('Wybierz godzine')
	submit=SubmitField('Zarezerwuj')

class EditProfileForm(FlaskForm):
	name = StringField("Imię",validators=[DataRequired()])
	surname = StringField("Nazwisko", validators=[DataRequired()])
	email = StringField("Email", validators=[DataRequired(), Email()])
	phoneNumber = IntegerField("Numer telefonu", validators=[DataRequired()])
	submit = SubmitField("Edytuj dane")
	
	

