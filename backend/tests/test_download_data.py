import pandas as pd
from modules.download_data import pull_data

if __name__ == "__main__":
    
    # test data
    results = pd.DataFrame({'SOURCE_ID':['4111834567779557376']})
    data_dir = pull_data(results)