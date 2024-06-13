import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from lightgbm import (LGBMClassifier as lgb)
from xgboost import XGBClassifier as xgb

from sklearn.metrics import (precision_score, accuracy_score, recall_score, f1_score, roc_auc_score, confusion_matrix, log_loss)
from sklearn.model_selection import RepeatedStratifiedKFold


def predict(model, X, y, PLOT=False):
    
    preds = np.zeros(X.shape[0])
    print("\nMaking predictions...")
    for m in model:

        preds += m.predict(X)

    preds /= len(model) 

    f1 = f1_score(y, preds)
    recall = recall_score(y, preds)
    precision = precision_score(y, preds)
    accuracy = accuracy_score(y, preds)
    cm = confusion_matrix(y, preds)
    
    print(f"F1 score: {f1:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Accuracy: {accuracy:.4f}")    
    print(f"Confusion matrix: \n{cm}")
    
    if PLOT:
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
        xticklabels=['Predicted Negative', 'Predicted Positive'],
        yticklabels=['True Negative', 'True Positive'])
        plt.title('Confusion Matrix')
        plt.show()

    return

def train_model(model, X, y, verbose=False):
    
    print(f"\nTraining {model} model")
    
    kfold = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=42)
    models = []
    losses, auc_scores= [], []
    for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y)):
        
        x_train, x_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        print(f"Fitting fold {fold+1}")

        model.fit(x_train, y_train)
        models.append(model)
        
        y_probs = model.predict_proba(x_val)[:,1]
        
        loss = log_loss(y_val, y_probs)
        losses.append(loss)
        auc_score = roc_auc_score(y_val, y_probs)
        auc_scores.append(auc_score)

        if verbose:
            print(f"Loss: {loss:.4f}")
            print(f"AUC score: {auc_score:.4f}")
        
    print("Overall:")
    print(f"Loss: {np.mean(losses):.4f}")
    print(f"AUC score: {np.mean(auc_scores):.4f}")

    return models

def prepare_data(data_dir):
    
    df = pd.read_parquet(data_dir)

    expanded_df = pd.DataFrame(df['flux'].tolist(), index=df.index)
    
    df = df.drop(columns=['source_id','spectraltype_esphs','teff_gspphot','logg_gspphot','mh_gspphot','flux'])
    df = pd.concat([df, expanded_df], axis=1)

    X = df.drop(columns=['Cat']).to_numpy()
    y = df['Cat']
    y = np.where(y == 'M', 1, np.where(y == 'LM', 0, y)).astype(float)

    print("Data loaded!")
    return X, y 

def main():
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    train_data = '../data/train.parquet'
    test_data = '../data/test.parquet'

    X_train, y_train = prepare_data(train_data)
    X_test, y_test = prepare_data(test_data)

    models = {'knn': KNeighborsClassifier(),
            'lgb': lgb(objective='binary',metric='binary_crossentropy',verbosity=-1),
            'xgb': xgb(objective='binary:logistic',eval_metric=['logloss', 'error'], learning_rate=0.05, max_depth=6)}

    log_dir = '../logs'
    
    for _, m in models.items():
        
        model = train_model(m, X_train, y_train, verbose=False)

        predict(model, X_test, y_test)

        #pickle.dump(model, open(f'../trained_models/{m}.pickle', 'wb'))

if __name__=="__main__":
    main()