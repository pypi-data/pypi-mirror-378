import os
from PIL import ImageOps, Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader, IterableDataset

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

import pandas as pd

import random
import csv
import itertools
import pickle

import matplotlib.pyplot as plt
import cv2

import numpy as np
import tqdm

import pennylane as qml

from sklearn import metrics
from sklearn.metrics import classification_report

class SigNet__Half(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # Input: [1, 155, 220]
            nn.Conv2d(1, 48, kernel_size=11, stride=4),  # [96, 37, 53]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [96, 18, 26]
            nn.Conv2d(48, 128, kernel_size=5, padding=2),  # [256, 18, 26]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 8, 12]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(128, 192, kernel_size=3, padding=1),  # [384, 8, 12]
            nn.Conv2d(192, 128, kernel_size=3, padding=1),  # [256, 8, 12]
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 3, 5]
            nn.Dropout2d(p=0.3),
            nn.Flatten(),  # 256*3*5 = 3,840
            nn.Linear(1920, 512),
            nn.Dropout(p=0.5),  # Note: Dropout2d → Dropout for Linear layers
            nn.Linear(512, 128),
        )

    def forward(self, x1, x2):
        x1 = self.features(x1)
        x2 = self.features(x2)
        return x1, x2

class SigNet__Half_Single(nn.Module):
    def __init__(self, classical_final_output=128):
        super().__init__()
        self.features = nn.Sequential(
            # Input: [1, 155, 220]
            nn.Conv2d(1, 48, kernel_size=11, stride=4),  # [96, 37, 53]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [96, 18, 26]
            nn.Conv2d(48, 128, kernel_size=5, padding=2),  # [256, 18, 26]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 8, 12]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(128, 192, kernel_size=3, padding=1),  # [384, 8, 12]
            nn.Conv2d(192, 128, kernel_size=3, padding=1),  # [256, 8, 12]
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 3, 5]
            nn.Dropout2d(p=0.3),
            nn.Flatten(),  # 256*3*5 = 3,840
            nn.Linear(1920, 512),
            nn.Dropout(p=0.5),  # Note: Dropout2d → Dropout for Linear layers
            nn.Linear(512, classical_final_output),
        )

    def forward(self, x1):
        x1 = self.features(x1)
        # x2 = self.features(x2)
        return x1

class SigNet__Half_Half_Single(nn.Module):
    def __init__(self, classical_final_output=128):
        super().__init__()
        self.features = nn.Sequential(
            # Input: [1, 155, 220]
            nn.Conv2d(1, 24, kernel_size=11, stride=4),  # [96, 37, 53]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [96, 18, 26]
            nn.Conv2d(24, 64, kernel_size=5, padding=2),  # [256, 18, 26]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 8, 12]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(64, 96, kernel_size=3, padding=1),  # [384, 8, 12]
            nn.Conv2d(96, 64, kernel_size=3, padding=1),  # [256, 8, 12]
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 3, 5]
            nn.Dropout2d(p=0.3),
            nn.Flatten(),  # 256*3*5 = 3,840
            nn.Linear(960, 256),
            nn.Dropout(p=0.5),  # Note: Dropout2d → Dropout for Linear layers
            nn.Linear(256, classical_final_output),
        )

    def forward(self, x1):
        x1 = self.features(x1)
        # x2 = self.features(x2)
        return x1

class SigNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # Input: [1, 155, 220]
            nn.Conv2d(1, 96, kernel_size=11, stride=4),  # [96, 37, 53]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [96, 18, 26]
            nn.Conv2d(96, 256, kernel_size=5, padding=2),  # [256, 18, 26]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 8, 12]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(256, 384, kernel_size=3, padding=1),  # [384, 8, 12]
            nn.Conv2d(384, 256, kernel_size=3, padding=1),  # [256, 8, 12]
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 3, 5]
            nn.Dropout2d(p=0.3),
            nn.Flatten(),  # 256*3*5 = 3,840
            nn.Linear(3840, 1024),
            nn.Dropout(p=0.5),  # Note: Dropout2d → Dropout for Linear layers
            nn.Linear(1024, 128),
        )

    def forward(self, x1, x2):
        x1 = self.features(x1)
        x2 = self.features(x2)
        return x1, x2

