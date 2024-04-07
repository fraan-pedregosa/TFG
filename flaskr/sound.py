from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_sound_db
from flaskr.db import get_users_db
from flask_pymongo import pymongo
from flaskr.db import get_mongo_db

bp = Blueprint('sound', __name__)

@bp.route('/')
def index():
    sounds = get_sound_db()
    return render_template('sound/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_sound_db()
            # ...

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = 'Title is required.'
        if error is not None:
            flash(error)
        else:
            db = get_mongo_db()
            db.posts.insert_one({
                'title': title,
                'body': body,
                'author_id': g.user['id']
            })
            return redirect(url_for('sound.index'))
    return render_template('sound/create.html')
