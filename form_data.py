from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length, URL
from flask_bootstrap import Bootstrap
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from wtforms.validators import ValidationError
from flask_ckeditor import CKEditor, CKEditorField


class NGOForm(FlaskForm):
    picture = FileField('Picture')
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    full_address = TextAreaField('Full Address', validators=[DataRequired()])
    contact_details = StringField('Contact Details', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    submit = SubmitField('Submit')