class SigNet__Single(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            # Input: [1, 155, 220]
            nn.Conv2d(1, 96, kernel_size=11, stride=4),  # [96, 37, 53]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [96, 18, 26]
            nn.Conv2d(96, 256, kernel_size=5, padding=2),  # [256, 18, 26]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 8, 12]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(256, 384, kernel_size=3, padding=1),  # [384, 8, 12]
            nn.Conv2d(384, 256, kernel_size=3, padding=1),  # [256, 8, 12]
            nn.MaxPool2d(kernel_size=3, stride=2),  # [256, 3, 5]
            nn.Dropout2d(p=0.3),
            nn.Flatten(),  # 256*3*5 = 3,840
            nn.Linear(3840, 1024),
            nn.Dropout(p=0.5),  # Note: Dropout2d → Dropout for Linear layers
            nn.Linear(1024, 128),
        )

    def forward(self, x1):
        x1 = self.features(x1)
        # x2 = self.features(x2)
        return x1

class SigNet2_FullClassical(nn.Module):
    '''
    Reference Keras: https://github.com/sounakdey/SigNet/blob/master/SigNet_v1.py
    '''
    def __init__(self):
        super().__init__()
        # self.quantum_weights = {"weights": (4, n_qubits, 3)}
        # self.qlayer = qml.qnn.TorchLayer(Naive_QuantumHybrid, self.quantum_weights)

        self.features = nn.Sequential(
            #input size = [155, 220, 1]
            nn.Conv2d(1, 48, 11), # size = [145,210]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [72, 105]
            nn.Conv2d(48, 64, 5, padding=2, padding_mode='zeros'), # size = [72, 105]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [36, 52]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(64, 128, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.Conv2d(128, 64, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.MaxPool2d(2, stride=2), # size = [18, 26]
            nn.Dropout2d(p=0.3),
            nn.Flatten(1, -1), # 18*26*256
            nn.Linear(18*26*64, 1024),
            nn.Dropout2d(p=0.5),
            nn.Linear(1024, 128),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(128, 8)
            # nn.Dropout2d(p=0.5),
            # self.qlayer,
            # nn.Linear(8, 16),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(16, 32)
        )

        # TODO: init bias = 0

    def forward(self, x1, x2):
        x1 = self.features(x1)
        x2 = self.features(x2)
        return x1, x2

class SigNet2_FullClassical__Single(nn.Module):
    '''
    Reference Keras: https://github.com/sounakdey/SigNet/blob/master/SigNet_v1.py
    '''
    def __init__(self):
        super().__init__()
        # self.quantum_weights = {"weights": (4, n_qubits, 3)}
        # self.qlayer = qml.qnn.TorchLayer(Naive_QuantumHybrid, self.quantum_weights)

        self.features = nn.Sequential(
            #input size = [155, 220, 1]
            nn.Conv2d(1, 48, 11), # size = [145,210]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [72, 105]
            nn.Conv2d(48, 64, 5, padding=2, padding_mode='zeros'), # size = [72, 105]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [36, 52]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(64, 128, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.Conv2d(128, 64, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.MaxPool2d(2, stride=2), # size = [18, 26]
            nn.Dropout2d(p=0.3),
            nn.Flatten(1, -1), # 18*26*256
            nn.Linear(18*26*64, 1024),
            nn.Dropout2d(p=0.5),
            nn.Linear(1024, 128),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(128, 8)
            # nn.Dropout2d(p=0.5),
            # self.qlayer,
            # nn.Linear(8, 16),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(16, 32)
        )

        # TODO: init bias = 0

    def forward(self, x1):
        x1 = self.features(x1)
        # x2 = self.features(x2)
        return x1