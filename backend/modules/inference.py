import torch

def inference(model, X):
        model.eval()
        with torch.no_grad():
            output = model(X.unsqueeze(1))
            prob = torch.sigmoid(output)
            prediction = torch.round(prob).numpy().astype(float)
            return prediction