from flask import render_template, url_for, flash, redirect, request, Response
from flaskproject import app, bcrypt, db
from flaskproject.forms import LoginForm, RegistrationForm, BookingForm, EditProfileForm
from flaskproject.models import User, Visit, Doctor
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import random, json
from flask import request, jsonify, session
import sys

reservedHoursArray = []

@app.route("/")
def home():
    return render_template('home.html', title="Przychodnia.pl")


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
		flash('Twoje konto zostało utworzone pomyślnie!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title="Rejestracja", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def account():
	date = datetime.now().strftime("%Y-%m-%d")
	bookedVisits = Visit.query.filter(Visit.bookerId==current_user.id, Visit.date > date).all()
	visitsHistory = Visit.query.filter(Visit.bookerId==current_user.id, Visit.date < date).all()
	doctor = Doctor.query.filter(Doctor.id==Visit.doctorId).all()
	return render_template('profile.html', title='Profil użytkownika', bookedVisits=bookedVisits, visitsHistory=visitsHistory, doctor=doctor)


@app.route("/book", methods=["GET", "POST"])
def book():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	form = BookingForm()
	if request.method=='POST':
		if 'sb_button' in request.form:
			session['choosenDoctor'] = form.doctor.data
			return redirect(url_for('hours'))
	return render_template('book.html', title='Rezerwacja wizyty', form=form)


@app.route("/hours", methods=["GET", "POST"])
def hours():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	choosenDate = session.get('choosenDate', None)
	choosenDoctor = session.get('choosenDoctor', None)
	my_var = session.get('my_var', None)
	if request.method=='POST':
		if 'submit_button' in request.form:
			user_answer=request.form['choosenHour']
			visit = Visit(bookerId=current_user.id, doctorId=choosenDoctor, date=str(choosenDate), startTime=str(user_answer)+":00:00")
			db.session.add(visit)
			db.session.commit()
			flash('Twoja wizyta została zarezerwowana pomyślnie!', 'success')
			return redirect(url_for('home'))
	return render_template('hours.html', title='Wybór godziny rezerwacji', choosenDate=choosenDate, choosenDoctor=choosenDoctor, my_var=my_var)



@app.route('/receiver', methods = ["POST"])
def worker():
	data = request.get_json()
	value = data.get('data')
	reservedHours = Visit.query.filter(Visit.date==value).all()
	reservedHoursArray.clear()
	for element in reservedHours:
		reservedHoursArray.append(element.startTime[0:2])
	reservedHoursArray.sort()
	session['my_var'] = reservedHoursArray
	session['choosenDate'] = value
	return  value



@app.route("/edit_profile", methods=["GET", "POST"])
def editProfile():
	data = User.query.filter(User.id==current_user.id).first()
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	form = EditProfileForm()
	if form.validate_on_submit():
		data.name=form.name.data
		data.surname=form.surname.data
		data.email=form.email.data
		data.phoneNumber=form.phoneNumber.data
		db.session.commit()
		flash(u'Dane zostały zaktualizowane!', 'success')
	return render_template('edit_profile.html', title='Edycja profilu', form=form, data=data)

	