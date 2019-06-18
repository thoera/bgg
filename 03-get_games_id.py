# -*- coding: utf-8 -*-

import boardgamegeek
from collections import namedtuple
from glob import glob
from itertools import zip_longest
import logging
from shutil import copyfileobj

bgg = boardgamegeek.BGGClient()

logging.basicConfig(filename='logs/games_name.log',
                    filemode='w', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def load_collections(file):
    with open(file, mode='r', encoding='utf-8') as f:
        collections = [line.rstrip().split(';') for line in f]
        return {item[0]: item[1].split(',') for item in collections}


def get_name_from_id(game_id):
    GameId = namedtuple('GameId', ['id', 'name'])
    try:
        name = bgg.game(game_id=game_id).name
    except boardgamegeek.BGGApiError:
        name = None
    return GameId(game_id, name)


def get_names_from_id(games_id):
    id_names = []
    for index, game_id in enumerate(games_id, start=1):
        if game_id:
            name = get_name_from_id(game_id)
            id_names.append(name)
            print(f'{name} ({index}/{len(games_id)})')
    return id_names


def write_games_id(games_id, file):
    with open(file, mode='w', encoding='utf-8') as f:
        for game in games_id:
            f.write(f'{game}\n')


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def write_games_name(games_name, file):
    with open(file, mode='w', encoding='utf-8') as f:
        for game in games_name:
            f.write(f'{game.id};{game.name}\n')


def concatenate_games_name(games_name, file):
    with open(file, mode='w', encoding='utf-8') as f:
        for batch in games_name:
            with open(batch, mode='r', encoding='utf-8') as file:
                copyfileobj(file, f)


def load_games_name(file):
    with open(file, mode='r', encoding='utf-8') as f:
        GameId = namedtuple('GameId', ['id', 'name'])
        return [GameId(*line.rstrip().split(';', 1)) for line in f]


collections = load_collections('data/collections.txt')

games = {game for games in collections.values() for game in games}
games = sorted([int(game) for game in games])
write_games_id(games, 'data/games_id.txt')

batches = list(grouper(100, games))

for index, batch in enumerate(batches, start=1):
    print(f'\n---- batch {index}/{len(batches)} ----\n')
    games_name = get_names_from_id(batch)
    write_games_name(games_name, f'data/games_name_{index}.txt')
    logging.info(f'batch {index}/{len(batches)} done')

concatenate_games_name(glob('data/games_name*.txt'), 'data/games_name.txt')

games_name = load_games_name('data/games_name.txt')
games_name = [game for game in games_name if game.name != 'None']
write_games_name(games_name, 'data/games_name.txt')
