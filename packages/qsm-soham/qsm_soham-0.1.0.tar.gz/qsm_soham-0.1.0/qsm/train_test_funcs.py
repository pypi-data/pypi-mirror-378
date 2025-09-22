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

def train_test_classical(model, optimizer, criterion, 
          train_loader, test_loader, 
          accuracy_function, distance_function,
          folder_path, num_epochs=20, log_interval=50, 
          load_checkpoint=False, start_epoch_checkpoint=0, checkpoint_start_file=None, scheduler=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else device

    os.makedirs(folder_path, exist_ok=True)
    start_epoch = 1

    loss_history = []
    loss_history_eval = []
    accs_history = []
    accs_history_eval = []
    threshold_history = []

    if load_checkpoint:
        start_epoch = start_epoch_checkpoint
        checkpoint = torch.load(checkpoint_start_file, map_location=device)

        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optim'])
        # scheduler__AmpVanilla.load_state_dict(checkpoint['scheduler'])

    for epoch in range(start_epoch, num_epochs + 1, 1):
        print(f'Epoch {epoch}/{num_epochs}')
        print('Training', '-'*20)
        print("lr:", optimizer.param_groups[0]['lr'])

        model.train()
        running_loss = 0.0
        running_accs = 0.0

        # The DataLoader now yields two images and a label per batch
        for batch_idx, (x1, x2, y) in enumerate(train_loader):
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)

            optimizer.zero_grad()

            # The model's forward pass
            out1 = model(x1)
            out2 = model(x2)
            # out1, out2 = model(x1, x2)

            # The loss calculation
            loss = criterion(out1, out2, y)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            # d_emb = torch.pairwise_distance(out1, out2, p=2)
            d_emb = distance_function(out1, out2)
            
            accs_batch, _ = accuracy_function(d_emb, y)
            running_accs += accs_batch / 100.0

            if (batch_idx + 1) % log_interval == 0:
                print(f'{batch_idx+1}/{len(train_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        epoch_loss = running_loss / len(train_loader)
        train_accuracy = (running_accs / len(train_loader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total training Loss: {epoch_loss:.4f} | Training Accuracy: {train_accuracy:.2f}%')

        loss_history.append(epoch_loss)
        accs_history.append(train_accuracy)

        if scheduler:
            scheduler.step()

        # After the training epoch, evaluate on the training set
        model.eval()
        running_loss = 0.0
        running_accs = 0.0
        # all_distances = []
        # all_labels = []

        dataloader = test_loader

        with torch.no_grad():
            for batch_idx, (x1, x2, y) in enumerate(dataloader):
                x1, x2, y = x1.to(device), x2.to(device), y.to(device)

                # Get the embeddings from the model
                # out1, out2 = model(x1, x2)
                out1 = model(x1)
                out2 = model(x2)

                # Calculate the loss for this batch
                loss = criterion(out1, out2, y)
                running_loss += loss.item()

                # Store distances and labels for accuracy calculation
                # distances = torch.pairwise_distance(out1, out2, p=2)
                distances = distance_function(out1, out2)

                # all_distances.append(distances.cpu())
                # all_labels.append(y.cpu())
                accs_batch, _ = accuracy_function(distances, y)
                running_accs += accs_batch / 100.0

                if (batch_idx + 1) % log_interval == 0:
                    print(f'{batch_idx+1}/{len(test_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        # # Concatenate all distances and labels from the batches
        # all_distances = torch.cat(all_distances)
        # all_labels = torch.cat(all_labels)

        # Calculate overall loss and accuracy
        total_loss = running_loss / len(dataloader)
        # accuracy, best_threshold = accuracy_contrastive_loss(all_distances, all_labels)
        test_accuracy = (running_accs / len(dataloader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total testing Loss: {total_loss:.4f} | Testing Accuracy: {test_accuracy:.2f}%')

        loss_history_eval.append(total_loss)
        accs_history_eval.append(test_accuracy)

        to_save = {
            'model': model.state_dict(),
            # 'scheduler': scheduler.state_dict(),
            'optim': optimizer.state_dict(),
        }

        print('Saving checkpoint and data..')
        # torch.save(to_save, '/Users/soardr/QSM/IYA Blocks/custom_Siamese_I_1to1__epoch_{}_loss_{:.3f}_acc_{:.3f}.pt'.format(epoch, loss, acc))
        torch.save(to_save, os.path.join(folder_path, f"_{epoch}.pt"))
    
    return loss_history, train_accuracy, loss_history_eval, accs_history_eval

def train_test_classical__triplet(model, optimizer, criterion, 
          train_loader, test_loader, 
          accuracy_function, distance_function,
          folder_path, num_epochs=20, log_interval=50, 
          load_checkpoint=False, start_epoch_checkpoint=0, checkpoint_start_file=None, scheduler=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else device

    os.makedirs(folder_path, exist_ok=True)
    start_epoch = 1

    loss_history = []
    loss_history_eval = []
    accs_history = []
    accs_history_eval = []
    threshold_history = []

    if load_checkpoint:
        start_epoch = start_epoch_checkpoint
        checkpoint = torch.load(checkpoint_start_file, map_location=device)

        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optim'])
        # scheduler__AmpVanilla.load_state_dict(checkpoint['scheduler'])

    for epoch in range(start_epoch, num_epochs + 1, 1):
        print(f'Epoch {epoch}/{num_epochs}')
        print('Training', '-'*20)
        print("lr:", optimizer.param_groups[0]['lr'])

        model.train()
        running_loss = 0.0
        running_accs = 0.0

        # The DataLoader now yields two images and a label per batch
        # for batch_idx, (x1, x2, y) in enumerate(train_loader):
        for batch_idx, (anchor, positive, negative) in enumerate(train_loader):
            # x1, x2, y = x1.to(device), x2.to(device), y.to(device)
            anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

            optimizer.zero_grad()

            # The model's forward pass
            anchor_out = model(anchor)
            positive_out = model(positive)
            negative_out = model(negative)
            # out1, out2 = model(x1, x2)

            # The loss calculation
            loss = criterion(anchor_out, positive_out, negative_out)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            # d_emb = torch.pairwise_distance(out1, out2, p=2)
            # d_emb = distance_function(out1, out2)
            
            # accs_batch, _ = accuracy_function(d_emb, y)
            accs_batch = accuracy_function(anchor_out, positive_out, negative_out)
            
            running_accs += accs_batch / 100.0

            if (batch_idx + 1) % log_interval == 0:
                print(f'{batch_idx+1}/{len(train_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        epoch_loss = running_loss / len(train_loader)
        train_accuracy = (running_accs / len(train_loader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total training Loss: {epoch_loss:.4f} | Training Accuracy: {train_accuracy:.2f}%')

        loss_history.append(epoch_loss)
        accs_history.append(train_accuracy)

        if scheduler:
            scheduler.step()

        # After the training epoch, evaluate on the training set
        model.eval()
        running_loss = 0.0
        running_accs = 0.0
        # all_distances = []
        # all_labels = []

        dataloader = test_loader

        with torch.no_grad():
            # for batch_idx, (x1, x2, y) in enumerate(dataloader):
            for batch_idx, (anchor, positive, negative) in enumerate(dataloader):
                anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

                # Get the embeddings from the model
                # out1, out2 = model(x1, x2)
                anchor_out = model(anchor)
                positive_out = model(positive)
                negative_out = model(negative)

                # Calculate the loss for this batch
                loss = criterion(anchor_out, positive_out, negative_out)
                running_loss += loss.item()

                # Store distances and labels for accuracy calculation
                # distances = torch.pairwise_distance(out1, out2, p=2)
                # distances = distance_function(out1, out2)

                # all_distances.append(distances.cpu())
                # all_labels.append(y.cpu())
                # accs_batch, _ = accuracy_function(distances, y)
                accs_batch = accuracy_function(anchor_out, positive_out, negative_out)
                
                running_accs += accs_batch / 100.0

                if (batch_idx + 1) % log_interval == 0:
                    print(f'{batch_idx+1}/{len(test_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        # # Concatenate all distances and labels from the batches
        # all_distances = torch.cat(all_distances)
        # all_labels = torch.cat(all_labels)

        # Calculate overall loss and accuracy
        total_loss = running_loss / len(dataloader)
        # accuracy, best_threshold = accuracy_contrastive_loss(all_distances, all_labels)
        test_accuracy = (running_accs / len(dataloader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total testing Loss: {total_loss:.4f} | Testing Accuracy: {test_accuracy:.2f}%')

        loss_history_eval.append(total_loss)
        accs_history_eval.append(test_accuracy)

        to_save = {
            'model': model.state_dict(),
            # 'scheduler': scheduler.state_dict(),
            'optim': optimizer.state_dict(),
        }

        print('Saving checkpoint and data..')
        # torch.save(to_save, '/Users/soardr/QSM/IYA Blocks/custom_Siamese_I_1to1__epoch_{}_loss_{:.3f}_acc_{:.3f}.pt'.format(epoch, loss, acc))
        torch.save(to_save, os.path.join(folder_path, f"_{epoch}.pt"))
    
    return loss_history, train_accuracy, loss_history_eval, accs_history_eval

def train_test_quantum(model, optimizer, criterion, 
                       train_loader, test_loader, 
                       accuracy_function, distance_function,
                       folder_path, num_epochs=20, log_interval=50, 
                       load_checkpoint=False, start_epoch_checkpoint=0, checkpoint_start_file=None, scheduler=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else device

    os.makedirs(folder_path, exist_ok=True)
    start_epoch = 1

    loss_history = []
    loss_history_eval = []
    accs_history = []
    accs_history_eval = []
    threshold_history = []

    if load_checkpoint:
        start_epoch = start_epoch_checkpoint
        checkpoint = torch.load(checkpoint_start_file, map_location=device)

        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optim'])
        # scheduler__AmpVanilla.load_state_dict(checkpoint['scheduler'])

    for epoch in range(start_epoch, num_epochs + 1, 1):
        print(f'Epoch {epoch}/{num_epochs}')
        print('Training', '-'*20)
        print("lr:", optimizer.param_groups[0]['lr'])

        model.train()
        running_loss = 0.0
        running_accs = 0.0

        # The DataLoader now yields two images and a label per batch
        for batch_idx, (x1, x2, y) in enumerate(train_loader):
            x1, x2, y = x1.to(device), x2.to(device), y.to(device)

            optimizer.zero_grad()

            # The model's forward pass
            # out1 = model(x1)
            # out2 = model(x2)
            # # out1, out2 = model(x1, x2)
            overlap = model(x1, x2)

            # The loss calculation
            loss = criterion(overlap, y)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            # d_emb = torch.pairwise_distance(out1, out2, p=2)
            if distance_function is not None:
                d_emb = distance_function(overlap)
            else:
                d_emb = overlap
            
            accs_batch, _ = accuracy_function(d_emb, y)
            # accs_batch = accuracy_function(d_emb, y)
            
            running_accs += accs_batch / 100.0

            if (batch_idx + 1) % log_interval == 0:
                print(f'{batch_idx+1}/{len(train_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        epoch_loss = running_loss / len(train_loader)
        train_accuracy = (running_accs / len(train_loader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total training Loss: {epoch_loss:.4f} | Training Accuracy: {train_accuracy:.2f}%')

        loss_history.append(epoch_loss)
        accs_history.append(train_accuracy)

        if scheduler:
            scheduler.step()

        # After the training epoch, evaluate on the training set
        model.eval()
        running_loss = 0.0
        running_accs = 0.0
        # all_distances = []
        # all_labels = []

        dataloader = test_loader

        with torch.no_grad():
            for batch_idx, (x1, x2, y) in enumerate(dataloader):
                x1, x2, y = x1.to(device), x2.to(device), y.to(device)

                # Get the embeddings from the model
                # # out1, out2 = model(x1, x2)
                # out1 = model(x1)
                # out2 = model(x2)
                overlap = model(x1, x2)

                # Calculate the loss for this batch
                loss = criterion(overlap, y)

                running_loss += loss.item()

                # Store distances and labels for accuracy calculation
                # distances = torch.pairwise_distance(out1, out2, p=2)
                if distance_function is not None:
                    distances = distance_function(overlap)
                else:
                    distances = overlap

                # all_distances.append(distances.cpu())
                # all_labels.append(y.cpu())
                accs_batch, _ = accuracy_function(distances, y)
                # accs_batch = accuracy_function(distances, y)
                
                running_accs += accs_batch / 100.0

                if (batch_idx + 1) % log_interval == 0:
                    print(f'{batch_idx+1}/{len(test_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        # # Concatenate all distances and labels from the batches
        # all_distances = torch.cat(all_distances)
        # all_labels = torch.cat(all_labels)

        # Calculate overall loss and accuracy
        total_loss = running_loss / len(dataloader)
        # accuracy, best_threshold = accuracy_contrastive_loss(all_distances, all_labels)
        test_accuracy = (running_accs / len(dataloader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total testing Loss: {total_loss:.4f} | Testing Accuracy: {test_accuracy:.2f}%')

        loss_history_eval.append(total_loss)
        accs_history_eval.append(test_accuracy)

        to_save = {
            'model': model.state_dict(),
            # 'scheduler': scheduler.state_dict(),
            'optim': optimizer.state_dict(),
        }

        print('Saving checkpoint and data..')
        # torch.save(to_save, '/Users/soardr/QSM/IYA Blocks/custom_Siamese_I_1to1__epoch_{}_loss_{:.3f}_acc_{:.3f}.pt'.format(epoch, loss, acc))
        torch.save(to_save, os.path.join(folder_path, f"_{epoch}.pt"))
    
    return loss_history, train_accuracy, loss_history_eval, accs_history_eval

def train_test_quantum__triplet(model, optimizer, criterion, 
                       train_loader, test_loader, 
                       accuracy_function, distance_function,
                       folder_path, num_epochs=20, log_interval=50, 
                       load_checkpoint=False, start_epoch_checkpoint=0, checkpoint_start_file=None, scheduler=None):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = 'mps' if torch.backends.mps.is_available() and torch.backends.mps.is_built() else device

    os.makedirs(folder_path, exist_ok=True)
    start_epoch = 1

    loss_history = []
    loss_history_eval = []
    accs_history = []
    accs_history_eval = []
    threshold_history = []

    if load_checkpoint:
        start_epoch = start_epoch_checkpoint
        checkpoint = torch.load(checkpoint_start_file, map_location=device)

        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optim'])
        # scheduler__AmpVanilla.load_state_dict(checkpoint['scheduler'])

    for epoch in range(start_epoch, num_epochs + 1, 1):
        print(f'Epoch {epoch}/{num_epochs}')
        print('Training', '-'*20)
        print("lr:", optimizer.param_groups[0]['lr'])

        model.train()
        running_loss = 0.0
        running_accs = 0.0

        # The DataLoader now yields two images and a label per batch
        # for batch_idx, (x1, x2, y) in enumerate(train_loader):
        for batch_idx, (anchor, positive, negative) in enumerate(train_loader):
            anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

            optimizer.zero_grad()

            # The model's forward pass
            # out1 = model(x1)
            # out2 = model(x2)
            # # out1, out2 = model(x1, x2)
            overlap_positive = model(anchor, positive)
            overlap_negative = model(anchor, negative)

            # The loss calculation
            loss = criterion(overlap_positive, overlap_negative)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            # d_emb = torch.pairwise_distance(out1, out2, p=2)
            if distance_function is not None:
                d_emb = distance_function(overlap)
            else:
                d_emb = overlap_positive
            
            # accs_batch, _ = accuracy_function(d_emb, y)
            accs_batch = accuracy_function(anchor, overlap_positive, overlap_negative)
            
            running_accs += accs_batch / 100.0

            if (batch_idx + 1) % log_interval == 0:
                print(f'{batch_idx+1}/{len(train_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        epoch_loss = running_loss / len(train_loader)
        train_accuracy = (running_accs / len(train_loader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total training Loss: {epoch_loss:.4f} | Training Accuracy: {train_accuracy:.2f}%')

        loss_history.append(epoch_loss)
        accs_history.append(train_accuracy)

        if scheduler:
            scheduler.step()

        # After the training epoch, evaluate on the training set
        model.eval()
        running_loss = 0.0
        running_accs = 0.0
        # all_distances = []
        # all_labels = []

        dataloader = test_loader

        with torch.no_grad():
            # for batch_idx, (x1, x2, y) in enumerate(dataloader):
            for batch_idx, (anchor, positive, negative) in enumerate(dataloader):
                anchor, positive, negative = anchor.to(device), positive.to(device), negative.to(device)

                # Get the embeddings from the model
                # # out1, out2 = model(x1, x2)
                # out1 = model(x1)
                # out2 = model(x2)
                overlap_positive = model(anchor, positive)
                overlap_negative = model(anchor, negative)

                # Calculate the loss for this batch
                loss = criterion(overlap_positive, overlap_negative)

                running_loss += loss.item()

                # Store distances and labels for accuracy calculation
                # distances = torch.pairwise_distance(out1, out2, p=2)
                if distance_function is not None:
                    distances = distance_function(overlap)
                else:
                    distances = overlap_positive

                # all_distances.append(distances.cpu())
                # all_labels.append(y.cpu())
                # accs_batch, _ = accuracy_function(distances, y)
                accs_batch = accuracy_function(anchor, overlap_positive, overlap_negative)
                
                running_accs += accs_batch / 100.0

                if (batch_idx + 1) % log_interval == 0:
                    print(f'{batch_idx+1}/{len(test_loader)}: Loss: {running_loss / (batch_idx+1):.4f}')

        # # Concatenate all distances and labels from the batches
        # all_distances = torch.cat(all_distances)
        # all_labels = torch.cat(all_labels)

        # Calculate overall loss and accuracy
        total_loss = running_loss / len(dataloader)
        # accuracy, best_threshold = accuracy_contrastive_loss(all_distances, all_labels)
        test_accuracy = (running_accs / len(dataloader)) * 100
        print(f'Epoch {epoch}/{num_epochs}: Total testing Loss: {total_loss:.4f} | Testing Accuracy: {test_accuracy:.2f}%')

        loss_history_eval.append(total_loss)
        accs_history_eval.append(test_accuracy)

        to_save = {
            'model': model.state_dict(),
            # 'scheduler': scheduler.state_dict(),
            'optim': optimizer.state_dict(),
        }

        print('Saving checkpoint and data..')
        # torch.save(to_save, '/Users/soardr/QSM/IYA Blocks/custom_Siamese_I_1to1__epoch_{}_loss_{:.3f}_acc_{:.3f}.pt'.format(epoch, loss, acc))
        torch.save(to_save, os.path.join(folder_path, f"_{epoch}.pt"))
    
    return loss_history, train_accuracy, loss_history_eval, accs_history_eval