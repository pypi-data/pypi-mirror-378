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

class ContrastiveLoss(nn.Module):
    def __init__(self, alpha, beta, margin):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.margin = margin

    def forward(self, x1, x2, y):
        '''
        Shapes:
        -------
        x1: [B,C]
        x2: [B,C]
        y: [B,1]

        Returns:
        --------
        loss: [B,1]]
        '''
        distance = torch.pairwise_distance(x1, x2, p=2)
        # print("shapes:", x1.shape, x2.shape, y.shape)
        loss = self.alpha * (1-y) * distance**2 + \
               self.beta * y * (torch.max(torch.zeros_like(distance), self.margin - distance)**2)
        return torch.mean(loss, dtype=torch.float)

class TripletMarginLoss(nn.Module):
    """
    A custom loss function for triplet networks. It aims to pull the anchor
    and positive embeddings closer together while pushing the anchor and negative
    embeddings apart by at least a specified margin.
    """
    def __init__(self, margin=1.0, p=2):
        """
        Args:
            margin (float): The minimum distance that the anchor-negative pair
                            must be from the anchor-positive pair.
            p (int): The norm degree for the distance calculation (e.g., p=2 for Euclidean distance).
        """
        super(TripletMarginLoss, self).__init__()
        self.margin = margin
        self.p = p

    def forward(self, anchor, positive, negative):
        """
        Calculates the triplet loss.

        Args:
            anchor (torch.Tensor): The embedding vector for the anchor images.
            positive (torch.Tensor): The embedding vector for the positive images.
            negative (torch.Tensor): The embedding vector for the negative images.

        Returns:
            torch.Tensor: The mean loss for the batch.
        """
        # Calculate the distance between the anchor and positive embeddings
        distance_positive = F.pairwise_distance(anchor, positive, p=self.p)

        # Calculate the distance between the anchor and negative embeddings
        distance_negative = F.pairwise_distance(anchor, negative, p=self.p)

        # Calculate the loss
        # loss = max(0, distance_positive - distance_negative + margin)
        loss = torch.relu(distance_positive - distance_negative + self.margin)

        return torch.mean(loss)

class TripletMarginLoss__Quantum(nn.Module):
    """
    A custom loss function for triplet networks. It aims to pull the anchor
    and positive embeddings closer together while pushing the anchor and negative
    embeddings apart by at least a specified margin.
    """
    def __init__(self, margin=1.0, p=2):
        """
        Args:
            margin (float): The minimum distance that the anchor-negative pair
                            must be from the anchor-positive pair.
            p (int): The norm degree for the distance calculation (e.g., p=2 for Euclidean distance).
        """
        super(TripletMarginLoss__Quantum, self).__init__()
        self.margin = margin
        self.p = p

    # def forward(self, anchor, positive, negative):
    def forward(self, positive_dist, negative_dist):
        """
        Calculates the triplet loss.

        Args:
            anchor (torch.Tensor): The embedding vector for the anchor images.
            positive (torch.Tensor): The embedding vector for the positive images.
            negative (torch.Tensor): The embedding vector for the negative images.

        Returns:
            torch.Tensor: The mean loss for the batch.
        """
        # # Calculate the distance between the anchor and positive embeddings
        # distance_positive = F.pairwise_distance(anchor, positive, p=self.p)

        # # Calculate the distance between the anchor and negative embeddings
        # distance_negative = F.pairwise_distance(anchor, negative, p=self.p)

        # Calculate the loss
        # loss = max(0, distance_positive - distance_negative + margin)
        loss = torch.relu(0 - positive_dist + negative_dist + self.margin)

        return torch.mean(loss)

