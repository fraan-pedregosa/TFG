import pymongo
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_users_db():
    if 'users_db' not in g:
        client = pymongo.MongoClient(current_app.config['MONGO_URI'])
        db = client[current_app.config['MONGO_DB']]
        g.users_db = db['users_collection']

    return g.users_db

def get_sound_db():
    if 'sound_db' not in g:
        client = pymongo.MongoClient(current_app.config['MONGO_URI'])
        db = client[current_app.config['MONGO_DB']]
        g.sound_db = db['sound_collection']
    return g.sound_db