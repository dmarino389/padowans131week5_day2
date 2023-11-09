# app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Create the SQLAlchemy instance without passing the app
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    pokemon_collection = db.relationship('UserPokemon', backref='user', lazy=True)
    wins = db.Column(db.Integer, default =0)
    losses = db.Column(db.Integer, default =0)

    def add_win(self):
        self.wins +=1
        db.session.commit()
        

    def add_loss(self):
        self.losses +=1
        db.session.commit()

    @property
    def user_pokemon(self):
        return [Pokemon.query.get(user_pokemon.pokemon_id) for user_pokemon in self.pokemon_collection]


class Pokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    hp = db.Column(db.Integer, nullable=True)
    attack = db.Column(db.Integer, nullable=False)
    defense = db.Column(db.Integer, nullable=False)
    sprite = db.Column(db.String(500), nullable=True)  # Assuming sprite is a URL, so the String length is set to 500.
    abilities = db.Column(db.String(255), nullable=True)  # Storing abilities as comma-separated values.

    
    # ... other columns ...

class UserPokemon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pokemon_id = db.Column(db.Integer, db.ForeignKey('pokemon.id'), nullable=False)
    pokemon = db.relationship('Pokemon', backref = 'user_pokemon', lazy = True)