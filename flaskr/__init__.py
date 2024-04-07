import os

from flask import Flask
from pymongo import MongoClient 
from flask_pymongo import PyMongo

import click
from flask import current_app, g
from flask.cli import with_appcontext


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
    app.config['MONGO_DB'] = 'sound'
    app.config['MONGO_COLLECTION'] = 'sound_collection'
    app.config['MONGO_COLLECTION_USERS'] = 'users_collection'
    
    mongo = PyMongo(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app
