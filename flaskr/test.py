from flask import Flask, jsonify
from pydub import AudioSegment
import numpy as np

app = Flask(__name__)

def generate_audio():
    with app.app_context():
        frequency = 440
        duration = 3
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        audio_data = (audio_data * 32767).astype(np.int16)
        audio_segment = AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1)
        output_file = "/home/francisco/Ampliacion/TFG/TFG/flaskr/file.mp3"  # Replace with the desired output file path
        audio_segment.export(output_file, format="mp3")
        return jsonify({"message": "Audio generated successfully"}), 200

if __name__ == "__main__":
    generate_audio()