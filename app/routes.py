from flask import render_template, request, flash, redirect, url_for
import jinja2
from app import app, db
from app.forms import PokemonForm, RegistrationForm, LoginForm
from app.utils import fetch_pokemon_info
from app.models import User, Pokemon, UserPokemon
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash


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

# ... (other parts of your code remain unchanged)

from sqlalchemy.exc import IntegrityError

@app.route('/pokemon-form', methods=['GET', 'POST'])
@login_required
def pokemon_form():
    form = PokemonForm()

    if form.validate_on_submit():
        pokemon_name = form.pokemon_name.data.lower()
        pokemon_info = fetch_pokemon_info(pokemon_name)

        if pokemon_info is None:
            flash('Failed to fetch Pokemon information.', 'danger')
            return render_template('pokemon_form.html', form=form)

        Name = pokemon_info['name']
        Hp = pokemon_info['hp']
        Defense = pokemon_info['defense']
        Attack = pokemon_info['attack']
        Abilities = pokemon_info['abilities']

        existing_pokemon = Pokemon.query.filter_by(name=pokemon_name).first()

        # Only try to add a new pokemon if it does not already exist.
        if not existing_pokemon:
            new_pokemon = Pokemon(name=Name, hp=Hp, attack=Attack, defense=Defense, abilities=Abilities)
            try:
                db.session.add(new_pokemon)
                db.session.commit()
                existing_pokemon = new_pokemon
            except IntegrityError:
                db.session.rollback()
                flash('Pokemon already exists.', 'info')
                existing_pokemon = Pokemon.query.filter_by(name=pokemon_name).first()

        # Handling for when the Pokemon doesn't exist in DB and isn't new either
        if not existing_pokemon:
            flash('Error occurred. Please try again.', 'danger')
            return render_template('pokemon_form.html', form=form)

        user_already_has_pokemon = UserPokemon.query.filter_by(user_id=current_user.id, pokemon_id=existing_pokemon.id).first()
        user_pokemon_count = UserPokemon.query.filter_by(user_id=current_user.id).count()

        if not user_already_has_pokemon and user_pokemon_count < 5:
            new_user_pokemon = UserPokemon(user_id=current_user.id, pokemon_id=existing_pokemon.id)
            db.session.add(new_user_pokemon)
            db.session.commit()
            flash(f'You have successfully added {pokemon_name} to your collection!', 'success')
        elif user_pokemon_count >= 5:
            flash('You can have a maximum of 5 Pokemon. Release one to add another.', 'warning')
        else:
            flash(f'You already have {pokemon_name} in your collection!', 'info')
                
        return render_template('pokemon_form.html', form=form, pokemon_info=pokemon_info)

    return render_template('pokemon_form.html', form=form)


# ... (rest of your code remains unchanged)


@app.route('/release_pokemon/<int:user_pokemon_id>', methods=['POST'])
@login_required
def release_pokemon(user_pokemon_id):
    user_pokemon = UserPokemon.query.get_or_404(user_pokemon_id)
    if user_pokemon.user_id == current_user.id:
        db.session.delete(user_pokemon)
        db.session.commit()
        flash(f'You have successfully removed a Pokemon from your collection!', 'success')
    return redirect(url_for('pokemon_form'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/opponents')
@login_required
def list_opponents():
    # Exclude the current user from the opponents' list
    opponents = User.query.filter(User.id != current_user.id).all()
    return render_template('opponents.html', opponents=opponents)

@app.route('/attack/<int:opponent_id>')
@login_required
def battle(opponent_id):
    opponent = User.query.get_or_404(opponent_id)

    # Gather the stats for each collection
    user_attack = sum(p.attack for p in current_user.user_pokemon)
    user_defense = sum(p.defense for p in current_user.user_pokemon)

    opponent_attack = sum(p.attack for p in opponent.user_pokemon)
    opponent_defense = sum(p.defense for p in opponent.user_pokemon)

    # Simple mechanism for determining winner
    if user_attack - opponent_defense > opponent_attack - user_defense:
        current_user.add_win()
        opponent.add_loss()
        winner = current_user.username
    else:
        current_user.add_loss()
        opponent.add_win() 
        winner = opponent.username

    db.session.commit()

    return render_template('battle_results.html', winner=winner, opponent=opponent)

@app.route('/show_team')
def show_team():
    if current_user.pokemon_collection:
        print(current_user.pokemon_collection[0].user)  # Protected with a check

    my_team = []

    my_pokemon = current_user.pokemon_collection
    for poke in my_pokemon:
        pokemon = Pokemon.query.get(poke.pokemon_id)
        my_team.append(pokemon)

    return render_template('my_team.html', my_team=my_team)


    
@app.errorhandler(jinja2.exceptions.UndefinedError)
def handle_undefined_error(e):
    return "An error occurred while processing your request. Please try again later.", 500


@app.route('/release_by_id/<int:pokemon_id>', methods=['POST'])
@login_required
def release_pokemon_by_id(pokemon_id):  # Function name changed here
    user_pokemon = UserPokemon.query.filter_by(user_id=current_user.id, pokemon_id=pokemon_id).first()
    
    if not user_pokemon:
        flash('You don\'t have this Pokémon in your collection.', 'warning')
        return redirect(url_for('show_team'))

    db.session.delete(user_pokemon)
    db.session.commit()

    flash(f'You have successfully released the Pokémon from your collection.', 'success')
    return redirect(url_for('show_team'))


# @app.route('/attack/<int:opponent_id>', methods=['GET', 'POST'])
# @login_required
# def attack(opponent_id):
#     opponent = User.query.get_or_404(opponent_id)

    # if request.method == 'POST':
    #     user_power = sum(p.attack for p in current_user.user_pokemon) 
    #     opponent_power = sum(p.attack for p in opponent.user_pokemon)

    #     # Basic logic to determine the winner
    #     if user_power > opponent_power:
    #         current_user.wins += 1
    #         opponent.losses += 1
    #         winner = current_user.username
    #     else:
    #         current_user.losses += 1
    #         opponent.wins += 1
    #         winner = opponent.username

    #     db.session.commit()
    #     flash(f'The winner is {winner}!', 'success')
    #     return redirect(url_for('list_opponents'))

    # return render_template('attack.html', opponent=opponent)



