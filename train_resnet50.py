"""
train_resnet50.py
------------------
Fine-tunes a torchvision ResNet50 (ImageNet-pretrained) as a binary
real-vs-fake classifier on ELA heatmaps produced by prepare_dataset.py.

Expected dataset layout (from prepare_dataset.py):

    dataset/
        train/real/*.png   train/fake/*.png
        val/real/*.png     val/fake/*.png
        test/real/*.png    test/fake/*.png

Usage:
    python train_resnet50.py --data_dir dataset --epochs 15 --batch_size 32 \
        --lr 1e-4 --unfreeze_at 5 --output_dir runs/exp1
"""

import argparse
import copy
import json
import time
from pathlib import Path

import torch
import torch.nn as nn
from torch.optim import Adam
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def build_dataloaders(data_dir: Path, batch_size: int, num_workers: int = 4):
    train_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(5),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])
    eval_tfms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])

    train_ds = datasets.ImageFolder(data_dir / "train", transform=train_tfms)
    val_ds = datasets.ImageFolder(data_dir / "val", transform=eval_tfms)
    test_ds = datasets.ImageFolder(data_dir / "test", transform=eval_tfms)

    # Sanity check: class_to_idx should be {'fake': 0, 'real': 1} or similar,
    # but it's alphabetical, so 'fake' -> 0, 'real' -> 1.
    assert train_ds.classes == val_ds.classes == test_ds.classes, "Class mismatch across splits"

    loaders = {
        "train": DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers),
        "val": DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
        "test": DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers),
    }
    return loaders, train_ds.classes


def build_model(num_classes: int = 2, freeze_backbone: bool = True) -> nn.Module:
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the final FC layer for our binary task.
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, num_classes),
    )
    return model


def unfreeze_backbone(model: nn.Module):
    for param in model.parameters():
        param.requires_grad = True


def run_epoch(model, loader, criterion, optimizer, device, train: bool):
    model.train() if train else model.eval()

    running_loss, running_correct, total = 0.0, 0, 0

    torch.set_grad_enabled(train)
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)

        if train:
            optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)

        if train:
            loss.backward()
            optimizer.step()

        preds = outputs.argmax(dim=1)
        running_loss += loss.item() * inputs.size(0)
        running_correct += (preds == labels).sum().item()
        total += inputs.size(0)

    return running_loss / total, running_correct / total


def main():
    parser = argparse.ArgumentParser(description="Fine-tune ResNet50 on ELA heatmaps.")
    parser.add_argument("--data_dir", required=True, type=Path)
    parser.add_argument("--output_dir", default="runs/exp1", type=Path)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--unfreeze_at", type=int, default=5,
                         help="Epoch at which to unfreeze the full backbone for fine-tuning "
                              "(set higher than --epochs to keep it frozen the whole run).")
    parser.add_argument("--patience", type=int, default=5, help="Early stopping patience on val loss.")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    loaders, classes = build_dataloaders(args.data_dir, args.batch_size, args.num_workers)
    print(f"Classes: {classes}  (index order used for predictions)")

    model = build_model(num_classes=len(classes), freeze_backbone=True).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=7, gamma=0.1)

    best_val_loss = float("inf")
    best_state = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0
    history = []

    for epoch in range(1, args.epochs + 1):
        start = time.time()

        if epoch == args.unfreeze_at:
            print(f"Epoch {epoch}: unfreezing full backbone for fine-tuning.")
            unfreeze_backbone(model)
            optimizer = Adam(model.parameters(), lr=args.lr / 10)
            scheduler = StepLR(optimizer, step_size=7, gamma=0.1)

        train_loss, train_acc = run_epoch(model, loaders["train"], criterion, optimizer, device, train=True)
        val_loss, val_acc = run_epoch(model, loaders["val"], criterion, optimizer, device, train=False)
        scheduler.step()

        elapsed = time.time() - start
        print(f"Epoch {epoch}/{args.epochs} "
              f"train_loss={train_loss:.4f} train_acc={train_acc:.4f} "
              f"val_loss={val_loss:.4f} val_acc={val_acc:.4f} "
              f"({elapsed:.1f}s)")

        history.append({
            "epoch": epoch, "train_loss": train_loss, "train_acc": train_acc,
            "val_loss": val_loss, "val_acc": val_acc,
        })

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
            torch.save(best_state, args.output_dir / "best_model.pt")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= args.patience:
                print(f"Early stopping at epoch {epoch} (no val improvement for {args.patience} epochs).")
                break

    # Evaluate best model on the held-out test set.
    model.load_state_dict(best_state)
    test_loss, test_acc = run_epoch(model, loaders["test"], criterion, optimizer, device, train=False)
    print(f"\nTest results: loss={test_loss:.4f} acc={test_acc:.4f}")

    with open(args.output_dir / "history.json", "w") as f:
        json.dump({"history": history, "classes": classes,
                   "test_loss": test_loss, "test_acc": test_acc}, f, indent=2)

    print(f"\nBest model saved to: {(args.output_dir / 'best_model.pt').resolve()}")


if __name__ == "__main__":
    main()
