from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, Email
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import email_validator
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor, CKEditorField

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///iseResearch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
ckeditor = CKEditor(app)

db = SQLAlchemy(app)

bootstrap = Bootstrap(app)


# login_manager = LoginManager()
# login_manager.init_app(app)
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
@app.route('/')
def home():
    return render_template("about.html")


if __name__ == '__main__':
    app.run()
