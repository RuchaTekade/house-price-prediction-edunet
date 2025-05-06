import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import json

# Load dataset
df = pd.read_csv('data/Housing.csv')

# Standardize categorical values to match form options
df['furnishingstatus'] = df['furnishingstatus'].str.lower()
df['guestroom'] = df['guestroom'].str.lower()

# Rename columns to match our form
df = df.rename(columns={
    'area': 'size',
    'furnishingstatus': 'furnish_status',
    'guestroom': 'guest_room'
})

# Create synthetic location
df['location'] = pd.qcut(df['price'], q=4, labels=['Area A', 'Area B', 'Area C', 'Area D'])

# Convert categorical features
encoders = {}
for col, options in [
    ('furnish_status', ['furnished', 'semi-furnished', 'unfurnished']),
    ('guest_room', ['no', 'yes']),
    ('location', ['Area A', 'Area B', 'Area C', 'Area D'])
]:
    # Ensure consistent categories
    df[col] = pd.Categorical(df[col], categories=options)
    encoder = LabelEncoder()
    encoder.fit(options)  # Force the encoder to use our specified categories
    df[col] = encoder.transform(df[col])
    encoders[col] = encoder
    
    # Save categories for validation
    with open(f'model/{col}_categories.json', 'w') as f:
        json.dump(options, f)  # Save our specified options, not the dataset's

# Features and target
X = df[['size', 'bedrooms', 'bathrooms', 'parking', 'location', 'furnish_status', 'guest_room']]
y = df['price']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Create model directory if not exists
os.makedirs('model', exist_ok=True)

# Save everything
joblib.dump(model, 'model/model.pkl')
for col, encoder in encoders.items():
    joblib.dump(encoder, f'model/{col}_encoder.pkl')

print("Model trained successfully!")
print(f"Model score: {model.score(X_test, y_test):.2f}")