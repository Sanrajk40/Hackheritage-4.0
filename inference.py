"""
inference.py
-------------
Run the fine-tuned ResNet50 on a new document image: generates the ELA
heatmap on the fly, runs the model, and prints real/fake + confidence.

Usage:
    python inference.py --model runs/exp1/best_model.pt --image path/to/doc.jpg
"""

import argparse
from pathlib import Path

import torch
import torch.nn.functional as F
from torchvision import models, transforms

from ela_utils import compute_ela

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Must match the alphabetical ImageFolder ordering used in training:
# 'fake' -> 0, 'real' -> 1
CLASS_NAMES = ["fake", "real"]


def load_model(model_path: str, device):
    model = models.resnet50(weights=None)
    in_features = model.fc.in_features
    model.fc = torch.nn.Sequential(
        torch.nn.Dropout(0.3),
        torch.nn.Linear(in_features, len(CLASS_NAMES)),
    )
    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def predict(model, image_path: str, device, quality: int = 90, scale: int = 15):
    ela_image = compute_ela(image_path, quality=quality, scale=scale)

    tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    tensor = tfms(ela_image).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs = F.softmax(logits, dim=1).squeeze(0)

    pred_idx = int(probs.argmax())
    return CLASS_NAMES[pred_idx], float(probs[pred_idx]), {
        CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))
    }


def main():
    parser = argparse.ArgumentParser(description="Run fake-document detection on a single image.")
    parser.add_argument("--model", required=True, help="best_model.pt")
    parser.add_argument("--image", required=True, help="Path to the document image to check")
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--scale", type=int, default=15)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.model, device)

    label, confidence, all_probs = predict(model, args.image, device, args.quality, args.scale)

    print(f"Image: {args.image}")
    print(f"Prediction: {label.upper()}  (confidence: {confidence:.2%})")
    print(f"All class probabilities: {all_probs}")


if __name__ == "__main__":
    main()
