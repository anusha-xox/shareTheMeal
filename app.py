from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file, session,jsonify,render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, TextAreaField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField
from form_data import *
from werkzeug.security import check_password_hash
import streamlit.components.v1 as components
import requests
import subprocess


import streamlit as st
import requests
import pandas as pd
import numpy as np

from statsmodels.tsa.arima.model import ARIMA

from datetime import datetime

from pmdarima import auto_arima

STREAMLIT_APP_URL = "http://127.0.0.1:5000/"
app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/shareTheMeal.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'shareTheMeal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)

global arima_model_1

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("about.html")


@app.route('/ngo_form', methods=['GET', 'POST'])
def ngo_form():
    form = NGOForm()

    if form.validate_on_submit():
        # Save the form data to the database or any other storage mechanism
        # You can access the form data using form.field_name.data
        # For simplicity, we'll just store the data in a dictionary here
        ngo_data = {
            'picture': form.picture.data,
            'name': form.name.data,
            'location': form.location.data,
            'full_address': form.full_address.data,
            'contact_details': form.contact_details.data,
            'capacity': form.capacity.data,
            'age': form.age.data
        }

        # Redirect to the profile page, passing the NGO data as a query parameter
        return redirect(url_for('ngo_profile', **ngo_data))

    return render_template('ngo_form.html', form=form)


@app.route('/', methods=['GET', 'POST'])
def ngo_profile():
    ngo_data = {
        'picture': request.args.get('picture'),
        'name': request.args.get('name'),
        'location': request.args.get('location'),
        'full_address': request.args.get('full_address'),
        'contact_details': request.args.get('contact_details'),
        'capacity': request.args.get('capacity'),
        'age': request.args.get('age')
    }

    return render_template('ngo_profile.html', ngo_data=ngo_data)


@app.route('/restaurant_form', methods=['GET', 'POST'])
def restaurant_form():
    if request.method == 'POST':
        # Retrieve form data
        restaurant_name = request.form['restaurant_name']
        location = request.form['location']
        food_type = request.form['food_type']

        # Store the data in session for later retrieval
        session['restaurant_name'] = restaurant_name
        session['location'] = location
        session['food_type'] = food_type

        return redirect(url_for('restaurant_profile'))

    return render_template('restaurant_form.html')


@app.route('/profile')
def restaurant_profile():
    restaurant_name = session.get('restaurant_name')
    location = session.get('location')
    food_type = session.get('food_type')

    return render_template('restaurant_profile.html', restaurant_name=restaurant_name, location=location,
                           food_type=food_type)


@app.route('/postrequestindex')
def postrequestindex():
    requests = FoodRequest.query.filter_by(restaurant_id=None).all()
    restaurants = Restaurant.query.all()
    ngo_offers = {}
    for request in requests:
        ngo_offers[request] = Restaurant.query.filter(Restaurant.offers.any(id=request.id)).all()
    return render_template('postrequestindex.html', requests=requests, ngo_offers=ngo_offers, restaurants=restaurants)


@app.route('/create_request', methods=['GET', 'POST'])
def create_request():
    if request.method == 'POST':
        people_to_feed = request.form['people_to_feed']
        date = request.form['date']
        food_type = request.form['food_type']

        new_request = FoodRequest(people_to_feed=people_to_feed, date=date, food_type=food_type)
        db.session.add(new_request)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('create_request.html')

@app.route('/offer_help/<int:request_id>')
def offer_help(request_id):
    request = FoodRequest.query.get(request_id)
    request.restaurant_id = 1  # Assuming the restaurant ID is 1 for demonstration purposes
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/choose_restaurant/<int:request_id>/<int:restaurant_id>')
def choose_restaurant(request_id, restaurant_id):
    request = FoodRequest.query.get(request_id)
    request.restaurant_id = restaurant_id
    db.session.commit()

    return redirect(url_for('home'))

@app.route('/login')
def loginnew():
    return render_template('login_register.html', title='Login')

