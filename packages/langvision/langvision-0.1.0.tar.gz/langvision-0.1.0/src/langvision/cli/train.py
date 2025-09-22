import argparse
import torch
from langvision.models.vision_transformer import VisionTransformer
from langvision.utils.config import default_config
from langvision.utils.data import get_preprocessing
from torchvision import datasets
from torch.utils.data import DataLoader
import os


def parse_args():
    parser = argparse.ArgumentParser(
        description='Train or evaluate VisionTransformer with LoRA',
        epilog='''\nExamples:\n  langvision train --dataset cifar10 --epochs 5\n  langvision train --dataset cifar100 --lora_rank 8 --eval\n''',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Data
    data_group = parser.add_argument_group('Data')
    data_group.add_argument('--dataset', type=str, default='cifar10', choices=['cifar10', 'cifar100'], help='Dataset to use')
    data_group.add_argument('--data_dir', type=str, default='./data', help='Dataset directory')
    # Training
    train_group = parser.add_argument_group('Training')
    train_group.add_argument('--epochs', type=int, default=10, help='Number of training epochs')
    train_group.add_argument('--batch_size', type=int, default=64, help='Batch size for training')
    train_group.add_argument('--learning_rate', type=float, default=1e-3, help='Learning rate')
    # LoRA
    lora_group = parser.add_argument_group('LoRA')
    lora_group.add_argument('--lora_rank', type=int, default=4, help='LoRA rank (low-rank adaptation)')
    lora_group.add_argument('--lora_alpha', type=float, default=1.0, help='LoRA alpha scaling')
    lora_group.add_argument('--lora_dropout', type=float, default=0.1, help='LoRA dropout rate')
    # Output
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('--output_dir', type=str, default='./checkpoints', help='Directory to save checkpoints')
    # Misc
    misc_group = parser.add_argument_group('Misc')
    misc_group.add_argument('--eval', action='store_true', help='Run evaluation only (no training)')
    misc_group.add_argument('--export', action='store_true', help='Export model for inference')
    misc_group.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu', help='Device to use (cuda or cpu)')
    return parser.parse_args()


def get_dataloaders(args):
    transform = get_preprocessing(default_config['img_size'])
    if args.dataset == 'cifar10':
        train_dataset = datasets.CIFAR10(root=args.data_dir, train=True, download=True, transform=transform)
        val_dataset = datasets.CIFAR10(root=args.data_dir, train=False, download=True, transform=transform)
        num_classes = 10
    elif args.dataset == 'cifar100':
        train_dataset = datasets.CIFAR100(root=args.data_dir, train=True, download=True, transform=transform)
        val_dataset = datasets.CIFAR100(root=args.data_dir, train=False, download=True, transform=transform)
        num_classes = 100
    else:
        raise ValueError(f"Unsupported dataset: {args.dataset}")
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False, num_workers=2)
    return train_loader, val_loader, num_classes


def main():
    args = parse_args()
    train_loader, val_loader, num_classes = get_dataloaders(args)
    model = VisionTransformer(
        img_size=default_config['img_size'],
        patch_size=default_config['patch_size'],
        in_chans=default_config['in_chans'],
        num_classes=num_classes,
        embed_dim=default_config['embed_dim'],
        depth=default_config['depth'],
        num_heads=default_config['num_heads'],
        mlp_ratio=default_config['mlp_ratio'],
        lora_config={
            'r': args.lora_rank,
            'alpha': args.lora_alpha,
            'dropout': args.lora_dropout,
        },
    ).to(args.device)

    if args.eval:
        print('Evaluation mode (stub)')
        # TODO: Implement evaluation logic
        return
    if args.export:
        print('Export mode (stub)')
        # TODO: Implement model export logic
        return

    optimizer = torch.optim.Adam(
        [p for n, p in model.named_parameters() if 'lora' in n and p.requires_grad],
        lr=args.learning_rate
    )
    criterion = torch.nn.CrossEntropyLoss()

    for epoch in range(args.epochs):
        model.train()
        total_loss, correct, total = 0, 0, 0
        for imgs, labels in train_loader:
            imgs, labels = imgs.to(args.device), labels.to(args.device)
            optimizer.zero_grad()
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * imgs.size(0)
            _, preds = outputs.max(1)
            correct += preds.eq(labels).sum().item()
            total += imgs.size(0)
        print(f"Epoch {epoch+1}/{args.epochs} | Train Loss: {total_loss/total:.4f}, Acc: {correct/total:.4f}")
        # TODO: Add validation and checkpoint saving

    os.makedirs(args.output_dir, exist_ok=True)
    torch.save(model.state_dict(), os.path.join(args.output_dir, 'vit_lora_final.pth'))
    print(f"Model saved to {os.path.join(args.output_dir, 'vit_lora_final.pth')}")

if __name__ == '__main__':
    main() 