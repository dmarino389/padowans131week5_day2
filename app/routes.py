from flask import render_template, request, flash, redirect, url_for
from app import app
from app.forms import PokemonForm, RegistrationForm, LoginForm
from app.utils import fetch_pokemon_info
from app.models import User, db
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


user_pokemon_data = {}  # Your in-memory database

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=False)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/pokemon-form', methods=['GET', 'POST'])
def pokemon_form():
    form = PokemonForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            pokemon_name = form.pokemon_name.data
            pokemon_info = fetch_pokemon_info(pokemon_name)
            print(pokemon_info)
            if pokemon_info is not None:
                user_pokemon_data[pokemon_name] = pokemon_info
                return render_template('pokemon_form.html', form=form, pokemon_info=pokemon_info)
            else:
                error_message = 'Failed to fetch Pokemon information.'
                return render_template('pokemon_form.html', form=form, error_message=error_message)

    return render_template('pokemon_form.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


