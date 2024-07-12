from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from modules.resolve_source import resolve, NoSourceFoundError, PoorSourceQualityError, NoDataError
from modules.download_data import pull_data, DataDownloadError
from modules.inference import inference, InferenceError

import glob
import pandas as pd
import shutil
import torch
import logging
import os
import time
from datetime import datetime

# environment variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
PORT = int(os.getenv('PORT', 8000))
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MODEL_PATH = os.getenv('MODEL_PATH', './models/cnn_ensemble.pth')

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"{current_time}.log")

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logging.basicConfig(level=LOG_LEVEL, handlers=[file_handler, console_handler])

# log the start of the application
logger.info(f"Starting application. Log file: {log_file}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

class SourceID(BaseModel):
    source_id: str

class Coordinates(BaseModel):
    ra: float
    dec: float

class ErrorResponse(BaseModel):
    error: str
    detail: str

def _clean_temp(data_dir):
    try:
        shutil.rmtree(data_dir)
        logger.info(f"Deleted {data_dir} directory and its contents.")
    except Exception as e:
        logger.error(f"Error deleting {data_dir} directory: {e}")

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

@app.post("/predict/id", response_model=dict, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def predict_by_id(source_id: SourceID, request: Request):
    correlation_id = request.headers.get('X-Correlation-ID', 'No-Correlation-ID')
    logger.info(f"Received prediction request for source ID: {source_id.source_id}, Correlation ID: {correlation_id}")
    start_time = time.time()
    try:
        results = resolve(id=source_id.source_id)
        logger.debug(f"Resolved source ID {source_id.source_id}: RA={results['ra']}, Dec={results['dec']}")
        
        data_dir = pull_data(results)
        logger.debug(f"Pulled data to directory: {data_dir}")
        
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        model = torch.jit.load(MODEL_PATH, map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        _clean_temp(data_dir)
        
        end_time = time.time()
        logger.info(f"Prediction for source ID {source_id.source_id} completed in {end_time - start_time:.2f} seconds")
        
        return {
            "prediction": prediction.tolist(),
            "ra": float(results['ra'].iloc[0]),
            "dec": float(results['dec'].iloc[0])
        }
    except (NoSourceFoundError, PoorSourceQualityError, NoDataError) as e:
        logger.warning(f"Source-related error for ID {source_id.source_id}: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except (DataDownloadError, InferenceError) as e:
        logger.error(f"Processing error for ID {source_id.source_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error processing ID {source_id.source_id}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "UnexpectedError", "detail": str(e)}
        )

@app.post("/predict/coordinates", response_model=dict, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def predict_by_coordinates(coordinates: Coordinates, request: Request):
    correlation_id = request.headers.get('X-Correlation-ID', 'No-Correlation-ID')
    logger.info(f"Received prediction request for coordinates: RA={coordinates.ra}, Dec={coordinates.dec}, Correlation ID: {correlation_id}")
    start_time = time.time()
    try:
        results = resolve(ra=coordinates.ra, dec=coordinates.dec)
        logger.debug(f"Resolved coordinates: RA={results['ra']}, Dec={results['dec']}")
        
        data_dir = pull_data(results)
        logger.debug(f"Pulled data to directory: {data_dir}")
        
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        model = torch.jit.load('./models/cnn_ensemble.pth', map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        _clean_temp(data_dir)
        
        end_time = time.time()
        logger.info(f"Prediction for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}) completed in {end_time - start_time:.2f} seconds")
        
        return {"prediction": prediction.tolist()}
    except (NoSourceFoundError, PoorSourceQualityError, NoDataError) as e:
        logger.warning(f"Source-related error for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except (DataDownloadError, InferenceError) as e:
        logger.error(f"Processing error for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error processing coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "UnexpectedError", "detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=PORT)