"""
PetCheck AI Prediction - Works with trained model
Recognizes: Healthy, Skin Infection, Eye Infection, Ear Infection, 
Ringworm, Wounds/Injuries, Obesity, Dental Disease
"""

import os
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'petcheck_model.pth')

# MUST MATCH YOUR TRAINING CLASSES EXACTLY
DISEASE_CLASSES = [
    "Healthy",
    "Skin Infection",
    "Eye Infection",
    "Ear Infection",
    "Ringworm",
    "Wounds/Injuries",
    "Obesity",
    "Dental Disease"
]

# Detailed advice for each condition
DISEASE_ADVICE = {
    "Healthy": "✅ Your pet appears healthy! Keep up regular vet checkups, a balanced diet, and daily exercise.",
    "Skin Infection": "⚠️ Clean the affected area with mild soap. Prevent scratching. Visit a vet for proper medication.",
    "Eye Infection": "⚠️ Gently wipe discharge with a clean, damp cloth. Do NOT use human eye drops. See a vet for antibiotics.",
    "Ear Infection": "⚠️ Do NOT insert anything into the ear. Visit a vet for proper cleaning and medication.",
    "Ringworm": "⚠️ Isolate your pet from other animals. Wash bedding daily. Antifungal treatment from a vet is needed.",
    "Wounds/Injuries": "🚨 Clean with saline solution. Apply gentle pressure if bleeding. See a vet for deep wounds.",
    "Obesity": "⚠️ Reduce food portions. Increase daily exercise. Consult a vet for a proper diet plan.",
    "Dental Disease": "⚠️ Brush your pet's teeth with pet-safe toothpaste. Provide dental chews. Schedule a vet dental checkup."
}

# What the AI looks for in each condition
DISEASE_SIGNS = {
    "Healthy": "Clear eyes, clean ears, healthy skin, normal weight",
    "Skin Infection": "Redness, rashes, bumps, hair loss, scratching",
    "Eye Infection": "Redness, swelling, discharge, squinting",
    "Ear Infection": "Head shaking, ear scratching, dark discharge, odor",
    "Ringworm": "Circular bald patches, scaly skin, broken hairs",
    "Wounds/Injuries": "Cuts, scrapes, swelling, bleeding",
    "Obesity": "Overweight body, no waist definition, excess fat",
    "Dental Disease": "Yellow teeth, red gums, bad breath, drooling"
}

_model = None

def load_model():
    """Load your trained model"""
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                # Use ResNet18 (matching your training)
                _model = models.resnet18(weights=None)
                _model.fc = nn.Linear(_model.fc.in_features, len(DISEASE_CLASSES))
                _model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
                _model.eval()
                print("✅ Trained AI model loaded successfully!")
            else:
                print("⚠️ Model file not found. Please run training first.")
                return None
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    return _model

def predict_disease(image_path):
    """Predict disease from pet image using trained model"""
    
    try:
        # Load the trained model
        model = load_model()
        
        if model is None:
            return {
                'success': False,
                'error': 'no_model',
                'message': 'AI model not trained yet. Please run training first.',
                'disease': 'Model Not Ready',
                'confidence': 0,
                'advice': 'Run: python model/train.py to train the AI model',
                'all_predictions': []
            }
        
        # Load and prepare the image
        image = Image.open(image_path).convert('RGB')
        
        # Use the same transform as training
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        input_tensor = transform(image).unsqueeze(0)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)[0]
        
        # Get top prediction
        confidence, idx = torch.max(probabilities, 0)
        disease = DISEASE_CLASSES[idx.item()]
        confidence_pct = round(confidence.item() * 100, 2)
        
        # Get all predictions for display
        all_predictions = []
        for i, prob in enumerate(probabilities):
            all_predictions.append({
                'disease': DISEASE_CLASSES[i],
                'confidence': round(prob.item() * 100, 2)
            })
        all_predictions.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'success': True,
            'disease': disease,
            'confidence': confidence_pct,
            'signs': DISEASE_SIGNS.get(disease, ""),
            'advice': DISEASE_ADVICE.get(disease, "Please consult a veterinarian."),
            'all_predictions': all_predictions[:4],
            'mode': 'trained_ai'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': 'processing_error',
            'message': str(e),
            'disease': 'Error',
            'confidence': 0,
            'advice': 'Please try uploading a different image.',
            'all_predictions': []
        }