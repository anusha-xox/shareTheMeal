from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, URL
from flask_wtf.file import FileField, FileRequired, FileAllowed

REG_CATEGORY = ["ngo", "restaurant"]


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    district = StringField('District', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=REG_CATEGORY, validators=[DataRequired()])
    submit = SubmitField(label='Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField('User Type', choices=REG_CATEGORY, validators=[DataRequired()])
    submit = SubmitField(label='Login')


class NGOForm(FlaskForm):
    picture = FileField('Picture')
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    full_address = TextAreaField('Full Address', validators=[DataRequired()])
    contact_details = StringField('Contact Details', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    est_year = IntegerField('Year of Est.', validators=[DataRequired()])
    submit = SubmitField('Submit')
