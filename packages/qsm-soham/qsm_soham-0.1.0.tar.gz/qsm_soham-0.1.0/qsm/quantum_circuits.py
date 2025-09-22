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
from helper_funcs import n_qubits_quantum_single_channel, n_qubits_single_channel


def qml_RZZ(swap_angle, wires):
    qml.CNOT(wires=wires)
    qml.RZ(swap_angle, wires=wires[1])
    qml.CNOT(wires=wires)

# @qml.qnode(dev, interface="torch")
def I_Block_Vanilla__1to1(n_qubits):
    dev = qml.device("default.qubit", n_qubits)

    def circuit(q_input_features_input1, q_input_features_input2, q_variational_swaps, pre_hadamard=False, final_hadamard=False):
        # encoding the outputs from the
        for i in range(n_qubits_single_channel):
            qml.RY(q_input_features_input1[i]*2*np.pi, wires=i)
        for i in range(n_qubits_single_channel, 2*n_qubits_single_channel):
            qml.RY(q_input_features_input2[i - n_qubits_single_channel]*2*np.pi, wires=i)

        # CNOT blocks
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # parametric interference
        for i in range(n_qubits_single_channel):
            # decomposing the RZZ gate; not available in PennyLane as of 27 May 2025
            # qml.CNOT(wires=[i, i + n_qubits_single_channel])
            # qml.RZ(q_variational_swaps[i]*2*np.pi, wires=i + n_qubits_single_channel)
            # qml.CNOT(wires=[i, i + n_qubits_single_channel])

            qml_RZZ(q_variational_swaps[i]*2*np.pi, wires=[i, i + n_qubits_single_channel])

        # if final_hadamard:
        #     for i in range(n_qubits):
        #         qml.Hadamard(wires=i)

        # CNOT blocks
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        if final_hadamard:
            for i in range(n_qubits):
                qml.Hadamard(wires=i)

        expvals = [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        return tuple(expvals[:n_qubits_single_channel]), tuple(expvals[n_qubits_single_channel:])
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def I_Block_AmplitudeEnc__variational_swap_cyclic_ansatz__w_per_pre_post_VQC(n_qubits):
    dev = qml.device("default.qubit", n_qubits)
    def circuit(inputs, q_weights_flat, pre_per_channel_VQC_weights, post_per_channel_VQC_weights):
        q_input_features_input1 = inputs[:, :2**n_qubits_single_channel]
        q_input_features_input2 = inputs[:, 2**n_qubits_single_channel:]

        # some hyper-params
        pre_per_channel_VQC = True
        post_per_channel_VQC = True
        pre_per_channel_VQC_depth = 2
        post_per_channel_VQC_depth = 2
        q_depth = 3
        pre_hadamard = False
        final_hadamard = False

        # # encoding the outputs from the
        # for i in range(n_qubits_single_channel):
        #     qml.RY(q_input_features_input1[:, i]*np.pi, wires=i)
        # for i in range(n_qubits_single_channel, 2*n_qubits_single_channel):
        #     qml.RY(q_input_features_input2[:, i - n_qubits_single_channel]*np.pi, wires=i)

        # encoding using Amplitude Embedding
        q_input_features_input1 = F.normalize(q_input_features_input1, p=2, dim=1)
        q_input_features_input2 = F.normalize(q_input_features_input2, p=2, dim=1)
        # state_vector = torch.cat((q_input_features_input1, q_input_features_input2), dim=1)

        qml.AmplitudeEmbedding(features=q_input_features_input1, wires=[i for i in range(n_qubits_single_channel)], normalize=True)
        # qml.AmplitudeEmbedding(features=q_input_features_input2, wires=[i for i in range(n_qubits_single_channel, 2*n_qubits_single_channel, 1)], normalize=True)

        # # CNOT blocks
        # for i in range(n_qubits_single_channel):
        #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        # for i in range(n_qubits_single_channel):
        #     qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # per-channel pre VQC
        if pre_per_channel_VQC and (pre_per_channel_VQC_weights is not None):
            # pre_per_channel_VQC_weights = pre_per_channel_VQC_weights.reshape(pre_per_channel_VQC_depth, n_qubits_single_channel, 3)

            for layer_idx in range(pre_per_channel_VQC_depth):
                for qubit_idx in range(n_qubits_single_channel):
                    qml.U3(*pre_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=qubit_idx)
                    qml.U3(*pre_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=n_qubits_single_channel+qubit_idx)

                # CNOT blocks
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # # parametric interference - from one wire in upper branch to all in lower branch, all different
        # for i in range(n_qubits_single_channel):
        #     for j in range(n_qubits_single_channel):
        #         qml_RZZ(q_variational_swaps[i+j]*2*np.pi, wires=[i, j + n_qubits_single_channel])

        # parametric interference - VQC for weight mixing
        # adding the cyclic CP gates
        wire_selector = lambda x : (x//2) + (x%2)*n_qubits_single_channel
        for angle_idx, angle in enumerate(q_weights_flat):
            control = wire_selector(angle_idx)
            target = wire_selector((angle_idx+1)%n_qubits)

            qml.ctrl(qml.RY, control=control)(angle, wires=target)

        # # add the circuit for the VQC (hardware-efficient ansatz)
        # q_weights = q_weights_flat.reshape(q_depth, n_qubits, 3)
        # for layer_idx in range(q_depth):
        #     for qubit_idx in range(n_qubits):
        #         qml.U3(q_weights[layer_idx, qubit_idx, :], wires=qubit_idx)

        #     # hardware-efficient ensatz
        #     for qubit_idx in range(0, n_qubits, 2):
        #         qml.CNOT(wires=[qubit_idx, qubit_idx + 1])
        #     for qubit_idx in range(1, n_qubits, 2):
        #         qml.CNOT(wires=[qubit_idx, (qubit_idx + 1) % n_qubits])

        # if final_hadamard:
        #     for i in range(n_qubits):
        #         qml.Hadamard(wires=i)

        # # CNOT blocks
        # for i in range(n_qubits_single_channel):
        #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        # for i in range(n_qubits_single_channel):
        #     qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # per-channel post VQC
        if post_per_channel_VQC and (post_per_channel_VQC_weights is not None):
            # post_per_channel_VQC_weights = post_per_channel_VQC_weights.reshape(post_per_channel_VQC_depth, n_qubits_single_channel, 3)

            for layer_idx in range(post_per_channel_VQC_depth):
                for qubit_idx in range(n_qubits_single_channel):
                    qml.U3(*post_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=qubit_idx)
                    qml.U3(*post_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=n_qubits_single_channel+qubit_idx)

                # CNOT blocks
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        if final_hadamard:
            for i in range(n_qubits):
                qml.Hadamard(wires=i)

        expvals =  [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        # return tuple(expvals)
        return expvals[:n_qubits_single_channel], expvals[n_qubits_single_channel:]
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def circuit__1__AngleEmbedding(n_qubits_main=512, s_dagger=False):
    n_qubits = n_qubits_quantum_single_channel(n_qubits_main)
    dev = qml.device("default.qubit", n_qubits)
    kappa = 1
    random_inds = sorted(np.random.choice(n_qubits - 1, size=kappa, replace=False))

    def circuit(inputs, theta_RY_switch, vqc_weights):
        # vqc_weights shape: (num_blocks, num_layers_per_block, num_wires, 3)
        switch = n_qubits - 1
        if s_dagger:
            qml.adjoint(qml.S(wires=switch))

        num_vqc_blocks = vqc_weights.shape[0]
        num_layers_per_block = vqc_weights.shape[1]
        num_wires_vqc = vqc_weights.shape[2]
        # print(num_wires_vqc, switch)
        assert num_wires_vqc == switch

        qml.Hadamard(wires=switch)
        # print("shape of input for circuit__1:", inputs.shape)

        # assuming that the input is normalized in the specific way
        # qml.AmplitudeEmbedding(features=inputs, wires=[w for w in range(n_qubits)], normalize=False)
        qml.ctrl(qml.AngleEmbedding, switch, control_values=(0))(features=inputs[:, :switch], wires=[w for w in range(switch)], rotation='Y')
        qml.ctrl(qml.AngleEmbedding, switch, control_values=(1))(features=inputs[:, switch:], wires=[w for w in range(switch)], rotation='Y')
        
        # qml.MottonenStatePreparation(state_vector=inputs, wires=[w for w in range(n_qubits)])

        # if (pre_vqc is True) and (pre_vqc_weights is not None):
        if True:
            for b in range(num_vqc_blocks):
                # qml.StronglyEntanglingLayers(weights=vqc_weights[b], wires=range(switch))

                for l in range(num_layers_per_block):
                    for q in range(num_wires_vqc):
                        qml.U3(*vqc_weights[b, l, q, :], wires=q)

                # # cyclic CNOT on 8
                # for i in range(n_qubits_single_channel):
                #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                # hardware-efficient CNOT on 8
                for i in range(0, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])
                for i in range(1, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])

                # qml.ctrl(qml.RX, (b % switch), control_values=(1))(theta_RY_switch[b], wires=switch)
                qml.ctrl(qml.U3, random_inds, control_values=(1 for _ in range(kappa)))(*theta_RY_switch[b], wires=switch)

        # final overlap
        qml.Hadamard(wires=switch)
        return qml.expval(qml.PauliZ(wires=switch))
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def type2_classical_quantum__single_branch(num_single_channel=128):
    n_qubits = n_qubits_quantum_single_channel(num_single_channel)
    dev = qml.device("default.qubit", n_qubits)

    def circuit(inputs, vqc_weights):
        # vqc_weights shape: (num_blocks, num_wires, 3)
        num_vqc_blocks = vqc_weights.shape[0]
        num_wires_vqc = vqc_weights.shape[1]

        # assuming that the input is normalized in the specific way
        qml.AmplitudeEmbedding(features=inputs, wires=[w for w in range(n_qubits)], normalize=True)

        if (vqc_weights is not None):
        # if True:
            for l in range(num_vqc_blocks):
                for q in range(num_wires_vqc):
                    qml.U3(*vqc_weights[l, q, :], wires=q)

                # # cyclic CNOT on 8
                # for i in range(n_qubits_single_channel):
                #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                # hardware-efficient CNOT on 8
                for i in range(0, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])
                for i in range(1, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])
        
        return [qml.expval(qml.PauliZ(wires=i)) for i in range(num_wires_vqc)]
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def I_Block_Vanilla__variational_swap_cyclic_ansatz__w_per_pre_post_VQC(n_qubits):
    dev = qml.device("default.qubit", n_qubits)

    def circuit(inputs, q_weights_flat, pre_per_channel_VQC_weights, post_per_channel_VQC_weights):
        q_input_features_input1 = inputs[:, :n_qubits_single_channel]
        q_input_features_input2 = inputs[:, n_qubits_single_channel:]

        # some hyper-params
        pre_per_channel_VQC = True
        post_per_channel_VQC = True
        pre_per_channel_VQC_depth = 2
        post_per_channel_VQC_depth = 2
        q_depth = 3
        pre_hadamard = False
        final_hadamard = False

        # encoding the outputs from the
        for i in range(n_qubits_single_channel):
            qml.RY(q_input_features_input1[:, i]*np.pi, wires=i)
        for i in range(n_qubits_single_channel, 2*n_qubits_single_channel):
            qml.RY(q_input_features_input2[:, i - n_qubits_single_channel]*np.pi, wires=i)

        # CNOT blocks
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # per-channel pre VQC
        if pre_per_channel_VQC and (pre_per_channel_VQC_weights is not None):
            # pre_per_channel_VQC_weights = pre_per_channel_VQC_weights.reshape(pre_per_channel_VQC_depth, n_qubits_single_channel, 3)

            for layer_idx in range(pre_per_channel_VQC_depth):
                for qubit_idx in range(n_qubits_single_channel):
                    qml.U3(*pre_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=qubit_idx)
                    qml.U3(*pre_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=n_qubits_single_channel+qubit_idx)

                # CNOT blocks
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # # parametric interference - from one wire in upper branch to all in lower branch, all different
        # for i in range(n_qubits_single_channel):
        #     for j in range(n_qubits_single_channel):
        #         qml_RZZ(q_variational_swaps[i+j]*2*np.pi, wires=[i, j + n_qubits_single_channel])

        # parametric interference - VQC for weight mixing
        # adding the cyclic CP gates
        wire_selector = lambda x : (x//2) + (x%2)*n_qubits_single_channel
        for angle_idx, angle in enumerate(q_weights_flat):
            control = wire_selector(angle_idx)
            target = wire_selector((angle_idx+1)%n_qubits)

            qml.ctrl(qml.RY, control=control)(angle, wires=target)

        # # add the circuit for the VQC (hardware-efficient ansatz)
        # q_weights = q_weights_flat.reshape(q_depth, n_qubits, 3)
        # for layer_idx in range(q_depth):
        #     for qubit_idx in range(n_qubits):
        #         qml.U3(q_weights[layer_idx, qubit_idx, :], wires=qubit_idx)

        #     # hardware-efficient ensatz
        #     for qubit_idx in range(0, n_qubits, 2):
        #         qml.CNOT(wires=[qubit_idx, qubit_idx + 1])
        #     for qubit_idx in range(1, n_qubits, 2):
        #         qml.CNOT(wires=[qubit_idx, (qubit_idx + 1) % n_qubits])

        # if final_hadamard:
        #     for i in range(n_qubits):
        #         qml.Hadamard(wires=i)

        # CNOT blocks
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        for i in range(n_qubits_single_channel):
            qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        # per-channel post VQC
        if post_per_channel_VQC and (post_per_channel_VQC_weights is not None):
            # post_per_channel_VQC_weights = post_per_channel_VQC_weights.reshape(post_per_channel_VQC_depth, n_qubits_single_channel, 3)

            for layer_idx in range(post_per_channel_VQC_depth):
                for qubit_idx in range(n_qubits_single_channel):
                    qml.U3(*post_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=qubit_idx)
                    qml.U3(*post_per_channel_VQC_weights[layer_idx, qubit_idx, :], wires=n_qubits_single_channel+qubit_idx)

                # CNOT blocks
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(n_qubits_single_channel):
                    qml.CNOT(wires=[n_qubits_single_channel+i, n_qubits_single_channel+((i+1)%n_qubits_single_channel)])

        if final_hadamard:
            for i in range(n_qubits):
                qml.Hadamard(wires=i)

        expvals =  [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        # return tuple(expvals)
        return expvals[:n_qubits_single_channel], expvals[n_qubits_single_channel:]
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def AmpEmb__Vanilla__pre_post_VQC__switch_ry(n_qubits):
    dev = qml.device("default.qubit", n_qubits)

    def circuit(inputs, theta_RY_switch, pre_vqc_weights, post_vqc_weights):
        num_pre_vqc_layers = pre_vqc_weights.shape[0]
        num_post_vqc_layers = post_vqc_weights.shape[0]
        pre_vqc = True
        post_vqc = True

        # assuming that the input is normalized in the specific way
        qml.AmplitudeEmbedding(features=inputs, wires=[w for w in range(n_qubits)], normalize=False)

        # RY on 9th qubit for weight sharing
        # qml.RY(phi=np.pi/8, wires=8)
        qml.RY(theta_RY_switch, wires=n_qubits-1)

        # pre_vqc_weights -> (num_layers, num_qubits, 3)
        # hardware-efficient entangling for 8
        if (pre_vqc is True) and (pre_vqc_weights is not None):
            for l in range(num_pre_vqc_layers):
                for q in range(n_qubits_single_channel):
                    qml.U3(*pre_vqc_weights[l, q, :], wires=q)

                # # cyclic CNOT on 8
                # for i in range(n_qubits_single_channel):
                #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                # hardware-efficient CNOT on 8
                for i in range(0, n_qubits_single_channel, 2):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(1, n_qubits_single_channel, 2):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        # post_vqc_weights -> (num_layers, num_qubits, 3)
        # hardware-efficient entangling for 8
        if (post_vqc is True) and (post_vqc_weights is not None):
            for l in range(num_post_vqc_layers):
                for q in range(n_qubits_single_channel):
                    qml.U3(*post_vqc_weights[l, q, :], wires=q)

                # # cyclic CNOT on 8
                # for i in range(n_qubits_single_channel):
                #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                # hardware-efficient CNOT on 8
                for i in range(0, n_qubits_single_channel, 2):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                for i in range(1, n_qubits_single_channel, 2):
                    qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        # final overlap
        qml.Hadamard(wires=n_qubits-1)
        return qml.expval(qml.PauliZ(wires=n_qubits-1))
    
    return qml.QNode(circuit, dev, interface="torch")


# @qml.qnode(dev, interface="torch")
def AmpEmb__pre__c_post_VQC__switch_ry(n_qubits):
    dev = qml.device("default.qubit", n_qubits)

    def circuit(inputs,
                pre_vqc_weights_A, post_vqc_weights_A,
                pre_vqc_weights_B, post_vqc_weights_B,
                pre_vqc_weights_C, post_vqc_weights_C,
                pre_vqc_weights_D, post_vqc_weights_D):
        num_pre_vqc_layers = pre_vqc_weights_A.shape[0]
        num_post_vqc_layers = post_vqc_weights_A.shape[0]
        pre_vqc = True
        post_vqc = True

        theta_RY_switch_1 = np.pi/2
        theta_RY_switch_2 = np.pi/3
        theta_RY_switch_3 = np.pi/4

        # assuming that the input is normalized in the specific way
        qml.AmplitudeEmbedding(features=inputs, wires=[w for w in range(n_qubits)], normalize=False)

        def pre_VQC_A():
            # pre_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (pre_vqc is True) and (pre_vqc_weights_A is not None):
                for l in range(num_pre_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*pre_vqc_weights_A[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        def post_VQC_A():
            # post_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (post_vqc is True) and (post_vqc_weights_A is not None):
                for l in range(num_post_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*post_vqc_weights_A[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        def pre_VQC_B():
            # pre_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (pre_vqc is True) and (pre_vqc_weights_B is not None):
                for l in range(num_pre_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*pre_vqc_weights_B[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        def post_VQC_B():
            # post_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (post_vqc is True) and (post_vqc_weights_B is not None):
                for l in range(num_post_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*post_vqc_weights_B[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        def pre_VQC_C():
            # pre_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (pre_vqc is True) and (pre_vqc_weights_C is not None):
                for l in range(num_pre_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*pre_vqc_weights_C[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        def post_VQC_C():
            # post_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (post_vqc is True) and (post_vqc_weights_C is not None):
                for l in range(num_post_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*post_vqc_weights_C[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        def pre_VQC_D():
            # pre_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (pre_vqc is True) and (pre_vqc_weights_D is not None):
                for l in range(num_pre_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*pre_vqc_weights_D[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
        def post_VQC_D():
            # post_vqc_weights -> (num_layers, num_qubits, 3)
            # hardware-efficient entangling for 8
            if (post_vqc is True) and (post_vqc_weights_D is not None):
                for l in range(num_post_vqc_layers):
                    for q in range(n_qubits_single_channel):
                        qml.U3(*post_vqc_weights_D[l, q, :], wires=q)

                    # # cyclic CNOT on 8
                    # for i in range(n_qubits_single_channel):
                    #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                    # hardware-efficient CNOT on 8
                    for i in range(0, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])
                    for i in range(1, n_qubits_single_channel, 2):
                        qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

        qml.X(wires=n_qubits-1)
        qml.ctrl(pre_VQC_A, control=n_qubits-1)()
        qml.X(wires=n_qubits-1)
        qml.ctrl(post_VQC_A, control=n_qubits-1)()

        # RY on 9th qubit for weight sharing
        # qml.RY(phi=np.pi/8, wires=8)
        qml.RY(theta_RY_switch_1, wires=n_qubits-1)

        qml.X(wires=n_qubits-1)
        qml.ctrl(pre_VQC_B, control=n_qubits-1)()
        qml.X(wires=n_qubits-1)
        qml.ctrl(post_VQC_B, control=n_qubits-1)()

        qml.RY(theta_RY_switch_2, wires=n_qubits-1)

        qml.X(wires=n_qubits-1)
        qml.ctrl(pre_VQC_C, control=n_qubits-1)()
        qml.X(wires=n_qubits-1)
        qml.ctrl(post_VQC_C, control=n_qubits-1)()

        qml.RY(theta_RY_switch_3, wires=n_qubits-1)

        qml.X(wires=n_qubits-1)
        qml.ctrl(pre_VQC_D, control=n_qubits-1)()
        qml.X(wires=n_qubits-1)
        qml.ctrl(post_VQC_D, control=n_qubits-1)()

        # final overlap
        qml.Hadamard(wires=n_qubits-1)
        return qml.expval(qml.PauliZ(wires=n_qubits-1))
    
    return qml.QNode(circuit, dev, interface="torch")

# @qml.qnode(dev, interface="torch")
def circuit__1(bool_vals: list, n_blocks=3, kappa=4, length_total_channels=256):
    type1_local_cost = False
    type2_local_cost = False
    weight_interaction_cost = False
    weight_interaction_cost__relaxed = False
    global_cost__layer_wise_type2 = False

    costs = [type1_local_cost, type2_local_cost, weight_interaction_cost, weight_interaction_cost__relaxed, global_cost__layer_wise_type2]
    for b in bool_vals:
        costs[b] = True

    s_dagger = False

    n_qubits_wo_blockwise = n_qubits_quantum_single_channel(length_total_channels)
    n_qubits = n_qubits_wo_blockwise
    if (weight_interaction_cost is True) or (weight_interaction_cost__relaxed is True):
        n_qubits = n_qubits_wo_blockwise + n_blocks

    dev = qml.device("default.qubit", n_qubits)
    # random_inds = sorted(np.random.choice(n_qubits - 1, size=kappa, replace=False))

    control_vals = [1 for _ in range(kappa)]
    control_vals_mixed = True
    if control_vals_mixed is True:
        control_vals = [1] * (kappa // 2) + [0] * (kappa - (kappa // 2))
        random.shuffle(control_vals)

    all_layers_random_ctlrs = True
    random_inds_list = []

    def circuit(inputs, theta_RY_switch, vqc_weights):
        # vqc_weights shape: (num_blocks, num_layers_per_block, num_wires, 3)
        switch = n_qubits_wo_blockwise - 1
        global control_vals

        num_vqc_blocks = vqc_weights.shape[0]
        num_layers_per_block = vqc_weights.shape[1]
        num_wires_vqc = vqc_weights.shape[2]
        # print(num_wires_vqc, switch)
        assert num_wires_vqc == switch

        # qml.Hadamard(wires=switch)
        # print("shape of input for circuit__1:", inputs)

        # assuming that the input is normalized in the specific way
        qml.AmplitudeEmbedding(features=inputs, wires=[w for w in range(n_qubits_wo_blockwise)], normalize=False)
        # qml.ctrl(qml.AmplitudeEmbedding, switch, control_values=(0))(features=inputs[:, :128], wires=[w for w in range(switch)], normalize=True)
        # qml.ctrl(qml.AmplitudeEmbedding, switch, control_values=(1))(features=inputs[:, 128:], wires=[w for w in range(switch)], normalize=True)

        if s_dagger:
            qml.adjoint(qml.S(wires=switch))

        if (weight_interaction_cost is True) or (weight_interaction_cost__relaxed is True):
            for _ in range(n_qubits_wo_blockwise, n_qubits, 1):
                qml.Hadamard(wires=_)
        
        # qml.MottonenStatePreparation(state_vector=inputs, wires=[w for w in range(n_qubits)])
        # print("qml state:", qml.state())

        # if (pre_vqc is True) and (pre_vqc_weights is not None):
        if True:
            for b in range(num_vqc_blocks):
                # qml.StronglyEntanglingLayers(weights=vqc_weights[b], wires=range(switch))

                for l in range(num_layers_per_block):
                    for q in range(num_wires_vqc):
                        qml.U3(*vqc_weights[b, l, q, :], wires=q)

                # # cyclic CNOT on 8
                # for i in range(n_qubits_single_channel):
                #     qml.CNOT(wires=[i, (i+1)%n_qubits_single_channel])

                # hardware-efficient CNOT on 8
                for i in range(0, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])
                for i in range(1, num_wires_vqc, 2):
                    qml.CNOT(wires=[i, (i+1)%num_wires_vqc])

                # qml.ctrl(qml.RX, (b % switch), control_values=(1))(theta_RY_switch[b], wires=switch)
                
                if all_layers_random_ctlrs is False:
                    if len(random_inds_list) != 1:
                        random_inds = sorted(np.random.choice(n_qubits - 1, size=kappa, replace=False))
                        random_inds_list.append(random_inds)
                        print("random_inds_list:", random_inds_list)

                    if type1_local_cost is True:
                        qml.ctrl(qml.Z, random_inds_list[0], control_values=control_vals)(wires=switch)
                    elif type2_local_cost is True:
                        for c_wire in random_inds_list[0]:
                            qml.ctrl(qml.Z, switch, control_values=(1))(wires=c_wire)
                else:
                    if len(random_inds_list) != num_vqc_blocks:
                        if weight_interaction_cost is True:
                            random_inds = sorted(np.random.choice(n_qubits_wo_blockwise - 1, size=kappa, replace=False))
                            for __ in range(n_qubits_wo_blockwise, n_qubits, 1):
                                random_inds.append(__)
                            # random_inds.append(n_qubits_wo_blockwise + b)
                        elif weight_interaction_cost__relaxed is True:
                            random_inds = sorted(np.random.choice(n_qubits_wo_blockwise - 1, size=kappa, replace=False))
                            random_inds.append(n_qubits_wo_blockwise + b)
                        else:
                            random_inds = sorted(np.random.choice(n_qubits - 1, size=kappa, replace=False))
                        random_inds_list.append(random_inds)
                        print("random_inds_list:", random_inds_list)

                    if weight_interaction_cost is True:
                        control_vals_temp = [0] * n_blocks
                        control_vals_temp[b] = 1
                        # print(control_vals, control_vals_temp)
                        control_vals.extend(control_vals_temp)
                        # control_vals.append(1)
                        
                        qml.ctrl(qml.U3, random_inds_list[b], control_values=control_vals)(*theta_RY_switch[b], wires=switch)
                        control_vals = control_vals[:-n_blocks]
                    elif weight_interaction_cost__relaxed is True:
                        control_vals.append(1)
                        
                        qml.ctrl(qml.U3, random_inds_list[b], control_values=control_vals)(*theta_RY_switch[b], wires=switch)
                        control_vals = control_vals[:-1]
                    else:
                        qml.ctrl(qml.U3, random_inds_list[b], control_values=control_vals)(*theta_RY_switch[b], wires=switch)

                    if type1_local_cost is True:
                        qml.ctrl(qml.Z, random_inds_list[b], control_values=control_vals)(wires=switch)
                    elif type2_local_cost is True:
                        for c_wire in random_inds_list[b]:
                            qml.ctrl(qml.Z, switch, control_values=(1))(wires=c_wire)
                
                # qml.ctrl(qml.U3, (b % switch), control_values=(1))(*theta_RY_switch[b], wires=switch)

        # final overlap
        if weight_interaction_cost is True:
            for _ in range(n_qubits_wo_blockwise, n_qubits, 1):
                qml.Hadamard(wires=_)
        elif weight_interaction_cost__relaxed is True:
            qml.ctrl(qml.Hadamard, [w for w in range(n_qubits_wo_blockwise, n_qubits, 1)], control_values=(1 for __ in range(n_qubits - n_qubits_wo_blockwise)))(wires=switch)
        else:
        # if True:
            qml.Hadamard(wires=switch)

        if weight_interaction_cost is True:
            # return [qml.expval(qml.PauliZ(wires=_)) for _ in range(n_qubits_wo_blockwise, n_qubits, 1)]
            return [qml.expval(qml.PauliZ(wires=_)) for _ in range(switch, n_qubits, 1)]
        else:
            return qml.expval(qml.PauliZ(wires=switch))

        # return qml.state(
    
    return qml.QNode(circuit, dev, interface="torch")