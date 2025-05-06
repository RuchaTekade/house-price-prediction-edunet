from flask import Flask, render_template, request, jsonify
import joblib
import os
import json

app = Flask(__name__)

def load_model_files():
    """Load model and encoders with error handling"""
    try:
        model = joblib.load('model/model.pkl')
        encoders = {
            'furnish_status': joblib.load('model/furnish_status_encoder.pkl'),
            'guest_room': joblib.load('model/guest_room_encoder.pkl'),
            'location': joblib.load('model/location_encoder.pkl')
        }
        categories = {
            'furnish_status': json.load(open('model/furnish_status_categories.json')),
            'guest_room': json.load(open('model/guest_room_categories.json')),
            'location': json.load(open('model/location_categories.json'))
        }
        return model, encoders, categories
    except Exception as e:
        raise RuntimeError(f"Model loading failed: {str(e)}")

try:
    model, encoders, categories = load_model_files()
except Exception as e:
    print(f"⚠️ Error during startup: {e}")
    # Consider fallback to external model URL here

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # ... (keep your existing predict code)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Render requires these settings