"""
Inference Module for Machine Learning Model Predictions

This module handles the inference process using a PyTorch model. It includes 
a custom exception class for handling errors that may occur during the 
inference process.

Classes:
    - InferenceError: Custom exception raised when an error occurs during inference.

Functions:
    - inference(model: torch.nn.Module, X: torch.Tensor) -> np.ndarray: 
      Performs inference on input data using a trained PyTorch model.

Dependencies:
    - torch: PyTorch library for handling deep learning models and operations.
    - logging: Standard Python library for logging application events.

Usage:
    The `inference` function is intended to be used by other modules or 
    applications that require predictions from a trained PyTorch model. 
    It takes input data, performs inference, and returns the prediction.
"""

import torch
import logging
import numpy as np

# Set up module-level logger
logger = logging.getLogger(__name__)

class InferenceError(Exception):
    """
    Custom exception raised when there is an error during model inference.

    Attributes:
        message (str): The error message describing the cause of the failure.
    """
    pass

def l2_normalize(tensor: torch.Tensor, eps: float = 1e-10) -> torch.Tensor:
    """
    L2 normalizes the input tensor.
    
    Args:
        tensor (torch.Tensor): The input tensor to normalize.
        eps (float): A small value to avoid division by zero.
    
    Returns:
        torch.Tensor: The L2-normalized tensor.
    """
    norm = tensor.norm(p=2, dim=1, keepdim=True)
    return tensor / norm

def inference(model: torch.nn.Module, X: torch.Tensor) -> np.ndarray:
    """
    Performs inference using a trained PyTorch model on the provided input data.

    This function sets the model to evaluation mode, disables gradient computation, 
    and processes the input tensor through the model to generate predictions. 
    The predictions are then converted to a numpy array and returned.

    Args:
        model torch.nn.Module: The PyTorch model to be used for inference.
        X (torch.Tensor): The input tensor data on which inference is performed. 
                          Expected to be a 2D tensor where each row represents 
                          a sample and each column a feature.

    Returns:
        np.ndarray: The prediction results as a numpy array of floats.

    Raises:
        InferenceError: If any error occurs during the inference process.
    """
    logger.info("Starting inference")
    try:
        # Perform L2 normalization on the input
        X = l2_normalize(X)

        # Set model to evaluation mode
        model.eval()

        # Perform inference without tracking gradients
        with torch.no_grad():
            logger.debug(f"Input shape: {X.shape}")
            
            # Add an additional dimension to match expected input shape
            output = model(X.unsqueeze(1))
            
            # Apply sigmoid activation to convert output to probabilities
            prob = torch.sigmoid(output)
            logger.debug(f"Probability: {prob}")

        # Round the probabilities to get binary predictions
        prediction = torch.round(prob).numpy().astype(float)

        logger.info(f"Inference completed. Prediction shape: {prediction.shape} and prediction: {prediction}")
        return prediction

    except Exception as e:
        # Log the error and raise a custom exception
        logger.error(f"Error occurred during inference: {str(e)}", exc_info=True)
        raise InferenceError(f"Inference failed: {str(e)}")