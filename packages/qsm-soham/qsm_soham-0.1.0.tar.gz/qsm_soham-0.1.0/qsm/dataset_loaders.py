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

class SignDataset(Dataset):
    def __init__(self, is_train: bool, data_dir: str, image_transform=None):
        if not os.path.exists(os.path.join(data_dir, 'train.csv')) or not os.path.exists(os.path.join(data_dir, 'test.csv')):
            print('Not found train/test splits, run create_annotation first')
        else:
            print('Use existed train/test splits')

        if is_train:
            self.df = pd.read_csv(os.path.join(data_dir, 'train.csv'), header=None)
        else:
            self.df = pd.read_csv(os.path.join(data_dir, 'test.csv'), header=None)

        self.image_transform = image_transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        x1, x2, y = self.df.iloc[index]

        x1 = Image.open(x1).convert('L')
        x2 = Image.open(x2).convert('L')

        if self.image_transform:
            x1 = self.image_transform(x1)
            x2 = self.image_transform(x2)

        return x1, x2, y

class CSVDataset(Dataset):
    """
    A custom PyTorch Dataset for loading image pairs and labels from a CSV file.
    """
    def __init__(self, csv_file, transform=None):
        """
        Args:
            csv_file (string): Path to the csv file with pairs and labels.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        # Read the CSV file using pandas
        self.pairs_df = pd.read_csv(csv_file)
        self.transform = transform

    def __len__(self):
        # The number of samples is the number of rows in the CSV file
        return len(self.pairs_df)

    def __getitem__(self, idx):
        # Get the file paths and label from the dataframe row
        row = self.pairs_df.iloc[idx]
        img1_path = row['sign1']
        img2_path = row['sign2']
        label = row['label']

        # Load the images
        # 'L' converts to grayscale, which is common for signature analysis
        image1 = Image.open(img1_path).convert('L')
        image2 = Image.open(img2_path).convert('L')

        # Apply transformations if provided
        if self.transform:
            image1 = self.transform(image1)
            image2 = self.transform(image2)

        # Convert label to a PyTorch tensor
        label = torch.tensor(label, dtype=torch.float32)

        return image1, image2, label

class TripletDataset(Dataset):
    def __init__(self, org_signs, forg_signs, transform=None):
        self.org_data = org_signs
        self.forg_data = forg_signs
        self.signer_ids = [i for i in range(len(org_signs))]
        self.transform = transform

    def __len__(self):
        # We'll use a large number for the length to ensure we get enough batches.
        return len(self.signer_ids) * 1000

    def __getitem__(self, index):
        # 1. Select a random anchor signer
        anchor_signer_id = random.choice(self.signer_ids)

        # anchor_signatures = self.signer_data[anchor_signer_id]['orig']
        anchor_signatures = self.org_data[anchor_signer_id]

        # 2. Select the anchor and positive images from the same signer
        anchor_path, positive_path = random.sample(anchor_signatures, 2)

        # 3. Select a negative image
        # To make the model robust, we can choose a negative from either a different
        # signer's genuine signature or a forgery of the anchor signer.

        if random.random() < 0.5 and len(self.forg_data[anchor_signer_id]) > 0:
            # Case A: Negative is a forgery of the anchor signer
            negative_path = random.choice(self.forg_data[anchor_signer_id])
        else:
            # Case B: Negative is a genuine signature from a different signer
            negative_signer_id = random.choice([sid for sid in self.signer_ids if sid != anchor_signer_id])
            negative_signatures = self.org_data[negative_signer_id]
            negative_path = random.choice(negative_signatures)

        # Load images and apply transformations
        anchor_image = Image.open(anchor_path).convert('L')
        positive_image = Image.open(positive_path).convert('L')
        negative_image = Image.open(negative_path).convert('L')

        if self.transform:
            anchor_image = self.transform(anchor_image)
            positive_image = self.transform(positive_image)
            negative_image = self.transform(negative_image)

        # Return a triplet of images
        return anchor_image, positive_image, negative_image

class TripletDataset_CL(Dataset):
    """
    A custom PyTorch Dataset that dynamically generates pairs of signatures
    (positive and negative) for training a Siamese network with contrastive loss.
    """
    def __init__(self, org_signs, forg_signs, transform=None):
        """
        Args:
            org_signs (list): A list of lists, where each sublist contains the
                              file paths of original signatures for one signer.
            forg_signs (list): A list of lists, where each sublist contains the
                               file paths of forged signatures for one signer.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.org_data = org_signs
        self.forg_data = forg_signs
        self.signer_ids = [i for i in range(len(org_signs))]
        self.transform = transform

    def __len__(self):
        # We'll use a large number for the length to ensure we get enough batches.
        # This number should be large enough to run for a full epoch.
        return len(self.signer_ids) * 1000

    def __getitem__(self, index):
        # Dynamically generate a positive or negative pair with a 50% chance
        is_positive = random.random() < 0.5

        if is_positive:
            # Create a positive pair (label 0)
            signer_id = random.choice(self.signer_ids)
            signatures = self.org_data[signer_id]

            # Select two different original signatures from the same signer
            # Ensure there are at least two signatures to sample from
            if len(signatures) < 2:
                # Handle cases with too few signatures by falling back to a different signer
                return self.__getitem__(random.randint(0, self.__len__() - 1))

            img1_path, img2_path = random.sample(signatures, 2)
            label = 0

        else:
            # Create a negative pair (label 1)
            # To make the model robust, we mix between genuine-forged and genuine-genuine pairs
            if random.random() < 0.5:
                # Case A: Genuine-forged pair from a single signer
                signer_id = random.choice(self.signer_ids)
                orig_sigs = self.org_data[signer_id]
                forg_sigs = self.forg_data[signer_id]

                # Ensure both lists are not empty
                if not orig_sigs or not forg_sigs:
                    return self.__getitem__(random.randint(0, self.__len__() - 1))

                img1_path = random.choice(orig_sigs)
                img2_path = random.choice(forg_sigs)
            else:
                # Case B: Genuine-genuine pair from two different signers
                signer_id1, signer_id2 = random.sample(self.signer_ids, 2)
                orig_sigs1 = self.org_data[signer_id1]
                orig_sigs2 = self.org_data[signer_id2]

                if not orig_sigs1 or not orig_sigs2:
                    return self.__getitem__(random.randint(0, self.__len__() - 1))

                img1_path = random.choice(orig_sigs1)
                img2_path = random.choice(orig_sigs2)

            label = 1

        # Load images and apply transformations
        img1 = Image.open(img1_path).convert('L')
        img2 = Image.open(img2_path).convert('L')

        if self.transform:
            img1 = self.transform(img1)
            img2 = self.transform(img2)

        # The label for contrastive loss should be a float tensor
        label_tensor = torch.tensor(label, dtype=torch.float32)

        return img1, img2, label_tensor

