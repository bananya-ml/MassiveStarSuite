import pandas as pd
import glob
import torch
import shutil

def inference(model, X):
        model.eval()
        with torch.no_grad():
            output = model(X.unsqueeze(1))
            prob = torch.sigmoid(output)
            prediction = torch.round(prob).numpy().astype(float)
            return prediction

#if __name__ == "__main__":
    
    #data_dir = './temp'
    #file = '*.csv'

    #csv_files = glob.glob(f"{data_dir}/{file}")
    #data = pd.read_csv(csv_files[0])
    #X = data['flux'].to_numpy()

    #model = torch.jit.load('../models/cnn_ensemble.pth', map_location=torch.device('cpu'))
    #prediction = inference(model, torch.from_numpy(X).float().unsqueeze(0))
    #print(prediction)
    #try:
        #shutil.rmtree(data_dir)
        #print(f"Deleted {data_dir} directory and its contents.")
    #except Exception as e:
        #print(f"Error deleting {data_dir} directory: {e}")