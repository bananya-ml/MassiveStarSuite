from fastapi import FastAPI, HTTPException
from modules.resolve_source import resolve
from modules.download_data import pull_data
from modules.inference import inference
import glob
import pandas as pd
import shutil
import torch

def clean_temp(data_dir):
    try:
        shutil.rmtree(data_dir)
        print(f"Deleted {data_dir} directory and its contents.")
    except Exception as e:
        print(f"Error deleting {data_dir} directory: {e}")
    
if __name__ == "__main__":
    
    source_id = '4111834567779557376'
    ra = '256.5229102004341'
    dec = '-26.580565130784702'
    
    results = resolve(id=source_id)
    data_dir = pull_data(results)

    file = '*.csv'
    csv_files = glob.glob(f"{data_dir}/{file}")
    data = pd.read_csv(csv_files[0])
    X = data['flux'].to_numpy()
    
    model = torch.jit.load('./models/cnn_ensemble.pth', map_location=torch.device('cpu'))
    
    prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
    print(prediction)
    clean_temp(data_dir)