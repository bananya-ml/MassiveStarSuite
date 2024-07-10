import torch
import logging

logger = logging.getLogger(__name__)

class InferenceError(Exception):
    pass

def inference(model, X):
    logger.info("Starting inference")
    try:
        model.eval()
        with torch.no_grad():
            logger.debug(f"Input shape: {X.shape}")
            output = model(X.unsqueeze(1))
            prob = torch.sigmoid(output)
            prediction = torch.round(prob).numpy().astype(float)
            logger.info(f"Inference completed. Prediction shape: {prediction.shape}")
            return prediction
    except Exception as e:
        logger.error(f"Error occurred during inference: {str(e)}", exc_info=True)
        raise InferenceError(f"Inference failed: {str(e)}")