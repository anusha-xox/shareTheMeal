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
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/shareTheMeal.db'
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




with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