@app.route('/loginpage', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data

        if user_type == 'ngo':
            user = NGOregistration.query.filter_by(email=email).first()
        elif user_type == 'restaurant':
            user = Restaurantregistration.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # User is authenticated, perform login
            return 'Login Successful'

        # Invalid credentials
        return 'Invalid email or password'

    return render_template('loginpage.html', form=form)

@app.route('/registerpage', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        phone_number = form.phone_number.data
        city = form.city.data
        district = form.district.data
        email = form.email.data
        password = form.password.data
        user_type = form.user_type.data

        if user_type == 'ngo':
            ngo = NGOregistration(name=name, phone_number=phone_number, city=city, district=district, email=email,
                                  password=password)
            db.session.add(ngo)
            db.session.commit()
        elif user_type == 'restaurant':
            restaurant = Restaurantregistration(name=name, phone_number=phone_number, city=city, district=district,
                                                email=email, password=password)
            db.session.add(restaurant)
            db.session.commit()

        return 'Registration Successful'

    return render_template('registerpage.html', form=form)


class NGO(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class FoodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    people_to_feed = db.Column(db.Integer)
    date = db.Column(db.String(20))
    food_type = db.Column(db.String(10))
    ngo_id = db.Column(db.Integer, db.ForeignKey('ngo.id'))
    ngo = db.relationship('NGO', backref=db.backref('requests', lazy=True))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'))
    restaurant = db.relationship('Restaurant', backref=db.backref('offers', lazy=True))

class NGOregistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Restaurantregistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    district = StringField('District', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('ngo', 'NGO'), ('restaurant', 'Restaurant')])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=[('ngo', 'NGO'), ('restaurant', 'Restaurant')])

def train_model():
    global arima_model_1
    # Assuming you have already trained your ARIMA model and named it 'arima_model'
    df_new = pd.read_csv('updated_food_data.csv', parse_dates=['Date'])
    df_new['Date'] = pd.to_datetime(df_new['Date'])
    df_new.set_index('Date',inplace = True)
    df_new_hotel_1 = df_new[df_new['Hotel'] == 'hotel-1']
    df_new_hotel_2 = df_new[df_new['Hotel'] == 'hotel-2']

    weekly_data_hotel_1 = df_new_hotel_1.groupby(['Date']).sum()
    weekly_data_hotel_2 = df_new_hotel_2.groupby(['Date']).sum()

    weekly_data_hotel_1 = pd.DataFrame({'Wastage Food Amount' : weekly_data_hotel_1['Wastage Food Amount'],
                                'Day of Week' : weekly_data_hotel_1.index.day_name()})
    weekly_data_hotel_2 = pd.DataFrame({'Wastage Food Amount' : weekly_data_hotel_2['Wastage Food Amount'],
                                'Day of Week' : weekly_data_hotel_2.index.day_name()})

    weekly_data_hotel_1_ts = weekly_data_hotel_1.drop(['Day of Week'],axis = 1)
    weekly_data_hotel_2_ts = weekly_data_hotel_2.drop(['Day of Week'],axis = 1)

    train_ds_hotel_1 = weekly_data_hotel_1_ts.iloc[:-25]
    test_ds_hotel_1 = weekly_data_hotel_1_ts.iloc[-25:]
    train_ds_hotel_2 = weekly_data_hotel_2_ts.iloc[:-25]
    test_ds_hotel_2 = weekly_data_hotel_2_ts.iloc[-25:]
    y_train_hotel_1 = weekly_data_hotel_1.iloc[:-25]['Wastage Food Amount']
    y_test_hotel_1 = weekly_data_hotel_1.iloc[-25:]['Wastage Food Amount']
    y_train_hotel_2 = weekly_data_hotel_2.iloc[:-25]['Wastage Food Amount']
    y_test_hotel_2 = weekly_data_hotel_2.iloc[-25:]['Wastage Food Amount']
    
    model_hotel_1 = ARIMA(train_ds_hotel_1['Wastage Food Amount'],order = (1,0,3))
    model_hotel_2 = ARIMA(train_ds_hotel_2['Wastage Food Amount'],order = (0,0,1))
    arima_model_1 = model_hotel_1.fit()
    arima_model_2 = model_hotel_2.fit()
    return arima_model_1,arima_model_2

@app.route('/train_arima', methods=['GET', 'POST'])
def train_arima():
    global arima_model_1, arima_model_2
    if(request.method == 'GET'):
        arima_model_1, arima_model_2 = train_model()
    else:
        return jsonify({'message': 'ARIMA model already trained'})

arima_model_1, arima_model_2 = train_model()

@app.route('/predict_wastage_food',methods = ['POST'])
def predict_wastage_food():
    global arima_model_1, arima_model_2
    choice = request.form['selected_hotel']
    start_date = datetime.strptime(request.form['date_start_input'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['date_end_input'], '%Y-%m-%d').date()
    print(start_date)
    # Create a pandas Series with the input date as the index
    index_future_dates = pd.date_range(start = start_date, end = end_date)
    # Predict using the ARIMA model
    if arima_model_1 and choice == 'Hotel-1':
        prediction_hotel_1 = arima_model_1.predict(start=start_date, end=end_date).rename('Wastage Food Amount Predictions')
        json_prediction_hotel_1 = prediction_hotel_1.to_json(orient='records')
        return jsonify({'prediction_hotel_1' : json_prediction_hotel_1})
    
    elif arima_model_2 and choice == 'Hotel-2':
        prediction_hotel_2 = arima_model_2.predict(start=start_date, end=end_date).rename('Wastage Food Amount Predictions')
        json_prediction_hotel_2 = prediction_hotel_2.to_json(orient='records')
        return jsonify({'prediction_hotel_2' : json_prediction_hotel_2})
    
    else:
        return jsonify({'message': 'Please choose an appropriate option'})
    
    
    
@app.route('/run_streamlit')
def run_streamlit():
    # Start the Streamlit app using subprocess
    streamlit_script_path = 'streamlit_app.py'
    subprocess.Popen(['streamlit', 'run', streamlit_script_path])
    return render_template('about.html')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, TextAreaField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField
from form_data import *
from werkzeug.security import check_password_hash

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'instance', 'shareTheMeal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


class RestaurantReg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    res_name = db.Column(db.String(1000))
    phone_number = db.Column(db.String(100))
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


class NGOReg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ngo_name = db.Column(db.String(1000))
    phone_number = db.Column(db.String(100))
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))


