"""
PetCheck AI Prediction - Uses Trained Model
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'petcheck_model.pth')

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

DISEASE_ADVICE = {
    "Healthy": "✅ Your pet appears healthy!\n\n📋 Recommendations:\n• Schedule regular vet checkups\n• Maintain a balanced diet\n• Ensure daily exercise",
    "Skin Infection": "⚠️ SKIN INFECTION\n\n📋 Clean the area with mild soap. See a vet within 24-48 hours.",
    "Eye Infection": "⚠️ EYE INFECTION\n\n📋 Gently wipe discharge. See a vet within 24 hours.",
    "Ear Infection": "⚠️ EAR INFECTION\n\n📋 Do NOT insert anything. See a vet within 24-48 hours.",
    "Ringworm": "⚠️ RINGWORM\n\n📋 Isolate your pet. See a vet for antifungal medication.",
    "Wounds/Injuries": "🚨 WOUND DETECTED\n\n📋 Clean with saline. See a vet immediately if bleeding.",
    "Obesity": "⚠️ OBESITY\n\n📋 Reduce food portions. Increase exercise. Consult a vet.",
    "Dental Disease": "⚠️ DENTAL DISEASE\n\n📋 Brush teeth daily. Schedule dental cleaning."
}

_model = None

def load_model():
    global _model
    if _model is None:
        try:
            if os.path.exists(MODEL_PATH):
                print(f"✅ Loading model from {MODEL_PATH}")
                model = models.resnet50(weights=None)
                model.fc = nn.Linear(model.fc.in_features, len(DISEASE_CLASSES))
                model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
                model.eval()
                _model = model
                print("✅ Trained AI model loaded successfully!")
            else:
                print(f"❌ Model file not found at {MODEL_PATH}")
                return None
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return None
    return _model

def predict_disease(image_path):
    """Predict disease using trained model"""
    
    # Load the trained model
    model = load_model()
    
    if model is None:
        return {
            'success': False,
            'error': 'no_model',
            'disease': 'Model Not Ready',
            'confidence': 0,
            'advice': 'AI model not loaded. Please run training first:\n\npython model/train_optimized.py',
            'all_predictions': []
        }
    
    try:
        # Load and prepare image
        image = Image.open(image_path).convert('RGB')
        
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
        
        print(f"✅ Prediction: {disease} ({confidence_pct}%)")
        
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
            'advice': DISEASE_ADVICE.get(disease, "Consult a veterinarian."),
            'all_predictions': all_predictions[:4],
            'mode': 'trained_ai'
        }
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {
            'success': False,
            'error': str(e),
            'disease': 'Error',
            'confidence': 0,
            'advice': f'Error: {str(e)}. Please try again.',
            'all_predictions': []
        }