import pymongo
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_users_db():
    if 'users_db' not in g:
        client = pymongo.MongoClient(current_app.config['MONGO_URI'])
        db = client[current_app.config['MONGO_DB']]
        g.users_db = db['users']

    return g.users_db

