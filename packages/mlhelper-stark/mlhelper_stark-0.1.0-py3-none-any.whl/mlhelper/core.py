"""
core function for mlhelper
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

def load_dataset(csv_path):
    """Load CSV inta a pandas DataFrame."""
    return pd.read_csv(csv_path)

def preprocess_features(X, scale=True):
    """scale Features if needed."""
    if scale:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        return X_scaled, scaler
    return X, None

def encode_labels(y):
    """Encode categorial labels to numeric."""
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    return y_encoded, encoder

def split_data(X, y, test_size=0.2, random_state=42):
    """Split into train/test."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)

def train_simple_model(X_train, y_train):
    """Train a basic Logistic Regression model."""
    model = LogisticRegression(max_item=500)
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluate Model Accuracy."""
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return acc

def save_model(model, path):
    """Save model with joblib."""
    joblib.dump(model, path)

def load_model(path):
    """Load model from file."""
    return joblib.load(path)