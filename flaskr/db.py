from pymongo import MongoClient 
from flask_pymongo import PyMongo

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        client = MongoClient(current_app.config['MONGO_URI'])
        g.db = client[current_app.config['MONGO_DBNAME']]
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.client.close()