from flask import Flask, render_template, request, jsonify
import joblib
import os
import json

app = Flask(__name__)

# Load all model files
def load_model_files():
    files = {
        'model': 'model/model.pkl',
        'encoders': {
            'furnish_status': 'model/furnish_status_encoder.pkl',
            'guest_room': 'model/guest_room_encoder.pkl',
            'location': 'model/location_encoder.pkl'
        },
        'categories': {
            'furnish_status': 'model/furnish_status_categories.json',
            'guest_room': 'model/guest_room_categories.json',
            'location': 'model/location_categories.json'
        }
    }
    
    # Check if all files exist
    for file in list(files['encoders'].values()) + list(files['categories'].values()) + [files['model']]:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Missing file: {file}")
    
    # Load everything
    model = joblib.load(files['model'])
    encoders = {name: joblib.load(path) for name, path in files['encoders'].items()}
    categories = {}
    
    for name, path in files['categories'].items():
        with open(path) as f:
            categories[name] = json.load(f)
    
    return model, encoders, categories

model, encoders, categories = load_model_files()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Validate all categorical inputs
        errors = {}
        for field in ['furnish_status', 'guest_room', 'location']:
            if data[field] not in categories[field]:
                errors[field] = f"Allowed values: {', '.join(categories[field])}"
        
        if errors:
            return jsonify({'error': "Invalid inputs", 'details': errors})
        
        # Prepare features
        features = [
            float(data['size']),
            int(data['bedrooms']),
            int(data['bathrooms']),
            int(data['parking']),
            encoders['location'].transform([data['location']])[0],
            encoders['furnish_status'].transform([data['furnish_status']])[0],
            encoders['guest_room'].transform([data['guest_room']])[0]
        ]
        
        prediction = model.predict([features])
        return jsonify({'prediction': round(prediction[0], 2)})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)