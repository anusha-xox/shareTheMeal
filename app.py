from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL, Email, Length
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField
from form_data import *

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iseResearch.db'
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


@app.route('/login', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(debug=True)
