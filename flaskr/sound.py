from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_sound_db
from flaskr.db import get_users_db
from flask_pymongo import pymongo

bp = Blueprint('sound', __name__)

@bp.route('/')
def index():
    sound_collection = get_sound_db().sound_collection
    sound = sound_collection.find().sort('_id', pymongo.DESCENDING)
    return render_template('sound/index.html', sound=sound)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        audiolink = request.form['audiolink']
        error = None
        if not title or not audiolink:
            error = 'Debes completar ambos campos'
        if error is not None:
            flash(error)
        else:
            get_sound_db.insert_one({
                'title': title,
                'audiolink': audiolink,
                'author_id': g.user['id']
            })
            return redirect(url_for('sound.index'))
    return render_template('sound/create.html')


def get_sound(sound_id, check_author=True):
    sound_collection = get_sound_db().sound_collection
    sound = sound_collection.find_one({'_id': sound_id, 'author_id': g.user['id']})

    if sound is None:
        abort(404, f"Sound id {sound_id} doesn't exist.")

    if check_author and sound['author_id'] != g.user['id']:
        abort(403)

    return sound

@bp.route('/update/<string:sound_id>', methods=('GET', 'POST'))
@login_required
def update(sound_id):
    sound_collection = get_sound_db().sound_collection
    sound = get_sound(sound_id, check_author=True)
    if sound is None:
        abort(404, "Sound doesn't exist or you don't have permission to update it.")
    
    if request.method == 'POST':
        title = request.form['title']
        error = None
        if not title:
            error = 'Debes completar el campo de título'
        if error is not None:
            flash(error)
        else:
            sound_collection.update_one({'_id': sound_id}, {'$set': {'title': title}})
            return redirect(url_for('sound.index'))
    
    return render_template('sound/update.html', sound=sound)

@bp.route('/<string:sound_id>/delete', methods=('POST',))
@login_required
def delete(sound_id):
    sound_collection = get_sound_db().sound_collection
    sound = get_sound(sound_id, check_author=True)
    if sound is None:
        abort(404, "Sound doesn't exist or you don't have permission to delete it.")
    
    sound_collection.delete_one({'_id': sound_id})
    return redirect(url_for('sound.index'))