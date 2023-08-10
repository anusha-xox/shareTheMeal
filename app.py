from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file, session, \
    jsonify
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
from form_data import *
from werkzeug.security import check_password_hash
import itertools

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
    kgs_of_food = db.Column(db.String(100))
    restaurant_id = db.Column(db.String(100))


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String(250), nullable=False)
    author_email = db.Column(db.String(250), nullable=False)
    receiver_email = db.Column(db.String(250), nullable=False)


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
                            return redirect(url_for("ngo_dashboard", ngo_id=ngo.id))
                else:
                    for res in RestaurantReg.query.all():
                        if user.email == res.email:
                            return redirect(url_for("restaurant_dashboard"))
    return render_template('login.html', form=form, title_given="Login")


@app.route("/ngo_dashboard")
def ngo_dashboard():
    ngo_id = int(request.args.get("ngo_id"))
    ngo = NGOReg.query.get(ngo_id)
    author_email = ngo.email
    if ngo_id is None:
        return "ID not found"
    else:
        ngo = NGOReg.query.get(ngo_id)
        ngo_functionalities = ["View/Edit Profile", "Recent Food Availabilities", "View Restaurants Nearby",
                               "View Messages", "Compose Message"]
        ngo_functionalities_url = [
            "",
            "",
            "",
            url_for("view_messages", receiver_email=author_email, receiver_type="ngo", receiver_id=ngo_id),
            url_for("compose", author_email=author_email, author_type="ngo", author_id=ngo_id)]
        ngo_functionalities_pictures = [
            "https://previews.123rf.com/images/microbagrandioza/microbagrandioza1906/microbagrandioza190600055/125932546"
            "-edit-photo-and-information-personal-internet-online-profile-computer-network-concept-vector-flat.jpg",
            "https://modernrestaurantmanagement.com/assets/media/2022/03/Shutterstock_707207614-1200x655.jpg",
            "https://img.freepik.com/premium-vector/cafe-with-tables-umbrellas-with-sea-views-street_136277-690.jpg",
            "https://static.vecteezy.com/system/resources/previews/000/963/033/original/cartoon-business-man-sending"
            "-messages-vector.jpg",
            ""
        ]
        dashboard_details = []
        for (a, b, c) in zip(ngo_functionalities, ngo_functionalities_url, ngo_functionalities_pictures):
            dashboard_details.append([a, b, c])
        return render_template(
            "ngo_dashboard.html",
            ngo=ngo,
            dashboard_details=dashboard_details
        )


@app.route("/compose", methods=["GET", "POST"])
def compose():
    form = MessageForm()
    if form.validate_on_submit():
        subject = form.subject.data
        date = datetime.datetime.now()
        body = form.body.data
        author_email = request.args.get("author_email")
        receiver_email = form.receiver_email.data
        new_message = Messages(subject=subject, date=date, body=body, author_email=author_email,
                               receiver_email=receiver_email)
        db.session.add(new_message)
        db.session.commit()
        if request.args.get("author_type") == "ngo":
            return redirect(url_for('ngo_dashboard', ngo_id=request.args.get("author_id")))
        else:
            return redirect(url_for('restaurant_dashboard'))
    return render_template("compose.html", form=form)


@app.route("/view-messages")
def view_messages():
    receiver_id = int(request.args.get("receiver_id"))
    if request.args.get("receiver_type") == "ngo":
        receiver = NGOReg.query.get(receiver_id)
    else:
        receiver = RestaurantReg.query.get(receiver_id)
    if receiver:
        receiver_email = receiver.email
        sent_messages = Messages.query.filter_by(author_email=receiver_email).all()
        received_messages = Messages.query.filter_by(receiver_email=receiver_email).all()
        display_messages = sent_messages + received_messages
        return render_template("view_messages.html", messages=display_messages)
    return redirect(url_for("home"))


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