class SiameseBHSigDataset(IterableDataset):
    def __init__(self, orig_groups, forg_groups, batch_size=32, img_h=155, img_w=220):
        self.orig_groups = [list(g) for g in orig_groups]
        self.forg_groups = [list(g) for g in forg_groups]
        self.batch_size = batch_size
        self.img_h = img_h
        self.img_w = img_w

    def generate_batches(self):
        while True:
        # if True:
            orig_pairs = []
            forg_pairs = []

            for orig, forg in zip(self.orig_groups, self.forg_groups):
                # Genuine-Genuine pairs (24C2 = 276 per person)
                orig_pairs.extend(list(itertools.combinations(orig, 2)))
                # Genuine-Forged pairs (24 * 12 = 300 per person)
                for i in range(len(orig)):
                    forg_pairs.extend([(orig[i], f) for f in random.sample(forg, 12)])

            all_pairs = orig_pairs + forg_pairs
            all_labels = [1] * len(orig_pairs) + [0] * len(forg_pairs)
            all_pairs, all_labels = shuffle(all_pairs, all_labels)

            k = 0
            pairs = [np.zeros((self.batch_size, self.img_h, self.img_w, 1), dtype=np.float32) for _ in range(2)]
            targets = np.zeros((self.batch_size,), dtype=np.float32)

            print("length of all_pairs:", len(all_pairs))
            print("length of all_labels:", len(all_labels))

            for (img1_path, img2_path), label in zip(all_pairs, all_labels):
                # Load and preprocess images
                img1 = cv2.imread(img1_path, 0)
                img2 = cv2.imread(img2_path, 0)
                img1 = cv2.resize(img1, (self.img_w, self.img_h)) / 255.0
                img2 = cv2.resize(img2, (self.img_w, self.img_h)) / 255.0
                img1 = img1[..., np.newaxis]
                img2 = img2[..., np.newaxis]

                pairs[0][k] = img1
                pairs[1][k] = img2
                targets[k] = label
                k += 1

                if k == self.batch_size:
                    # Convert to PyTorch tensors
                    x1 = torch.tensor(pairs[0], dtype=torch.float32).permute(0, 3, 1, 2)  # (B, C, H, W)
                    x2 = torch.tensor(pairs[1], dtype=torch.float32).permute(0, 3, 1, 2)
                    y = torch.tensor(targets, dtype=torch.float32)
                    yield x1, x2, y
                    # Reset for next batch
                    k = 0
                    pairs = [np.zeros((self.batch_size, self.img_h, self.img_w, 1), dtype=np.float32) for _ in range(2)]
                    targets = np.zeros((self.batch_size,), dtype=np.float32)

    def __iter__(self):
        return iter(self.generate_batches())