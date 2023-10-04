import os

basedir = os.path.abspath(os.path.dirname(__name__))

class Config():
  FLASK_APP = os.environ.get("FLASK_APP")
  FLASK_DEBUG = os.environ.get("FLASK_DEBUG")
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # Use your database URI here
  SQLALCHEMY_TRACK_MODIFICATIONS = False

