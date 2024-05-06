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

@bp.route('/enviar_datos', methods=['POST'])
def enviar_datos():
    try:
        # Obtener datos de la solicitud POST (asumimos que se envía un número)
        data = request.json
        
        # Hacer una solicitud POST al otro servidor en el puerto 7860, enviando el número
        response = requests.post('http://127.0.0.1:7860/recibir_datos', json=data)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            # Obtener el contenido de la respuesta (asumimos que el servidor en el puerto 7860 devuelve el número multiplicado por 2)
            response_data = response.json()
            return f'Respuesta de la otra aplicación: {response_data}'
        else:
            return jsonify({"error": f"Failed to send request to port 7860. Status code: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500



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
        option = request.form['option']
        
        if option == "option1":
            public = "true"
        else:
            public = "false"
        
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
                'prompt': prompt,
                'public': public

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

@bp.route('/consejos')
def consejos():
    return render_template('sound/consejos.html')

from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip, AudioFileClip
from flask import send_file
import os


@bp.route('/merge_audio_video', methods=['GET'])
def show_merge_page():
    return render_template('sound/video.html')

@bp.route('/merge_audio_video', methods=['POST'])
def merge_audio_video():
    audio_file = request.files['audio_file']
    video_file = request.files['video_file']

    if not audio_file.filename or not video_file.filename:
        return "Error: No se proporcionaron archivos de audio o video", 400

    audio_filename = secure_filename(audio_file.filename)
    video_filename = secure_filename(video_file.filename)

    audio_file.save(audio_filename)
    video_file.save(video_filename)

    video = VideoFileClip(video_filename)
    audio = AudioFileClip(audio_filename)

    video = video.set_audio(audio)
    

    nombre_audio = ''
    nombre_video = ''
    for char in audio_filename:
        if char == '.':
            break
        else:
            nombre_audio = nombre_audio + char
    
    for char in video_filename:
        if char == '.':
            break
        else:
            nombre_video = nombre_video + char
    
    nombre_archivo = nombre_video + nombre_audio + '.mp4'
    
    
    output_filename = os.path.join(os.getcwd(), nombre_archivo)
    video.write_videofile(output_filename)

    return send_file(output_filename, as_attachment=True)


@bp.route('/generateaudio', methods=('GET', 'POST'))
@login_required
def generate_audio():
    
    if request.method == 'POST':
        title = request.form['title']        
        duration = request.form['duration']
        prompt = request.form['prompt']
        option = request.form['option']
        
        if option == "option1":
            public = "true"
        else:
            public = "false"
        
        error = None
        if not title or not duration or not prompt:
            error = 'Debes completar todos los campos'

        # Enviar solicitud al módulo de IA
        response = requests.post('http://localhost:7860/generateaudio', data={'title': title, 'prompt': prompt, 'duration': duration})

        # Verificar el tipo de contenido de la respuesta
        if response.status_code == 200:

            # La respuesta es el audio en formato de bytes
            audio_data = response.content
            ruta = 'flaskr/static/audios/'+title+'.wav'
            rutadb = title+'.wav'
            # Guardar el audio en el servidor
            with open(ruta, 'wb') as audio_file:
                audio_file.write(audio_data)

            # Guardar la ruta del audio en la base de datos
            if error is not None:
                flash(error)
            else:
                sound_db = get_sound_db()  # Llama a la función para obtener la colección de MongoDB
                sound_db.insert_one({
                    'email': g.user['email'],
                    'title': title,
                    'duration': duration,
                    'prompt': prompt,
                    'path': rutadb,
                    'public': public

                })
            
            return render_template('sound/misaudios.html')
        else:
            # La respuesta es un mensaje de error en formato JSON
            error_message = response.json().get('error', 'Error desconocido')
            return jsonify({"error": error_message}), 500
