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
import itertools

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
    ngo_functionalities = ["View/Edit Profile", "Recent Food Availabilities", "View Restaurants Nearby", "Messages"]
    ngo_functionalities_url = ["", "", "", ""]
    ngo_functionalities_pictures = [
        "https://previews.123rf.com/images/microbagrandioza/microbagrandioza1906/microbagrandioza190600055/125932546"
        "-edit-photo-and-information-personal-internet-online-profile-computer-network-concept-vector-flat.jpg",
        "https://modernrestaurantmanagement.com/assets/media/2022/03/Shutterstock_707207614-1200x655.jpg",
        "https://img.freepik.com/premium-vector/cafe-with-tables-umbrellas-with-sea-views-street_136277-690.jpg",
        "https://static.vecteezy.com/system/resources/previews/000/963/033/original/cartoon-business-man-sending"
        "-messages-vector.jpg"]
    dashboard_details = []
    for (a, b, c) in zip(ngo_functionalities, ngo_functionalities_url, ngo_functionalities_pictures):
        dashboard_details.append([a, b, c])
    return render_template(
        "ngo_dashboard.html",
        ngo=ngo,
        dashboard_details=dashboard_details
    )


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
