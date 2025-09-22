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

import helper_funcs
from helper_funcs import q_delta, n_qubits_single_channel

import quantum_circuits
from quantum_circuits import I_Block_Vanilla__1to1, I_Block_AmplitudeEnc__variational_swap_cyclic_ansatz__w_per_pre_post_VQC, \
    AmpEmb__pre__c_post_VQC__switch_ry, circuit__1, circuit__1__AngleEmbedding

class SigNet__I_Block(nn.Module):
    def __init__(self):
        super(SigNet__I_Block, self).__init__()
        self.q_params = nn.Parameter(q_delta * torch.randn(n_qubits_single_channel))

        self.cnn1 = nn.Sequential(
            # nn.ReflectionPad2d(1),
            nn.Conv2d(1, 4, kernel_size=11),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(4),
            nn.MaxPool2d(2),

            # nn.ReflectionPad2d(1),
            nn.Conv2d(4, 4, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(4),
            nn.MaxPool2d(2),

            # nn.ReflectionPad2d(1),
            nn.Conv2d(4, 8, kernel_size=3),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(8),
            nn.MaxPool2d(2),
        )

        dummy_input = torch.zeros(1, 1, 155, 220)  # adjust size according to your input
        out = self.cnn1(dummy_input)
        flattened_size = out.view(1, -1).size(1)

        print("shape:", flattened_size)

        self.fc1 = nn.Sequential(
            nn.Linear(flattened_size, 1024),
            nn.ReLU(inplace=True),

            nn.Linear(1024, 128),
            nn.ReLU(inplace=True),

            nn.Linear(128, 4)
        )

        self.post_quantum = nn.Sequential(
            nn.Linear(4, 16),
            nn.ReLU(inplace=True),

            nn.Linear(16, 32),
            nn.ReLU(inplace=True),

            nn.Linear(32, 64)
        )

    def forward_once(self, x):
        output = self.cnn1(x)
        output = output.view(output.size()[0], -1)
        output = self.fc1(output)
        return output

    def forward(self, input1, input2):
        # Get classical feature vectors from CNN+FC pipeline
        output1 = self.forward_once(input1)  # shape: [batch_size, embedding_size]
        output2 = self.forward_once(input2)

        batch_size = output1.size(0)
        q_out_1_all = []
        q_out_2_all = []

        for i in range(batch_size):
            # Concatenate the two embeddings for this instance
            q_input_1 = output1[i]
            q_input_2 = output2[i]

            # Quantum processing (returns two tuples)
            q_out_1, q_out_2 = I_Block_Vanilla__1to1(n_qubits=8)(q_input_1, q_input_2, self.q_params, final_hadamard=True)

            # Convert from tuple to tensor and add batch dimension
            q_out_1_tensor = torch.stack(q_out_1).unsqueeze(0)  # shape: [1, n_qubits_single_channel]
            q_out_2_tensor = torch.stack(q_out_2).unsqueeze(0)

            q_out_1_all.append(q_out_1_tensor)
            q_out_2_all.append(q_out_2_tensor)

        # Combine all quantum outputs into batch tensors
        q_out_1_all = torch.cat(q_out_1_all, dim=0).float()  # shape: [batch_size, n_qubits_single_channel]
        q_out_2_all = torch.cat(q_out_2_all, dim=0).float()

        # apply post-quantum layers to calculate the contrastive loss (only one classical loss function)
        output1 = self.post_quantum(q_out_1_all)
        output2 = self.post_quantum(q_out_2_all)

        return output1, output2

    # def forward(self, input1, input2):
    #     output1 = self.forward_once(input1)
    #     output2 = self.forward_once(input2)

    #     q_out_1 = torch.Tensor(0, n_qubits_single_channel)
    #     q_out_2 = torch.Tensor(0, n_qubits_single_channel)

    #     q_out_1 = q_out_1.to(device)
    #     q_out_2 = q_out_2.to(device)

    #     for elem in q_in:
    #         q_out_elem = torch.hstack(I_Block_Vanilla__1to1(elem, elem, self.q_params)).float().unsqueeze(0)
    #         q_out = torch.cat((q_out, q_out_elem))

    #     return output1, output2

class SigNet2__I8_Block(nn.Module):
    '''
    Reference Keras: https://github.com/sounakdey/SigNet/blob/master/SigNet_v1.py
    '''
    def __init__(self):
        super().__init__()
        self.quantum_weights = {"q_weights_flat": (2*n_qubits_single_channel),
                                "pre_per_channel_VQC_weights": (2, n_qubits_single_channel, 3),
                                "post_per_channel_VQC_weights": (2, n_qubits_single_channel, 3)}
        self.qlayer = qml.qnn.TorchLayer(I_Block_AmplitudeEnc__variational_swap_cyclic_ansatz__w_per_pre_post_VQC(8), self.quantum_weights)

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
            nn.Linear(1024, 512),
            nn.Dropout2d(p=0.5),
            nn.Linear(512, 256)
            # nn.Dropout2d(p=0.5),
            # self.qlayer,
            # nn.Linear(8, 16),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(16, 32)
        )

        self.post_quantum = nn.Sequential(
            nn.Linear(8, 16),
            nn.Dropout2d(p=0.5),
            nn.Linear(16, 32)
        )

        # TODO: init bias = 0

    def forward(self, x1, x2):
        output1 = torch.tanh(self.features(x1))
        output2 = torch.tanh(self.features(x2))

        # print("output1:", output1)
        # print("output2:", output2)

        # batch_size = output1.size(0)

        # outputs_stacked = torch.stack([output1, output2], dim=0)
        # outputs_stacked = outputs_stacked.permute(1, 0, 2)
        # outputs_stacked = outputs_stacked.reshape(outputs_stacked.shape[0], outputs_stacked.shape[1]*outputs_stacked.shape[2])
        # print("shape of outputs_stacked:", outputs_stacked.shape)

        # q_out_1_all, q_out_2_all = self.qlayer(outputs_stacked)
        # # print("shape of q_layer_output:", q_out_1_all.shape, q_out_2_all.shape)

        # # Combine all quantum outputs into batch tensors
        # # q_out_1_all = torch.cat(q_out_1_all, dim=0).float()  # shape: [batch_size, n_qubits_single_channel]
        # # q_out_2_all = torch.cat(q_out_2_all, dim=0).float()

        # q_out_1_all = torch.tanh(q_out_1_all)
        # q_out_2_all = torch.tanh(q_out_2_all)

        # q_out_1_all = q_out_1_all.float()
        # q_out_2_all = q_out_2_all.float()

        # # print("q_out_1_all:", q_out_1_all)
        # # print("q_out_2_all:", q_out_2_all)

        # # apply post-quantum layers to calculate the contrastive loss (only one classical loss function)
        # output1 = self.post_quantum(q_out_1_all)
        # output2 = self.post_quantum(q_out_2_all)

        return output1, output2