def train_model():
    global arima_model_1
    # Assuming you have already trained your ARIMA model and named it 'arima_model'
    df_new = pd.read_csv('updated_food_data.csv', parse_dates=['Date'])
    df_new['Date'] = pd.to_datetime(df_new['Date'])
    df_new.set_index('Date', inplace=True)
    df_new_hotel_1 = df_new[df_new['Hotel'] == 'hotel-1']
    df_new_hotel_2 = df_new[df_new['Hotel'] == 'hotel-2']

    weekly_data_hotel_1 = df_new_hotel_1.groupby(['Date']).sum()
    weekly_data_hotel_2 = df_new_hotel_2.groupby(['Date']).sum()

    weekly_data_hotel_1 = pd.DataFrame({'Wastage Food Amount': weekly_data_hotel_1['Wastage Food Amount'],
                                        'Day of Week': weekly_data_hotel_1.index.day_name()})
    weekly_data_hotel_2 = pd.DataFrame({'Wastage Food Amount': weekly_data_hotel_2['Wastage Food Amount'],
                                        'Day of Week': weekly_data_hotel_2.index.day_name()})

    weekly_data_hotel_1_ts = weekly_data_hotel_1.drop(['Day of Week'], axis=1)
    weekly_data_hotel_2_ts = weekly_data_hotel_2.drop(['Day of Week'], axis=1)

    train_ds_hotel_1 = weekly_data_hotel_1_ts.iloc[:-25]
    test_ds_hotel_1 = weekly_data_hotel_1_ts.iloc[-25:]
    train_ds_hotel_2 = weekly_data_hotel_2_ts.iloc[:-25]
    test_ds_hotel_2 = weekly_data_hotel_2_ts.iloc[-25:]
    y_train_hotel_1 = weekly_data_hotel_1.iloc[:-25]['Wastage Food Amount']
    y_test_hotel_1 = weekly_data_hotel_1.iloc[-25:]['Wastage Food Amount']
    y_train_hotel_2 = weekly_data_hotel_2.iloc[:-25]['Wastage Food Amount']
    y_test_hotel_2 = weekly_data_hotel_2.iloc[-25:]['Wastage Food Amount']

    model_hotel_1 = ARIMA(train_ds_hotel_1['Wastage Food Amount'], order=(1, 0, 3))
    model_hotel_2 = ARIMA(train_ds_hotel_2['Wastage Food Amount'], order=(0, 0, 1))
    arima_model_1 = model_hotel_1.fit()
    arima_model_2 = model_hotel_2.fit()
    return arima_model_1, arima_model_2


@app.route('/train_arima', methods=['GET', 'POST'])
def train_arima():
    global arima_model_1, arima_model_2
    if request.method == 'GET':
        arima_model_1, arima_model_2 = train_model()
    else:
        return jsonify({'message': 'ARIMA model already trained'})


arima_model_1, arima_model_2 = train_model()


@app.route('/predict_wastage_food', methods=['POST'])
def predict_wastage_food():
    global arima_model_1, arima_model_2
    choice = request.form['selected_hotel']
    start_date = datetime.strptime(request.form['date_start_input'], '%Y-%m-%d').date()
    end_date = datetime.strptime(request.form['date_end_input'], '%Y-%m-%d').date()
    print(start_date)
    # Create a pandas Series with the input date as the index
    index_future_dates = pd.date_range(start=start_date, end=end_date)
    # Predict using the ARIMA model
    if arima_model_1 and choice == 'Hotel-1':
        prediction_hotel_1 = arima_model_1.predict(start=start_date, end=end_date).rename(
            'Wastage Food Amount Predictions')
        json_prediction_hotel_1 = prediction_hotel_1.to_json(orient='records')
        return jsonify({'prediction_hotel_1': json_prediction_hotel_1})

    elif arima_model_2 and choice == 'Hotel-2':
        prediction_hotel_2 = arima_model_2.predict(start=start_date, end=end_date).rename(
            'Wastage Food Amount Predictions')
        json_prediction_hotel_2 = prediction_hotel_2.to_json(orient='records')
        return jsonify({'prediction_hotel_2': json_prediction_hotel_2})

    else:
        return jsonify({'message': 'Please choose an appropriate option'})


@app.route('/run_streamlit')
def run_streamlit():
    # Start the Streamlit app using subprocess
    streamlit_script_path = 'streamlit_app.py'
    subprocess.Popen(['streamlit', 'run', streamlit_script_path])
    return render_template('streamlit.html')


if __name__ == '__main__':
    app.run(debug=True)
