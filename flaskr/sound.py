from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort


from flask import jsonify 
from flask import current_app


from flaskr.auth import login_required
from flaskr.db import get_sound_db
from flaskr.db import get_users_db
from flask_pymongo import pymongo
from bson.objectid import ObjectId
from flask_cors import CORS
import requests


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
        duration = request.form['duration']
        prompt = request.form['prompt']
        
        
        error = None
        if not title or not duration or not prompt:
            error = 'Debes completar todos los campos'
        if error is not None:
            flash(error)
        else:
            sound_db = get_sound_db()  # Llama a la función para obtener la colección de MongoDB
            sound_db.insert_one({
                'email': g.user['email'],
                'title': title,
                'duration': duration,
                'prompt': prompt

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
        duration = request.form['duration']
        prompt = request.form['prompt']
        
        error = None
        if not title:
            error = 'Debes completar el campo de título'
        if not duration:
            error = 'Debes completar el campo de duración'
        if not prompt:
            error = 'Debes completar el campo de prompt'
            
        if error is not None:
            flash(error)
        else:
            sound_collection.update_one({'_id': ObjectId(sound_id)}, {'$set': {'title': title, 'duration': duration, 'prompt': prompt}})
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

@bp.route('/generateaudio', methods=['POST'])
def generate_audio():
    try:
        title = request.form['title']
        prompt = request.form['prompt']
        duracion = request.form['duracion']

        # Enviar solicitud al módulo de IA
        response = requests.post('http://localhost:7860/generateaudio', data={'title': title, 'prompt': prompt, 'duracion': duracion})

        # Verificar el tipo de contenido de la respuesta
        if response.status_code == 200:

            # La respuesta es el audio en formato de bytes
            audio_data = response.content

            # Guardar el audio en el servidor
            with open('.wav', 'wb') as audio_file:
                audio_file.audiowrite(audio_data)

            # Guardar la ruta del audio en la base de datos
            
            return jsonify({"message": "Audio generado exitosamente"}), 200
        else:
            # La respuesta es un mensaje de error en formato JSON
            error_message = response.json().get('error', 'Error desconocido')
            return jsonify({"error": error_message}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500