class SigNet2__Amp_Vanilla__Block(nn.Module):
    '''
    Reference Keras: https://github.com/sounakdey/SigNet/blob/master/SigNet_v1.py
    '''
    def __init__(self):
        super().__init__()
        # self.quantum_weights = {"theta_RY_switch": (1),
        #                         "pre_vqc_weights": (2, n_qubits_single_channel, 3),
        #                         "post_vqc_weights": (2, n_qubits_single_channel, 3)}
        self.quantum_weights = {"pre_vqc_weights_A": (2, n_qubits_single_channel, 3),
                                "pre_vqc_weights_B": (2, n_qubits_single_channel, 3),
                                "post_vqc_weights_A": (2, n_qubits_single_channel, 3),
                                "post_vqc_weights_B": (2, n_qubits_single_channel, 3),
                                "pre_vqc_weights_C": (2, n_qubits_single_channel, 3),
                                "pre_vqc_weights_D": (2, n_qubits_single_channel, 3),
                                "post_vqc_weights_C": (2, n_qubits_single_channel, 3),
                                "post_vqc_weights_D": (2, n_qubits_single_channel, 3)}

        # self.qlayer = qml.qnn.TorchLayer(AmpEmb__Vanilla__pre_post_VQC__switch_ry, self.quantum_weights)
        self.qlayer = qml.qnn.TorchLayer(AmpEmb__pre__c_post_VQC__switch_ry(8), self.quantum_weights)

        self.features = nn.Sequential(
            #input size = [155, 220, 1]
            nn.Conv2d(1, 32, 11), # size = [145,210]
            nn.ReLU(),
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [72, 105]
            nn.Conv2d(32, 48, 5, padding=2, padding_mode='zeros'), # size = [72, 105]
            nn.LocalResponseNorm(size=5, k=2, alpha=1e-4, beta=0.75),
            nn.MaxPool2d(2, stride=2), # size = [36, 52]
            nn.Dropout2d(p=0.3),
            nn.Conv2d(48, 64, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.Conv2d(64, 48, 3, stride=1, padding=1, padding_mode='zeros'),
            nn.MaxPool2d(2, stride=2), # size = [18, 26]
            nn.Dropout2d(p=0.3),
            nn.Flatten(1, -1), # 18*26*256
            nn.Linear(18*26*48, 2048),
            nn.Dropout2d(p=0.5),
            nn.Linear(2048, 1024)
            # nn.Dropout2d(p=0.5),
            # nn.Linear(1024, 512)
            # nn.Dropout2d(p=0.5),
            # self.qlayer,
            # nn.Linear(8, 16),
            # nn.Dropout2d(p=0.5),
            # nn.Linear(16, 32)
        )

        self.post_quantum = nn.Sequential(
            nn.Linear(8, 16),
            nn.Dropout2d(p=0.5),
            nn.Linear(16, 32)
        )

        # TODO: init bias = 0

    def forward(self, x1, x2):
        # output1 = self.features(x1)
        # output2 = self.features(x2)

        output1 = torch.tanh(self.features(x1))
        output2 = torch.tanh(self.features(x2))

        # print("output1:", output1)
        # print("output2:", output2)

        batch_size = output1.size(0)

        output1 = F.normalize(output1, p=2, dim=1) / np.sqrt(2)
        output2 = F.normalize(output2, p=2, dim=1) / np.sqrt(2)

        outputs_stacked = torch.stack([output1, output2], dim=0)
        outputs_stacked = outputs_stacked.permute(1, 0, 2)
        outputs_stacked = outputs_stacked.reshape(outputs_stacked.shape[0], outputs_stacked.shape[1]*outputs_stacked.shape[2])
        # print("shape of outputs_stacked:", outputs_stacked.shape)

        state_overlap = self.qlayer(outputs_stacked)
        # print("shape of q_layer_output:", q_out_1_all.shape, q_out_2_all.shape)

        # # Combine all quantum outputs into batch tensors
        # # q_out_1_all = torch.cat(q_out_1_all, dim=0).float()  # shape: [batch_size, n_qubits_single_channel]
        # # q_out_2_all = torch.cat(q_out_2_all, dim=0).float()

        # q_out_1_all = torch.tanh(q_out_1_all)
        # q_out_2_all = torch.tanh(q_out_2_all)

        # q_out_1_all = q_out_1_all.float()
        # q_out_2_all = q_out_2_all.float()

        # # print("q_out_1_all:", q_out_1_all)
        # # print("q_out_2_all:", q_out_2_all)

        # # apply post-quantum layers to calculate the contrastive loss (only one classical loss function)
        # output1 = self.post_quantum(q_out_1_all)
        # output2 = self.post_quantum(q_out_2_all)

        # return output1, output2

        return state_overlap

class SigNet__Circuit_1(nn.Module):
    def __init__(self):
        super().__init__()
        self.quantum_weights = {"theta_RY_switch": (3, 3),
                                "vqc_weights": (3, 2, 7, 3)}

        self.qlayer = qml.qnn.TorchLayer(circuit__1(bool_vals=None), self.quantum_weights)

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
            nn.Linear(1024, 256),
        )

    def forward(self, x1, x2):
        x1 = self.features(x1)
        x2 = self.features(x2)

        x1 = F.normalize(x1, p=2, dim=1) / np.sqrt(2)
        x2 = F.normalize(x2, p=2, dim=1) / np.sqrt(2)

        quantum_input = torch.cat((x1, x2), dim=1)
        quantum_output = self.qlayer(quantum_input)

        # final_out = nn.Sigmoid()(quantum_output)

        return (1 + quantum_output) / 2
        # return final_out

        # return x1, x2

