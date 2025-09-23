from torch.utils.data import Dataset
import torch
from winterrb.utils import generate_all_augmentations

class CustomDataset(Dataset):
    def __init__(self, x_data, y_data, transform=None, augment=False):
        self.transform = transform
        self.augment = augment

        if self.augment:
            self.samples = []
            for x, y in zip(x_data, y_data):
                for aug in generate_all_augmentations(x):
                    self.samples.append((aug, y))
        else:
            self.samples = list(zip(x_data, y_data))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y = self.samples[idx]

        if self.transform:
            x = self.transform(x)

        y = torch.tensor(y).float()  # optional: ensures tensor output

        return x, y