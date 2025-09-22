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

image_transform = transforms.Compose([
    transforms.Resize((155, 220)),
    ImageOps.invert,
    transforms.ToTensor(),
    # TODO: add normalize
])

img_h, img_w = 155, 220
batch_size = 128
log_interval = 50
num_epochs = 20
q_delta = 0.01
BHSig260_Hindi_path = "/kaggle/input/handwritten-signature-datasets/BHSig260-Hindi/BHSig260-Hindi/"
BHSig260_Bengali_path = "/kaggle/input/handwritten-signature-datasets/BHSig260-Bengali/BHSig260-Bengali/"
classical_branch_output_size = 256
num_channels = 2

n_qubits_single_channel = int(np.ceil(np.log2(classical_branch_output_size)))
n_qubits_switch = int(np.ceil(np.log2(num_channels)))
n_qubits = n_qubits_single_channel + n_qubits_switch
n_qubits_quantum_single_channel = lambda x : int(np.log2(x))

def visualize_sample_signature(dataset, img_w, img_h):
    '''Function to randomly select a signature from train set and
    print two genuine copies and one forged copy'''
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize = (10, 10))

    # k = np.random.randint(len(BHSig260_Hindi_orig_train))
    # orig_img_names = random.sample(BHSig260_Hindi_orig_train[k], 2)
    # forg_img_name = random.sample(BHSig260_Hindi_forg_train[k], 1)

    k = np.random.randint(len(dataset))
    orig_img_names = random.sample(dataset[k], 2)
    forg_img_name = random.sample(dataset[k], 1)

    orig_img1 = cv2.imread(orig_img_names[0], 0)
    orig_img2 = cv2.imread(orig_img_names[1], 0)
    forg_img = plt.imread(forg_img_name[0], 0)
    orig_img1 = cv2.resize(orig_img1, (img_w, img_h))
    orig_img2 = cv2.resize(orig_img2, (img_w, img_h))
    forg_img = cv2.resize(forg_img, (img_w, img_h))

    ax1.imshow(orig_img1, cmap = 'gray')
    ax2.imshow(orig_img2, cmap = 'gray')
    ax3.imshow(forg_img, cmap = 'gray')

    ax1.set_title('Genuine Copy')
    ax1.axis('off')
    ax2.set_title('Genuine Copy')
    ax2.axis('off')
    ax3.set_title('Forged Copy')
    ax3.axis('off')

def generate_batch(orig_groups, forg_groups, batch_size, img_w, img_h):
    '''Function to generate a batch of data with batch_size number of data points
    Half of the data points will be Genuine-Genuine pairs and half will be Genuine-Forged pairs'''
    # img_h, img_w = 155, 220  # Assuming image height and width are 155 and 220, respectively
    while True:
        orig_pairs = []
        forg_pairs = []
        gen_gen_labels = []
        gen_for_labels = []
        all_pairs = []
        all_labels = []

        # Here we create pairs of Genuine-Genuine image names and Genuine-Forged image names
        # For every person we have 24 genuine signatures, hence we have
        # 24 choose 2 (24C2)= 276 Genuine-Genuine image pairs for one person.
        # To make Genuine-Forged pairs, we pair every Genuine signature of a person
        # with 12 randomly sampled Forged signatures of the same person.
        # Thus we make 24 * 12 = 300 Genuine-Forged image pairs for one person.
        # In all we have 120 person's data in the training data.
        # Total no. of Genuine-Genuine pairs = 120 * 276 = 33120
        # Total number of Genuine-Forged pairs = 120 * 300 = 36000
        # Total no. of data points = 33120 + 36000 = 69120
        for orig, forg in zip(orig_groups, forg_groups):
            orig_pairs.extend(list(itertools.combinations(orig, 2)))
            forg_list = list(forg)  # Ensure forg is a list
            for i in range(len(forg_list)):
                forg_pairs.extend(list(itertools.product(orig[i:i + 1], random.sample(forg_list, 12))))

        # Label for Genuine-Genuine pairs is 1
        # Label for Genuine-Forged pairs is 0
        gen_gen_labels = [1] * len(orig_pairs)
        gen_for_labels = [0] * len(forg_pairs)

        # Concatenate all the pairs together along with their labels and shuffle them
        all_pairs = orig_pairs + forg_pairs
        all_labels = gen_gen_labels + gen_for_labels
        del orig_pairs, forg_pairs, gen_gen_labels, gen_for_labels
        all_pairs, all_labels = shuffle(all_pairs, all_labels)

        k = 0
        pairs = [np.zeros((batch_size, img_h, img_w, 1), dtype=np.float32) for _ in range(2)]
        targets = np.zeros((batch_size,), dtype=np.float32)

        for ix, pair in enumerate(all_pairs):
            # Ensure pair elements are strings
            path1 = pair[0].decode('utf-8') if isinstance(pair[0], bytes) else pair[0]
            path2 = pair[1].decode('utf-8') if isinstance(pair[1], bytes) else pair[1]

            img1 = cv2.imread(path1, 0)
            img2 = cv2.imread(path2, 0)
            img1 = cv2.resize(img1, (img_w, img_h))          #Resizing Images
            img2 = cv2.resize(img2, (img_w, img_h))
            img1 = np.array(img1, dtype=np.float64)
            img2 = np.array(img2, dtype=np.float64)
            img1 /= 255                                     #Normalizing Images
            img2 /= 255
            img1 = img1[..., np.newaxis]
            img2 = img2[..., np.newaxis]
            pairs[0][k, :, :, :] = img1
            pairs[1][k, :, :, :] = img2
            targets[k] = all_labels[ix]
            k += 1
            if k == batch_size:
                yield (torch.tensor(pairs[0], dtype=torch.float32), torch.tensor(pairs[1], dtype=torch.float32)), torch.tensor(targets, dtype=torch.float32)
                k = 0
                pairs = [np.zeros((batch_size, img_h, img_w, 1), dtype=np.float32) for _ in range(2)]
                targets = np.zeros((batch_size,), dtype=np.float32)

