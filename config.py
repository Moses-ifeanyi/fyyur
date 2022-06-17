from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect
import os
SECRET_KEY = os.urandom(32)


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)

csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:abc@localhost:5432/fyyur'

SQLALCHEMY_TRACK_MODIFICATIONS = False