class FoodReqTab(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    no_of_people = db.Column(db.String(1000))
    delivery_date = db.Column(db.String(100))
    food_type = db.Column(db.String(100))
    ngo_id = db.Column(db.String(100))
    restaurant_id = db.Column(db.String(100))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("about.html")


@app.route('/login-buttons')
def loginnew():
    return render_template('login-register-buttons.html', title='Login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        phone_number = form.phone_number.data
        city = form.city.data
        district = form.district.data
        email = form.email.data
        password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        user_type = form.user_type.data
        if user_type == 'ngo':
            ngo = NGOReg(ngo_name=name, phone_number=phone_number, city=city, district=district, email=email,
                         password=password)
            db.session.add(ngo)
            db.session.commit()
        elif user_type == 'restaurant':
            restaurant = RestaurantReg(res_name=name, phone_number=phone_number, city=city, district=district,
                                       email=email, password=password)
            db.session.add(restaurant)
            db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        usertype = form.user_type.data
        if usertype == "ngo":
            user = NGOReg.query.filter_by(email=email).first()
        else:
            user = RestaurantReg.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            if check_password_hash(user.password, password):
                # login_user(user)
                if usertype == "ngo":
                    for ngo in NGOReg.query.all():
                        if user.email == ngo.email:
                            return redirect(url_for("ngo_dashboard"))
                else:
                    for res in RestaurantReg.query.all():
                        if user.email == res.email:
                            return redirect(url_for("restaurant_dashboard"))
    return render_template('login.html', form=form, title_given="Login")


@app.route("/ngo_dashboard")
def ngo_dashboard():
    return render_template("ngo_dashboard.html")

@app.route("/restaurant_dashboard")
def restaurant_dashboard():
    return render_template("restaurant_dashboard.html")


@app.route('/ngo_form', methods=['GET', 'POST'])
def ngo_form():
    form = NGOForm()
    if form.validate_on_submit():
        ngo_data = {
            'picture': form.picture.data,
            'name': form.name.data,
            'location': form.location.data,
            'full_address': form.full_address.data,
            'contact_details': form.contact_details.data,
            'capacity': form.capacity.data,
            'age': form.age.data
        }
        return redirect(url_for('ngo_profile', **ngo_data))
    return render_template('ngo_form.html', form=form)


@app.route('/ngo-profile', methods=['GET', 'POST'])
def ngo_profile():
    ngo_data = {
        'picture': request.args.get('picture'),
        'name': request.args.get('name'),
        'location': request.args.get('location'),
        'full_address': request.args.get('full_address'),
        'contact_details': request.args.get('contact_details'),
        'capacity': request.args.get('capacity'),
        'age': request.args.get('age')
    }
    return render_template('ngo_profile.html', ngo_data=ngo_data)


@app.route('/restaurant_form', methods=['GET', 'POST'])
def restaurant_form():
    if request.method == 'POST':
        # Retrieve form data
        restaurant_name = request.form['restaurant_name']
        location = request.form['location']
        food_type = request.form['food_type']
        # Store the data in session for later retrieval
        session['restaurant_name'] = restaurant_name
        session['location'] = location
        session['food_type'] = food_type
        return redirect(url_for('restaurant_profile'))
    return render_template('restaurant_form.html')


@app.route('/profile')
def restaurant_profile():
    restaurant_name = session.get('restaurant_name')
    location = session.get('location')
    food_type = session.get('food_type')
    return render_template('restaurant_profile.html', restaurant_name=restaurant_name, location=location,
                           food_type=food_type)


@app.route('/postrequestindex')
def postrequestindex():
    requests = FoodRequest.query.filter_by(restaurant_id=None).all()
    restaurants = Restaurant.query.all()
    ngo_offers = {}
    for request in requests:
        ngo_offers[request] = Restaurant.query.filter(Restaurant.offers.any(id=request.id)).all()
    return render_template('postrequestindex.html', requests=requests, ngo_offers=ngo_offers, restaurants=restaurants)


@app.route('/create_request', methods=['GET', 'POST'])
def create_request():
    if request.method == 'POST':
        people_to_feed = request.form['people_to_feed']
        date = request.form['date']
        food_type = request.form['food_type']
        new_request = FoodRequest(people_to_feed=people_to_feed, date=date, food_type=food_type)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('create_request.html')


@app.route('/offer_help/<int:request_id>')
def offer_help(request_id):
    request = FoodRequest.query.get(request_id)
    request.restaurant_id = 1  # Assuming the restaurant ID is 1 for demonstration purposes
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/choose_restaurant/<int:request_id>/<int:restaurant_id>')
def choose_restaurant(request_id, restaurant_id):
    request = FoodRequest.query.get(request_id)
    request.restaurant_id = restaurant_id
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True)
