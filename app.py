from flask import Flask, render_template, request, jsonify
import joblib
import os
import json
import numpy as np

app = Flask(__name__)

def load_model_files():
    """Load model and encoders with absolute paths and error handling"""
    try:
        # Get absolute path to model directory
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')
        
        # Load model and encoders
        model = joblib.load(os.path.join(model_dir, 'model.pkl'))
        
        encoders = {
            'furnish_status': joblib.load(os.path.join(model_dir, 'furnish_status_encoder.pkl')),
            'guest_room': joblib.load(os.path.join(model_dir, 'guest_room_encoder.pkl')),
            'location': joblib.load(os.path.join(model_dir, 'location_encoder.pkl'))
        }
        
        # Load categories
        categories = {
            'furnish_status': json.load(open(os.path.join(model_dir, 'furnish_status_categories.json'))),
            'guest_room': json.load(open(os.path.join(model_dir, 'guest_room_categories.json'))),
            'location': json.load(open(os.path.join(model_dir, 'location_categories.json')))
        }
        
        return model, encoders, categories
        
    except Exception as e:
        raise RuntimeError(f"Model loading failed: {str(e)}")

# Load model at startup
try:
    model, encoders, categories = load_model_files()
    print("✅ Model and encoders loaded successfully")
except Exception as e:
    print(f"⚠️ Error during startup: {e}")
    model = encoders = categories = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded", "status": "failed"}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received", "status": "failed"}), 400
        
        # Input validation
        required_fields = ['size', 'bedrooms', 'bathrooms', 'parking', 'location', 'furnish_status', 'guest_room']
        if not all(field in data for field in required_fields):
            return jsonify({"error": f"Missing required fields: {required_fields}", "status": "failed"}), 400

        # Validate categorical inputs
        for field in ['furnish_status', 'guest_room', 'location']:
            if data[field] not in categories[field]:
                return jsonify({
                    "error": f"Invalid {field}. Must be one of: {categories[field]}",
                    "status": "failed"
                }), 400

        # Prepare features exactly as done during training
        features = [
            float(data['size']),
            int(data['bedrooms']),
            int(data['bathrooms']),
            int(data['parking']),
            int(encoders['location'].transform([data['location']])[0]),
            int(encoders['furnish_status'].transform([data['furnish_status']])[0]),
            int(encoders['guest_room'].transform([data['guest_room']])[0])
        ]
        
        # Make prediction
        prediction = model.predict([features])
        
        return jsonify({
         "prediction": round(float(prediction[0]), 2),  
    "status": "success"
        })

    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}", "status": "failed"}), 400
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}", "status": "failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)