class ContrastiveLoss_Quantum(nn.Module):
    def __init__(self, alpha, beta, margin):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.margin = margin

    def forward(self, overlap, y):
        '''
        Shapes:
        -------
        x1: [B,C]
        x2: [B,C]
        y: [B,1]

        Returns:
        --------
        loss: [B,1]]
        '''
        distance = (1 - overlap) / 2

        loss = self.alpha * (1-y) * distance**2 + \
               self.beta * y * (torch.max(torch.zeros_like(distance), self.margin - distance)**2)
        return torch.mean(loss, dtype=torch.float)

class ContrastiveLoss_Quantum_Sigmoid(nn.Module):
    def __init__(self, alpha, beta, margin):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.margin = margin

    def forward(self, overlap, y):
        '''
        Shapes:
        -------
        x1: [B,C]
        x2: [B,C]
        y: [B,1]

        Returns:
        --------
        loss: [B,1]]
        '''
        # distance = torch.pairwise_distance(x1, x2, p=2)
        distance = overlap
        
        loss = self.alpha * (1-y) * distance**2 + \
               self.beta * y * (torch.max(torch.zeros_like(distance), self.margin - distance)**2)
        return torch.mean(loss, dtype=torch.float)

class ContrastiveLoss_Quantum_Direct(nn.Module):
    def __init__(self, alpha, beta, margin, overlap_func=None):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.margin = margin
        self.overlap_func = overlap_func

    def forward(self, overlap, y):
        '''
        Shapes:
        -------
        x1: [B,C]
        x2: [B,C]
        y: [B,1]

        Returns:
        --------
        loss: [B,1]]
        '''
        # distance = torch.pairwise_distance(x1, x2, p=2)
        if self.overlap_func is None:
            distance = overlap
            # 0: different class
            # 1: same class
        else:
            distance = self.overlap_func(overlap)
        
        # loss = self.alpha * (1-y) * (1 - distance)**2 + \
        #        self.beta * y * (torch.max(torch.zeros_like(distance), self.margin - 1 + distance)**2)

        loss_similar = self.alpha * (1 - overlap)**2
        loss_dissimilar = self.beta * torch.relu(overlap - self.margin)**2
        loss = (1 - y) * loss_similar + y * loss_dissimilar
        
        return torch.mean(loss, dtype=torch.float)

class ContrastiveLoss_Quantum_Direct_2(nn.Module):
    """
    Implements a custom contrastive loss function adapted for a similarity
    score (overlap) between 0 and 1.

    The loss is defined as: L = (1-y)*(1-overlap)^2 + y*(overlap)^2
    where y=0 for similar pairs and y=1 for dissimilar pairs.
    """
    def __init__(self):
        super().__init__()

    def forward(self, overlap, y):
        """
        Calculates the contrastive loss for a batch of pairs using the overlap score.
        
        Args:
            overlap (torch.Tensor): A 1D tensor of overlap scores (0-1).
            y (torch.Tensor): A 1D tensor of ground-truth labels (0 for similar, 1 for dissimilar).
            
        Returns:
            torch.Tensor: The mean loss for the batch.
        """
        # Ensure y has the same dimensions as overlap for element-wise operations
        if y.ndim != overlap.ndim:
            y = y.view_as(overlap)

        # Loss for similar pairs (y=0) - minimizes (1 - overlap)^2,
        # encouraging overlap to be close to 1.
        loss_similar = (1 - y) * torch.pow(1 - overlap, 2)
        
        # Loss for dissimilar pairs (y=1) - minimizes overlap^2,
        # encouraging overlap to be close to 0.
        loss_dissimilar = y * torch.pow(overlap, 2)
        
        # The total loss is the average of the combined components
        loss = torch.mean(loss_similar + loss_dissimilar)
        
        return loss

class BCEOverlapLoss_Quantum(nn.Module):
    def __init__(self):
        super().__init__()
        self.loss_fn = nn.BCEWithLogitsLoss()

    def forward(self, overlap, y):
        # Map overlap from [-1, 1] → logits in R
        logits = overlap * 3  # scale to increase contrast
        return self.loss_fn(logits.squeeze(), y.float())