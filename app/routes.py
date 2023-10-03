from flask import render_template, request
from app import app
from app.forms import PokemonForm
from app.utils import fetch_pokemon_info

user_pokemon_data = {}  # Your in-memory database

@app.route('/')
def home():
    return render_template('index.html')

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
