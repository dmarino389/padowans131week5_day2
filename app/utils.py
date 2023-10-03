import requests

def fetch_pokemon_info(pokemon_name):
    # Placeholder URL for the actual PokeAPI call: https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}'

    response = requests.get(url.lower())
    
    if response.ok:
        data = response.json()
        pokemon_info = {
            'name': data['name'],
            'hp': data['stats'][0]['base_stat'],
            'attack': data['stats'][1]['base_stat'],
            'defense': data['stats'][2]['base_stat'],
            'sprite': data['sprites']['front_default'],
            'abilities': [data['abilities'][0]['ability']['name'], data['abilities'][1]['ability']['name']]
            

        }

        return pokemon_info
    else:
        return None



    