class SigNet_Half__Circuit_1(nn.Module):
    def __init__(self):
        super().__init__()
        self.quantum_weights = {"theta_RY_switch": (3, 3),
                                "vqc_weights": (3, 1, 7, 3)}

        self.qlayer = qml.qnn.TorchLayer(qml.transforms.broadcast_expand(circuit__1(bool_vals=None)), self.quantum_weights)

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

        x1 = F.normalize(x1, p=2, dim=1) / np.sqrt(2)
        x2 = F.normalize(x2, p=2, dim=1) / np.sqrt(2)

        quantum_input = torch.cat((x1, x2), dim=1)
        quantum_output = self.qlayer(quantum_input)

        # final_out = nn.Sigmoid()(quantum_output)
        # print("quantum_output:", quantum_output)

        return (1 + quantum_output) / 2
        # return final_out

        # return x1, x2

class SigNet_Half__Circuit_1__AngEnc(nn.Module):
    def __init__(self):
        super().__init__()
        self.quantum_weights = {"theta_RY_switch": (3, 3),
                                "vqc_weights": (3, 2, 8, 3)}

        self.qlayer = qml.qnn.TorchLayer(circuit__1__AngleEmbedding(), self.quantum_weights)

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
            nn.Linear(512, 7),
        )

    def forward(self, x1, x2):
        x1 = self.features(x1)
        x2 = self.features(x2)

        # x1 = F.normalize(x1, p=2, dim=1) / np.sqrt(2)
        # x2 = F.normalize(x2, p=2, dim=1) / np.sqrt(2)
        x1 = F.normalize(x1, p=2, dim=1) * np.pi
        x2 = F.normalize(x2, p=2, dim=1) * np.pi

        quantum_input = torch.cat((x1, x2), dim=1)
        quantum_output = self.qlayer(quantum_input)

        # final_out = nn.Sigmoid()(quantum_output)

        return (1 + quantum_output) / 2
        # return final_out

        # return x1, x2