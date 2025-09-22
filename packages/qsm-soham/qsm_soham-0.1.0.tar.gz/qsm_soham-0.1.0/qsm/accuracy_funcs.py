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

def accuracy(distances, y, step=0.01):
    min_threshold_d = min(distances)
    max_threshold_d = max(distances)
    max_acc = 0
    best_thresh = 0
    same_id = (y == 1)

    for threshold_d in torch.arange(min_threshold_d, max_threshold_d+step, step):
        true_positive = (distances <= threshold_d) & (same_id)
        true_positive_rate = true_positive.sum().float() / same_id.sum().float()
        true_negative = (distances > threshold_d) & (~same_id)
        true_negative_rate = true_negative.sum().float() / (~same_id).sum().float()

        acc = 0.5 * (true_negative_rate + true_positive_rate)

        if acc > max_acc:
            max_acc = acc
            best_thresh = threshold_d
        # max_acc = max(max_acc, acc)
    return max_acc, best_thresh

def accuracy_triplet(anchor_embeddings, positive_embeddings, negative_embeddings, threshold=None):
    """
    Calculates the accuracy of a triplet network by comparing the distances.
    A triplet is considered "correct" if the distance from anchor to positive
    is less than the distance from anchor to negative.

    Args:
        anchor_embeddings (torch.Tensor): Embeddings of the anchor images.
        positive_embeddings (torch.Tensor): Embeddings of the positive images.
        negative_embeddings (torch.Tensor): Embeddings of the negative images.

    Returns:
        float: The accuracy as a percentage.
    """
    # Calculate the distances for all triplets
    dist_positive = torch.pairwise_distance(anchor_embeddings, positive_embeddings, p=2)
    dist_negative = torch.pairwise_distance(anchor_embeddings, negative_embeddings, p=2)

    # A prediction is correct if dist_positive < dist_negative
    correct_predictions = (dist_positive < dist_negative).sum().item()
    total_triplets = len(anchor_embeddings)

    return (correct_predictions / total_triplets) * 100

def accuracy_triplet__quantum(anchor_embeddings, dist_positive, dist_negative, threshold=None):
    """
    Calculates the accuracy of a triplet network by comparing the distances.
    A triplet is considered "correct" if the distance from anchor to positive
    is less than the distance from anchor to negative.

    Args:
        anchor_embeddings (torch.Tensor): Embeddings of the anchor images.
        positive_embeddings (torch.Tensor): Embeddings of the positive images.
        negative_embeddings (torch.Tensor): Embeddings of the negative images.

    Returns:
        float: The accuracy as a percentage.
    """
    # Calculate the distances for all triplets
    # dist_positive = torch.pairwise_distance(anchor_embeddings, positive_embeddings, p=2)
    # dist_negative = torch.pairwise_distance(anchor_embeddings, negative_embeddings, p=2)

    # A prediction is correct if dist_positive < dist_negative
    correct_predictions = (dist_positive > dist_negative).sum().item()
    total_triplets = len(anchor_embeddings)

    return (correct_predictions / total_triplets) * 100

def accuracy_contrastive_loss(distances, labels):
    """
    Calculates the optimal accuracy for a Siamese network trained with
    contrastive loss by finding the best threshold.

    Args:
        distances (torch.Tensor): A 1D tensor of distances between image pairs.
        labels (torch.Tensor): A 1D tensor of ground-truth labels (0 for similar, 1 for dissimilar).

    Returns:
        tuple: A tuple containing the maximum accuracy (float) and the
               corresponding best threshold (float).
    """
    max_accuracy = 0.0
    best_threshold = 0.0

    # Sort distances to iterate through all possible thresholds efficiently
    distances_sorted, _ = torch.sort(distances)

    for threshold in distances_sorted:
        # A pair is predicted as similar if its distance is <= threshold
        predictions = (distances <= threshold).float()

        # Calculate True Positives and True Negatives
        # True Positives: correct similar prediction (label=0, pred=0)
        # True Negatives: correct dissimilar prediction (label=1, pred=1)
        # predictions = 1 - predictions because label is 0 for similar, 1 for dissimilar
        tp = ((labels == 0) & (predictions == 1)).sum().item()
        tn = ((labels == 1) & (predictions == 0)).sum().item()

        accuracy = (tp + tn) / len(labels)

        if accuracy > max_accuracy:
            max_accuracy = accuracy
            best_threshold = threshold.item()

    return max_accuracy * 100, best_threshold