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

import quantum_circuits
from quantum_circuits import circuit__1

class ClassicalFrozen_QuantumTrainable__1(nn.Module):
    def __init__(self, classical_model_path, model_def):
        super().__init__()

        self.quantum_weights = {"theta_RY_switch": (3, 3),
                                "vqc_weights": (3, 1, 7, 3)}
        # self.qlayer = qml.qnn.TorchLayer(qml.transforms.broadcast_expand(circuit__1), self.quantum_weights)
        self.qlayer = qml.qnn.TorchLayer(circuit__1(bool_vals=None), self.quantum_weights)

        self.checkpoint = torch.load(classical_model_path, weights_only=True)
        self.classical_model = model_def()
        self.classical_model.load_state_dict(self.checkpoint['model'])

        for param in self.classical_model.parameters():
            param.requires_grad = False

    def forward(self, x1, x2):
        x1 = self.classical_model(x1)
        x2 = self.classical_model(x2)

        x1 = F.normalize(x1, p=2, dim=1) / np.sqrt(2)
        x2 = F.normalize(x2, p=2, dim=1) / np.sqrt(2)

        x = torch.cat((x1, x2), dim=1)
        # x = torch.stack([x1, x2], dim=0)
        # print(x1.shape, x2.shape, x.shape)
        
        overlap = self.qlayer(x)
        # overlap = torch.mean(overlap, dim=1)
        
        overlap = (1 + overlap) / 2

        # overlap = nn.Sigmoid()(overlap)

        # print(x1, x2, overlap)

        # print("overlap:", overlap)
        
        return overlap

    # def forward(self, x):
    #     x = self.classical_model(x)
        
    #     return x