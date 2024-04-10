from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_sound_db
from flaskr.db import get_users_db
from flask_pymongo import pymongo
from bson.objectid import ObjectId

from bson import ObjectId

bp = Blueprint('sound', __name__)

@bp.route('/')
def index():
    sound_collection = get_sound_db()
    sound = sound_collection.find().sort('_id', pymongo.DESCENDING)
    return render_template('sound/index.html', sound=sound)

@bp.route('/misaudios')
def misaudios():
    sound_collection = get_sound_db()
    sound = sound_collection.find().sort('_id', pymongo.DESCENDING)
    return render_template('sound/misaudios.html', sound=sound)

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
            sound_db = get_sound_db()  # Llama a la función para obtener la colección de MongoDB
            sound_db.insert_one({
                'email': g.user['email'],
                'title': title,
                'audiolink': audiolink

            })
            return redirect(url_for('sound.index'))
    return render_template('sound/create.html')


def get_sound(sound_id, check_author=True):
    sound_collection = get_sound_db()
    sound = sound_collection.find_one({'_id': ObjectId(sound_id)})

    if sound is None:
        abort(404, f"Sound id {sound_id} doesn't exist.")

    if check_author and sound['email'] != g.user['email']:
        abort(403)

    return sound

@bp.route('/update/<string:sound_id>', methods=('GET', 'POST'))
@login_required
def update(sound_id):
    sound_collection = get_sound_db()
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
            sound_collection.update_one({'_id': ObjectId(sound_id)}, {'$set': {'title': title}})
            updated_sound = sound_collection.find_one({'_id': ObjectId(sound_id)})
            return redirect(url_for('sound.index'))

    return render_template('sound/update.html', sound=sound)

@bp.route('/<string:sound_id>/delete', methods=('POST',))
@login_required
def delete(sound_id):
    sound_collection = get_sound_db()
    sound = get_sound(sound_id, check_author=True)
    if sound is None:
        abort(404, "Sound doesn't exist or you don't have permission to delete it.")
    
    sound_collection.delete_one({'_id': ObjectId(sound_id)})
    return redirect(url_for('sound.index'))

@app.route('/generateaudio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()
        frequency = data.get('frequency')
        duration = data.get('duration')
                
        # Generate audio
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * frequency * t)
                
        # Initialize PyAudio
        p = pyaudio.PyAudio()
                
        # Open stream
        stream = p.open(format=pyaudio.paFloat32,
                                channels=1,
                                rate=sample_rate,
                                output=True)                
        # Play audio
        stream.write(audio_data.astype(np.float32).tobytes())
                
        # Close stream
        stream.stop_stream()
        stream.close()
                
        # Terminate PyAudio
        p.terminate()
                
        return jsonify({"message": "Audio generated successfully"}), 200
                
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500