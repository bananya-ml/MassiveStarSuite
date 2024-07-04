from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from modules.resolve_source import resolve
from modules.download_data import pull_data
from modules.inference import inference
import glob
import pandas as pd
import shutil
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SourceID(BaseModel):
    source_id: str

class Coordinates(BaseModel):
    ra: float
    dec: float

def clean_temp(data_dir):
    try:
        shutil.rmtree(data_dir)
        print(f"Deleted {data_dir} directory and its contents.")
    except Exception as e:
        print(f"Error deleting {data_dir} directory: {e}")

@app.post("/predict/id")
async def predict_by_id(source_id: SourceID):
    try:
        results = resolve(id=source_id.source_id)
        data_dir = pull_data(results)
        
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        model = torch.jit.load('./models/cnn_ensemble.pth', map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        clean_temp(data_dir)
        
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/coordinates")
async def predict_by_coordinates(coordinates: Coordinates):
    try:
        results = resolve(ra=coordinates.ra, dec=coordinates.dec)
        data_dir = pull_data(results)
        
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        model = torch.jit.load('./models/cnn_ensemble.pth', map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        clean_temp(data_dir)
        
        return {"prediction": prediction.tolist()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)