#Creating a tf Dataset from generator
def ensure_list(groups):
    return [list(group) if not isinstance(group, list) else group for group in groups]

def make_pairs_BHSig260(orig_arr, forg_arr, filename):
    o_o = []
    o_f = []
    header = ["sign1", "sign2", "label"]
    user_idx = 0

    for user_idx in range(len(orig_arr)):
    # if True:
        for i in range(len(orig_arr[user_idx])):
            for j in range(i, len(orig_arr[user_idx])):
                o_o.append([orig_arr[user_idx][i], orig_arr[user_idx][j], 0])

    for user_idx in range(len(orig_arr)):
    # if True:
        for i in range(len(orig_arr[user_idx])):
            for j in range(len(forg_arr[user_idx])):
                o_f.append([orig_arr[user_idx][i], forg_arr[user_idx][j], 1])

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(o_o)
        writer.writerows(o_f)

    # for user_1 in range(len(orig_arr)):
    #     for user_2 in range(user_1 + 1, len(orig_arr)):
    #         o_f = []
    #         for i in range(len(orig_arr[user_1])):
    #             for j in range(len(orig_arr[user_2])):
    #                 o_f.append([orig_arr[user_1][i], orig_arr[user_2][j], 1])

    #         with open(filename, 'a', newline='') as f:
    #             writer = csv.writer(f)
    #             writer.writerows(o_f)

def far_frr(predictions, labels, step=1e-3):
    '''Compute ROC accuracy with a range of thresholds on distances.
    '''
    dmax = np.max(predictions)
    dmin = np.min(predictions)
    nsame = np.sum(labels == 1)
    ndiff = np.sum(labels == 0)
    
    max_acc = 0
    best_thresh = -1

    thresholds=[]
    accuracies=[]
    tprr=[]
    tnrr=[]

    for d in np.arange(dmin, dmax+step, step):
        # print("d",d,"\n","dmin",dmin,"\tdmax",dmax,"\n step",step)

        idx1 = predictions.ravel() <= d
        idx2 = predictions.ravel() > d

        tpr = float(np.sum(labels[idx1] == 1)) / nsame
        tnr = float(np.sum(labels[idx2] == 0)) / ndiff
        acc = 0.5 * (tpr + tnr)
        #print ('ROC', acc, "tpr",tpr, "tnr",tnr)


        if (acc > max_acc):
            max_acc, best_thresh = acc, d

            thresholds.append(d)
            accuracies.append(acc)
            tprr.append(1-tpr)
            tnrr.append(1-tnr)

            #print("Max acc",max_acc,"\t best_thresh",best_thresh,"\n===============")

    # Create the line plot
    plt.plot(thresholds, accuracies, label = "Threshold")

    plt.xlabel('Threshold')
    plt.ylabel('Accuracy')
    plt.title('ROC Accuracy vs. Threshold')
    plt.legend()
    plt.grid(True)
    plt.show()

    plt.xlabel('Threshold')
    plt.ylabel('Accuracy')
    plt.title('FAR vs FRR')
    plt.plot(thresholds,tprr, label = "FAR")
    plt.plot(thresholds,tnrr, label = "FRR")
    plt.legend()
    plt.grid(True)
    plt.show()

    return max_acc, best_thresh,tprr,tnrr

def predict_score(model, test_dataset, device, threshold=0.5):
    '''Predict distance score and classify test images as Genuine or Forged'''

    # Get one batch of test samples
    BHSig260_Hindi_test_dataset_iter = iter(test_dataset)
    img1, img2, test_label = next(BHSig260_Hindi_test_dataset_iter)

    batch_size = img1.size(0)

    # Plot image pairs
    fig, axes = plt.subplots(batch_size, 2, figsize=(5, batch_size * 2))
    if batch_size == 1:
        axes = [axes]

    for i in range(batch_size):
        ax1, ax2 = axes[i]
        ax1.imshow(np.squeeze(img1[i].numpy()), cmap='gray')
        ax2.imshow(np.squeeze(img2[i].numpy()), cmap='gray')
        ax1.set_title("Genuine")
        ax2.set_title("Genuine" if test_label[i].item() == 1 else "Forged")
        ax1.axis("off")
        ax2.axis("off")

    plt.tight_layout()
    plt.show()

    # Inference
    img1, img2, test_label = img1.to(device), img2.to(device), test_label.to(device)
    model.eval()
    with torch.no_grad():
        out1, out2 = model(img1, img2)

        # Compute Euclidean distances
        distances = torch.norm(out1 - out2, dim=1)

        # Optionally interpret as probability with sigmoid
        probs = torch.sigmoid(distances)

    # Display scores and predicted class
    print("\nPredicted distance scores and classification:")
    for i in range(batch_size):
        score = distances[i].item()
        classification = "FORGED" if score > threshold else "GENUINE"
        print(f"Sample {i+1:02d}: Score = {score:.4f} → {classification}")