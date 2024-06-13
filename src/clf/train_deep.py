import os
import torch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from model import StellarNet

from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight
from torch import nn
from torch.optim.lr_scheduler import OneCycleLR

def plot(training_losses, validation_losses, accuracy_scores, filename, save_fig=True):
    
    filename ='../results/training_curves.png'

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 14))
    
    ax1.plot(accuracy_scores, label='Validation Accuracy')
    ax1.set_xlabel('Epochs')
    ax1.set_ylabel('Accuracy')
    ax1.set_title('Accuracy')
    ax1.legend()

    ax1.annotate(f'{accuracy_scores[0]:.2f}', (0, accuracy_scores[0]), textcoords="offset points", xytext=(0,10), ha='center')
    ax1.annotate(f'{accuracy_scores[-1]:.2f}', (len(accuracy_scores)-1, accuracy_scores[-1]), textcoords="offset points", xytext=(0,10), ha='center')

    ax2.plot(training_losses, label='Training Loss')
    ax2.plot(validation_losses, label='Validation Loss')
    ax2.set_xlabel('Epochs')
    ax2.set_ylabel('Loss')
    ax2.set_title('Training and Validation Loss')
    ax2.legend()

    ax2.annotate(f'{training_losses[0]:.2f}', (0, training_losses[0]), textcoords="offset points", xytext=(0,10), ha='center')
    ax2.annotate(f'{training_losses[-1]:.2f}', (len(training_losses)-1, training_losses[-1]), textcoords="offset points", xytext=(0,10), ha='center')
    ax2.annotate(f'{validation_losses[0]:.2f}', (0, validation_losses[0]), textcoords="offset points", xytext=(0,10), ha='center')
    ax2.annotate(f'{validation_losses[-1]:.2f}', (len(validation_losses)-1, validation_losses[-1]), textcoords="offset points", xytext=(0,10), ha='center')

    plt.show()

    if save_fig:
        plt.savefig(filename)
    
def _extend_curves(curves):
    '''
    function to extended loss curves to the same length
    '''
    max_length = max(len(curve) for curve in curves)
    
    extended_curves = []
    for curve in curves:
        last_value = curve[-1]
        extended_curve = curve + [last_value] * (max_length - len(curve))
        extended_curves.append(extended_curve)
    
    return np.array(extended_curves)

def _init_weights(m):
    if isinstance(m, nn.Conv1d) or isinstance(m, nn.Linear):
        nn.init.kaiming_uniform_(m.weight, nonlinearity='relu')
        if m.bias is not None:
            nn.init.constant_(m.bias, 0)

