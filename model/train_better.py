"""
PetCheck Optimized Training
Train with your 136 train + 34 val images
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import os

# Configuration
DATASET_DIR = 'dataset'
MODEL_SAVE_PATH = 'model/petcheck_model.pth'
NUM_CLASSES = 8
BATCH_SIZE = 16
EPOCHS = 60
LEARNING_RATE = 0.0001

CLASS_NAMES = [
    "Healthy",
    "Skin Infection",
    "Eye Infection",
    "Ear Infection",
    "Ringworm",
    "Wounds/Injuries",
    "Obesity",
    "Dental Disease"
]

# Data augmentation
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def train():
    print("=" * 60)
    print("🐾 PetCheck Optimized Training")
    print("=" * 60)
    
    # Check dataset
    train_dir = os.path.join(DATASET_DIR, 'train')
    val_dir = os.path.join(DATASET_DIR, 'val')
    
    if not os.path.exists(train_dir):
        print(f"\n❌ Training folder not found: {train_dir}")
        return
    
    # Load datasets
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transform)
    
    if os.path.exists(val_dir) and len(os.listdir(val_dir)) > 0:
        val_dataset = datasets.ImageFolder(val_dir, transform=val_transform)
        print(f"\n✅ Using separate validation folder")
    else:
        val_size = int(0.2 * len(train_dataset))
        train_size = len(train_dataset) - val_size
        train_dataset, val_dataset = torch.utils.data.random_split(train_dataset, [train_size, val_size])
        print(f"\n⚠️ No validation folder. Created 80/20 split")
    
    print(f"\n📊 Dataset Statistics:")
    print(f"   Training images: {len(train_dataset)}")
    print(f"   Validation images: {len(val_dataset)}")
    print(f"   Classes: {CLASS_NAMES}")
    
    # Show class distribution
    print(f"\n📈 Training Class Distribution:")
    if hasattr(train_dataset, 'classes'):
        for i, class_name in enumerate(CLASS_NAMES):
            count = sum(1 for _, label in train_dataset.samples if label == i)
            print(f"   {class_name}: {count} images")
    
    # Data loaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    # Device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"\n🖥️ Training on: {device}")
    
    # Model
    model = models.resnet50(weights='IMAGENET1K_V2')
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    model = model.to(device)
    
    # Loss, Optimizer, Scheduler
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    best_val_acc = 0.0
    
    print(f"\n🚀 Starting Training for {EPOCHS} epochs...")
    print("=" * 60)
    
    for epoch in range(EPOCHS):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)
        
        # Update learning rate
        scheduler.step(avg_val_loss)
        
        # Print progress
        print(f"Epoch [{epoch+1:2d}/{EPOCHS}] | "
              f"Train Acc: {train_acc:.2f}% | Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            os.makedirs('model', exist_ok=True)
            torch.save(model.state_dict(), MODEL_SAVE_PATH)
            print(f"   ✅ Best model saved! (Val Acc: {val_acc:.2f}%)")
    
    print("=" * 60)
    print(f"\n🎉 TRAINING COMPLETE!")
    print(f"   Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"   Model saved to: {MODEL_SAVE_PATH}")
    
    print("\n🎯 Next Steps:")
    print("   1. Restart your Flask app: python app.py")
    print("   2. Upload a pet photo")
    print("   3. The AI will now give diagnoses based on your training!")

if __name__ == '__main__':
    train()