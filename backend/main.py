"""
Main FastAPI Application for Predictive Model Inference

This application provides endpoints for making predictions based on 
source IDs or celestial coordinates. It includes CORS middleware, 
detailed logging, and custom error handling.

Modules:
    - resolve_source: Handles source resolution and validation.
    - download_data: Manages data retrieval from external sources.
    - inference: Performs model inference on the retrieved data.

Environment Variables:
    - ENVIRONMENT: Specifies the environment (default: 'production').
    - PORT: The port number on which the application runs (default: 8000).
    - ALLOWED_ORIGINS: Allowed origins for CORS (default: 'http://localhost:5173').
    - LOG_LEVEL: Sets the logging level (default: 'INFO').
    - MODEL_PATH: Path to the saved model file (default: './models/cnn_ensemble.pth').

Endpoints:
    - GET /: Health check endpoint to verify the server is running.
    - POST /predict/id: Predict based on a source ID.
    - POST /predict/coordinates: Predict based on celestial coordinates (RA and Dec).
"""
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

#########################
# Environment Variables #
#########################
ENVIRONMENT = os.getenv('ENVIRONMENT', 'production')
PORT = int(os.getenv('PORT', 8000))
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
MODEL_PATH = os.getenv('MODEL_PATH', './models/cnn_ensemble.pth')

#################
# Logging Setup #
#################

# Create a log directory and file with a timestamp.
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"{current_time}.log")

# Configure logging to file and console with detailed formatting.
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger = logging.getLogger()
logging.basicConfig(level=LOG_LEVEL, handlers=[file_handler, console_handler])

# Log the start of the application
logger.info(f"Starting application. Log file: {log_file}")

#################
# FastAPI Setup #
#################

app = FastAPI()

# Enable CORS to allow requests from specified origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

##########
# Models #
##########

# Define Pydantic models for request validation.
class SourceID(BaseModel):
    source_id: str

class Coordinates(BaseModel):
    ra: float
    dec: float

class ErrorResponse(BaseModel):
    error: str
    detail: str

#####################
# Utility Functions #
#####################

def _clean_temp(data_dir):
    try:
        shutil.rmtree(data_dir)
        logger.info(f"Deleted {data_dir} directory and its contents.")
    except Exception as e:
        logger.error(f"Error deleting {data_dir} directory: {e}")

##########################
# Custom Error Handlers #
##########################

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

######################
# Endpoint Handlers #
######################

@app.get("/")
async def check():
    """
    Health check endpoint to verify that the server is running.

    Returns:
        str: A simple message indicating the server is running.
    """
    return "Server is running!"

@app.post("/predict/id", response_model=dict, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def predict_by_id(source_id: SourceID, request: Request):
    """
    Predict based on a given source ID.

    Args:
        source_id (SourceID): The ID of the source to predict.
        request (Request): The incoming request object.

    Returns:
        dict: The prediction result along with the source's RA and Dec.
    """
    correlation_id = request.headers.get('X-Correlation-ID', 'No-Correlation-ID')
    logger.info(f"Received prediction request for source ID: {source_id.source_id}, Correlation ID: {correlation_id}")
    start_time = time.time()
    try:
        # Resolve the source ID to obtain coordinates.
        results = resolve(id=source_id.source_id)
        logger.debug(f"Resolved source ID {source_id.source_id}: RA={results['ra']}, Dec={results['dec']}")
        
        # Pull the necessary data for the prediction.
        data_dir = pull_data(results)
        logger.debug(f"Pulled data to directory: {data_dir}")
        
        # Read the CSV file containing the data.
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        # Load the model and perform inference.
        model = torch.jit.load(MODEL_PATH, map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        # Clean up temporary data directory.
        _clean_temp(data_dir)
        
        end_time = time.time()
        logger.info(f"Prediction for source ID {source_id.source_id} completed in {end_time - start_time:.2f} seconds")
        
        # Return the prediction and resolved coordinates.
        return {
            "prediction": prediction.tolist(),
            "ra": float(results['ra'].iloc[0]),
            "dec": float(results['dec'].iloc[0])
        }
    except (NoSourceFoundError, PoorSourceQualityError, NoDataError) as e:
        # Handle known errors related to source resolution and data quality.
        logger.warning(f"Source-related error for ID {source_id.source_id}: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except (DataDownloadError, InferenceError) as e:
        # Handle errors during data download or inference.
        logger.error(f"Processing error for ID {source_id.source_id}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except Exception as e:
        # Handle any unexpected errors.
        logger.error(f"Unexpected error processing ID {source_id.source_id}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "UnexpectedError", "detail": str(e)}
        )

@app.post("/predict/coordinates", response_model=dict, responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def predict_by_coordinates(coordinates: Coordinates, request: Request):
    """
    Predict based on given celestial coordinates (RA and Dec).

    Args:
        coordinates (Coordinates): The celestial coordinates (RA and Dec).
        request (Request): The incoming request object.

    Returns:
        dict: The prediction result for the given coordinates.
    """
    correlation_id = request.headers.get('X-Correlation-ID', 'No-Correlation-ID')
    logger.info(f"Received prediction request for coordinates: RA={coordinates.ra}, Dec={coordinates.dec}, Correlation ID: {correlation_id}")
    start_time = time.time()
    try:
        # Resolve the coordinates to obtain additional data.
        results = resolve(ra=coordinates.ra, dec=coordinates.dec)
        logger.debug(f"Resolved coordinates: RA={results['ra']}, Dec={results['dec']}")
        
        # Pull the necessary data for the prediction.
        data_dir = pull_data(results)
        logger.debug(f"Pulled data to directory: {data_dir}")
        
        # Read the CSV file containing the data.
        file = '*.csv'
        csv_files = glob.glob(f"{data_dir}/{file}")
        data = pd.read_csv(csv_files[0])
        X = data['flux'].to_numpy()
        
        # Load the model and perform inference.
        model = torch.jit.load('./models/cnn_ensemble.pth', map_location=torch.device('cpu'))
        prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
        
        # Clean up temporary data directory.
        _clean_temp(data_dir)
        
        end_time = time.time()
        logger.info(f"Prediction for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}) completed in {end_time - start_time:.2f} seconds")
        
        # Return the prediction result.
        return {"prediction": prediction.tolist()}
    except (NoSourceFoundError, PoorSourceQualityError, NoDataError) as e:
        # Handle known errors related to source resolution and data quality.
        logger.warning(f"Source-related error for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except (DataDownloadError, InferenceError) as e:
        # Handle errors during data download or inference.
        logger.error(f"Processing error for coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": e.__class__.__name__, "detail": str(e)}
        )
    except Exception as e:
        # Handle any unexpected errors.
        logger.error(f"Unexpected error processing coordinates (RA={coordinates.ra}, Dec={coordinates.dec}): {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "UnexpectedError", "detail": str(e)}
        )

####################
# Application Entry #
####################

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting the FastAPI application")
    uvicorn.run(app, host="0.0.0.0", port=PORT)