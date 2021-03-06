from flask import render_template, url_for, flash, redirect, request, Response
from flaskproject import app, bcrypt, db
from flaskproject.forms import LoginForm, RegistrationForm, BookingForm, EditProfileForm, VisitForm
from flaskproject.models import User, Visit, Doctor
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime
import random, json
from flask import request, jsonify, session
import sys
from sqlalchemy import desc

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
	if current_user.isDoctor()==True:
		return redirect(url_for('doctor'))
	date = datetime.now().strftime("%Y-%m-%d")
	bookedVisits = Visit.query.filter(Visit.bookerId==current_user.id, Visit.date >= date).all()
	visitsHistory = Visit.query.filter(Visit.bookerId==current_user.id, Visit.date < date).all()
	doctor = User.query.filter(User.userType=='doctor', User.id==Visit.doctorId).all()
	return render_template('profile.html', title='Profil pacjenta', bookedVisits=bookedVisits, visitsHistory=visitsHistory, doctor=doctor)


@app.route("/book", methods=["GET", "POST"])
def book():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="user":
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

@app.route("/profile/visits", methods=["GET", "POST"])
def profileVisits():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="user":
		return redirect(url_for('home'))
	date = datetime.now().strftime("%Y-%m-%d")
	visitsHistory = Visit.query.filter(Visit.bookerId==current_user.id, Visit.date < date).all()
	doctor = User.query.filter(User.userType=='doctor', User.id==Visit.doctorId).all()
	return render_template('profilevisits.html', title='Historia wizyt', visitsHistory=visitsHistory, doctor=doctor)

@app.route("/profile/visits/<int:id>", methods=["GET", "POST"])
def profileVisitsDetails(id):
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="user":
		return redirect(url_for('home'))
	visit = Visit.query.filter(Visit.id==id).all()
	doctor = User.query.filter(User.id==visit[0].doctorId).all()
	return render_template('details.html', title='Szczegóły wizyty', visit=visit, doctor=doctor, id=id)

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="doctor":
		return redirect(url_for('home'))
	date = datetime.now().strftime("%Y-%m-%d")
	patient = []
	bookedVisits = Visit.query.filter(Visit.doctorId==current_user.id, Visit.date==date).all()
	for i in bookedVisits:
		patient.append(User.query.filter(i.bookerId==User.id).all())
	return render_template('doctor.html', title='Panel doktora', date=date, bookedVisits=bookedVisits, patient=patient)


@app.route("/doctor/visits", methods=["GET", "POST"])
def doctorVisits():
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="doctor":
		return redirect(url_for('home'))
	patient = []
	bookedVisits = Visit.query.filter(Visit.doctorId==current_user.id).order_by(desc(Visit.date)).all()
	for i in bookedVisits:
		patient.append(User.query.filter(i.bookerId==User.id).all())
	return render_template('doctorvisits.html', title='Wszystkie wizyty', bookedVisits=bookedVisits, patient=patient)

@app.route("/doctor/visits/<int:id>", methods=["GET", "POST"])
def doctorVisitsDetails(id):
	if current_user.is_authenticated==False:
		return redirect(url_for('home'))
	if current_user.userType!="doctor":
		return redirect(url_for('home'))
	form = VisitForm()
	visit = Visit.query.filter(Visit.id==id).all()
	patient = User.query.filter(User.id==visit[0].bookerId).all()
	form.diganosis.data = visit[0].diganosis
	form.recommendations.data = visit[0].recommendations
	if form.validate_on_submit():
		print(form.diganosis.data)
		visit[0].diganosis= request.form.get('diganosis')
		visit[0].recommendations=request.form.get('recommendations')
		db.session.commit()
		flash(u'Dane wizyty zostały zaktualizowane pomyślnie!', 'success')
		return redirect(url_for('doctorVisits'))
	return render_template('doctorvisitsdetails.html', title='Szczegóły wizyty', visit=visit, patient=patient, id=id, form=form)




	