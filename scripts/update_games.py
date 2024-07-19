import yaml
import requests
import os
import json
import csv

from igdb.wrapper import IGDBWrapper
from bs4 import BeautifulSoup


class Game:
    def __init__(self, name: str, id: str, url: str, category: str):
        self.name = name
        self.id = id
        self.url = url
        self.category = category


    def slug_name(self) -> str:
        return (self.name.lower().
                replace(' ', '-').replace(':', '').replace('!', '').replace('?', '').
                replace('’', '').replace('®', '').replace('™', '').replace('"', '').
                replace('*', '').replace('/', '-').replace('\\', '-').replace('.', '')) + '_' + self.id


    def to_dict(self) -> dict[str, str]:
        return { 'name': self.name, 'id': self.id, 'url': self.url, 'slug': self.slug_name() }


def get_igdb_connection() -> IGDBWrapper:
    twitch_client_id = None
    twitch_client_secret = None

    with open('twitch_creds.yml') as file:
        secret_data = yaml.load(file, Loader=yaml.FullLoader)
        twitch_client_id = secret_data['clientID']
        twitch_client_secret = secret_data['secret']

    resp = requests.post(f'https://id.twitch.tv/oauth2/token?client_id={twitch_client_id}'
                         + f'&client_secret={twitch_client_secret}&grant_type=client_credentials')
    token = resp.json()['access_token']                     

    return IGDBWrapper(twitch_client_id, token)


def is_valid_game(game: Game) -> bool:
    return not 'duplicate' in game.name.lower()


def fetch_game_cover(igdb_conn: IGDBWrapper, game: Game):
    # Check if image already exists
    image_path = f'assets/images/games/{game.slug_name()}.jpg'
    if os.path.exists(image_path):
        print(f'Image for "{game.name}" already exists at {image_path}')
        return

    print(f'Fetching image for {game.name}({game.id}) from {game.url} to {image_path}...')
    
    resp = igdb_conn.api_request(
        'covers',
        f'fields url, game, width, height, image_id; where game={game.id};',
    )

    resp = json.loads(resp.decode('utf-8'))[0]
    cover_url = "https:" + resp['url'].replace('t_thumb', 't_cover_big')

    image_response = requests.get(cover_url)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    
    with open(image_path, 'wb') as image_file:
        image_file.write(image_response.content)

    print(f'Downloaded {image_path}')


def get_games_list():
    all_games = []

    with open('played.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None) # Skip header
        
        for row in reader:
            if len(row) <= 1:
                continue

            game = Game(row[1], row[0], row[2], row[4])
            if not is_valid_game(game):
                continue

            all_games.append(game)

    all_games.sort(key=lambda x: x.slug_name())

    return all_games


def fetch_game_covers():
    igdb_conn = get_igdb_connection()

    for game in get_games_list():
        fetch_game_cover(igdb_conn, game)


def generate_games_data_yaml():
    games = get_games_list()
    games = [game.to_dict() for game in games]

    with open('_data/games.yml', 'w') as file:
        yaml.dump(games, file)
     

if __name__ == '__main__':
    generate_games_data_yaml()
    fetch_game_covers()
