# -*- coding: utf-8 -*-

import boardgamegeek
from glob import glob
import logging
from itertools import zip_longest
from shutil import copyfileobj

bgg = boardgamegeek.BGGClient()

logging.basicConfig(filename='logs/collections.log',
                    filemode='w', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def load_usernames(file):
    with open(file, mode='r', encoding='utf-8') as f:
        return [line.rstrip() for line in f]


def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)


def get_collection(username):
    try:
        games = [game.id for game in bgg.collection(user_name=username)]
    except boardgamegeek.BGGItemNotFoundError as e:
        print(f'{e}: {username}')
        games = []
    return games


def get_users_collections(usernames):
    users_collections = {}
    for index, username in enumerate(usernames, start=1):
        print(f'{username} ({index}/{len(usernames)})')
        if username:
            try:
                users_collections[username] = get_collection(username)
            except boardgamegeek.BGGApiError:
                users_collections[username] = None
    return users_collections


def filter_empty_collections(collections):
    return {k: v for k, v in collections.items() if v}


def write_collections(collections, file):
    with open(file, mode='w', encoding='utf-8') as f:
        for user, collection in collections.items():
            f.write(f'{user};{",".join(str(game) for game in collection)}\n')


def concatenate_collections(collections, file):
    with open(file, mode='w', encoding='utf-8') as f:
        for collection in collections:
            with open(collection, mode='r', encoding='utf-8') as file:
                copyfileobj(file, f)


usernames = load_usernames('data/usernames.txt')
batches = list(grouper(100, usernames))

for index, batch in enumerate(batches, start=1):
    print(f'\n---- batch {index}/{len(batches)} ----\n')
    collections = get_users_collections(batch)
    collections = filter_empty_collections(collections)
    write_collections(collections, f'data/collections_{index}.txt')
    logging.info(f'batch {index}/{len(batches)} done')

concatenate_collections(glob('data/collections_*.txt'), 'data/collections.txt')
