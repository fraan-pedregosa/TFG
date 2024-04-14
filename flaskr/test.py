from flask import Flask, jsonify
from pydub import AudioSegment
import numpy as np

app = Flask(__name__)

def generate_audio():
    with app.app_context():
        frequency = 440
        duration = 30
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # Generate the drum beats
        kick = np.zeros_like(t)
        snare = np.zeros_like(t)
        
        kick_beat = np.random.choice([0, 1], size=int(sample_rate * duration), p=[0.8, 0.2])
        snare_beat = np.random.choice([0, 1], size=int(sample_rate * duration), p=[0.9, 0.1])
        
        kick[kick_beat == 1] = 0.8
        snare[snare_beat == 1] = 0.6
        
        # Generate the audio with drum beats
        audio_data = kick + snare
        
        audio_data = (audio_data * 32767).astype(np.int16)
        audio_segment = AudioSegment(audio_data.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1)
        
        output_file = "/home/francisco/Ampliacion/TFG/TFG/flaskr/file.mp3"  # Replace with desired output file path
        audio_segment.export(output_file, format="mp3")
        
        return jsonify({"message": "Audio generated successfully"}), 200

if __name__ == "__main__":
    generate_audio()
