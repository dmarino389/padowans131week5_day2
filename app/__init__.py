from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from .models import db, User
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from . import routes


