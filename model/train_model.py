import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json
import os

# Load and prepare data
df = pd.read_csv('data/Housing.csv')
df['furnishingstatus'] = df['furnishingstatus'].str.lower().str.strip()
df['guestroom'] = df['guestroom'].str.lower().str.strip()

# Rename columns
df = df.rename(columns={
    'area': 'size',
    'furnishingstatus': 'furnish_status',
    'guestroom': 'guest_room'
})

# Create location categories
df['location'] = pd.qcut(df['price'], q=4, labels=['Area A', 'Area B', 'Area C', 'Area D'])

# Create model directory
os.makedirs('model', exist_ok=True)

# Define consistent categories
category_mapping = {
    'furnish_status': ['furnished', 'semi-furnished', 'unfurnished'],
    'guest_room': ['no', 'yes'],
    'location': ['Area A', 'Area B', 'Area C', 'Area D']
}

# Process and save encoders
encoders = {}
for col, options in category_mapping.items():
    encoder = LabelEncoder()
    encoder.fit(options)
    df[col] = encoder.transform(df[col])
    encoders[col] = encoder
    joblib.dump(encoder, f'model/{col}_encoder.pkl')
    with open(f'model/{col}_categories.json', 'w') as f:
        json.dump(options, f)

# Train model
X = df[['size', 'bedrooms', 'bathrooms', 'parking', 'location', 'furnish_status', 'guest_room']]
y = df['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
joblib.dump(model, 'model/model.pkl')

print(f"Model trained with score: {model.score(X_test, y_test):.2f}")
print("All model files saved to 'model/' directory")