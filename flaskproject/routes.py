from flask import render_template, url_for, flash, redirect, request
from flaskproject import app, bcrypt, db
from flaskproject.forms import LoginForm, RegistrationForm
from flaskproject.models import User
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def home():
    return render_template('home.html', title="Strona Główna")


@app.route("/login", methods=["GET", "POST"])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get("next")
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Logowanie niepowiodło się. Sprawdź poprawność wprowadzonych danych', 'danger')
	return render_template('login.html', title="Logowanie", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(name=form.name.data, surname=form.surname.data, email=form.email.data, password=hashed_password, phoneNumber=form.phoneNumber.data)
		db.session.add(user)
		db.session.commit()
		flash('Twoje konto zostało utworzone pomyślnie!', 'succes')
		return redirect(url_for('login'))
	return render_template('register.html', title="Rejestracja", form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def account():
    return render_template('profile.html', title='Profil użytkownika')