from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flaskproject.models import User


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