def train_model(X, y, spectrum_width, learning_rate, epochs, batch_size, device, weight_decay, patience):

    def fit(model, x_train, y_train, x_val, y_val, learning_rate, epochs, batch_size, device, weight_decay, patience):
    
        model.apply(_init_weights)

        # hyperparameters
        epochs = epochs
        learning_rate = learning_rate
        batch_size = batch_size
        device = device

        # early stopping
        patience = patience
        best_val_loss = float('inf')
        patience_counter = 0
        
        class_weights = torch.tensor(compute_class_weight(class_weight='balanced',classes=np.unique(y_train), y=y_train.numpy())).to(device)

        # model components
        criterion = nn.BCEWithLogitsLoss(pos_weight=class_weights[1])
        optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
        
        # move everything to gpu
        model.to(device)
        x_train = x_train.to(device)
        y_train = y_train.unsqueeze(1).to(device)
        x_val = x_val.to(device)
        y_val = y_val.unsqueeze(1).to(device)

        # metrics
        training_losses, validation_losses = [], []
        accuracy = []
        
        # lr cycling
        max_lr = 1e-3
        steps_per_epoch = (len(x_train) + batch_size - 1) // batch_size
        scheduler = OneCycleLR(optimizer, max_lr=max_lr, steps_per_epoch=steps_per_epoch, epochs=epochs)

        batch_start = torch.arange(0, len(x_train), batch_size)
        t = tqdm(range(epochs), leave=True, dynamic_ncols=True, desc="Epochs")

        for epoch in t:
            
            model.train()
            running_loss = 0

            for start in batch_start:
                
                x_spectra = x_train[start:start+batch_size,:-2]
                x_context = x_train[start:start+batch_size,-2:]
            
                y_batch = y_train[start:start+batch_size]
                
                output = model(x_spectra.unsqueeze(1), x_context)
                loss = criterion(output, y_batch)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                scheduler.step()

                running_loss += loss.item() * x_spectra.size(0)

            train_loss = running_loss / len(x_train)
            training_losses.append(train_loss)

            t.set_postfix({'Train Loss':train_loss})

            model.eval()
            preds, labels = [], []

            with torch.no_grad():
                
                x_spectra = x_val[:,:-2]
                x_context = x_val[:,-2:]
                output = model(x_spectra.unsqueeze(1), x_context)
                loss = criterion(output, y_val)

                probs = torch.sigmoid(output)
                pred = torch.round(probs).cpu().numpy().astype(float)
                
                preds.extend(pred)
                labels.extend(y_val.cpu().numpy())
                
                val_loss = loss.item()
            
            epoch_acc = accuracy_score(labels, preds)
            validation_losses.append(val_loss)
            accuracy.append(epoch_acc)

            t.set_postfix({'Train loss': train_loss, 'Val Loss': val_loss, 'Accuracy': epoch_acc})

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                t.set_postfix_str(f'Early stopping triggered at epoch {epoch+1}')
                break

        return model, training_losses, validation_losses, accuracy

    kfold = StratifiedKFold(n_splits=10)
    training_losses_foldx, validation_losses_foldx, accuracy_scores_foldx, models = [], [], [], []

    model = StellarNet(input_channels=spectrum_width)

    for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
        
        print(f"\nFitting fold {fold+1}")

        model, tr_loss, val_loss, acc = fit(model, X[train_idx], y[train_idx], X[val_idx], y[val_idx], learning_rate, epochs, batch_size, device, weight_decay, patience)
        models.append(model)
        training_losses_foldx.append(tr_loss)
        validation_losses_foldx.append(val_loss)
        accuracy_scores_foldx.append(acc)

    training_losses = np.mean(_extend_curves(training_losses_foldx), axis=0)
    validation_losses = np.mean(_extend_curves(validation_losses_foldx), axis=0)
    accuracy_scores = np.mean(_extend_curves(accuracy_scores_foldx), axis=0)

    plot(training_losses, validation_losses, accuracy_scores, save_fig=True)

    return models

def prepare_data(data_dir):
    
    data = pd.read_parquet(data_dir)
    df = data.drop(columns = ['teff_gspphot', 'logg_gspphot', 'mh_gspphot', 'spectraltype_esphs'])

    # create context
    df['min'] = df['flux'].apply(np.min)
    df['max'] = df['flux'].apply(np.max)

    spectrum_width = len(df['flux'][0])

    spectra = df['flux'].to_numpy()
    context = df[['max','min']].to_numpy()

    # L2 normalization
    spectra = torch.from_numpy(np.array([spectrum / np.linalg.norm(spectrum, keepdims=True) for spectrum in spectra])).float()
    context = torch.tensor(context)

    X = torch.cat([spectra,context],1)
    y = df['Cat'].to_numpy()

    # encode categories to int
    y = torch.from_numpy(np.where(y == 'M', 1, np.where(y == 'LM', 0, y)).astype(float))

    print("Data loaded!")
    return X, y, spectrum_width

def main():

    print("Starting training...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    data_dir = '../data/train.parquet'

    X, y, spectrum_width = prepare_data(data_dir)

    models = train_model(X, y, spectrum_width, learning_rate=1e-4, epochs=50, batch_size=64, device='cuda' if torch.cuda.is_available() else 'cpu', weight_decay=0.01, patience=5)
    
    # save trained model
    torch.save(models,'../trained_models/StellarNet.pth')

if __name__ == "__main__":
    main()