"""
Data Download Module for Gaia Source Data

This module handles the downloading of data from the Gaia astronomical database 
using the `astroquery` library. It includes a custom exception class for error 
handling during the data retrieval process.

Classes:
    - DataDownloadError: Custom exception raised when data download fails.

Functions:
    - pull_data(results: dict) -> str: Downloads data for a given source ID from 
      the Gaia database and saves it as a CSV file.

Dependencies:
    - os: Standard Python library for interacting with the operating system.
    - logging: Standard Python library for logging application events.
    - astroquery.gaia.Gaia: Module from `astroquery` for querying Gaia data.

Usage:
    The `pull_data` function is intended to be used by other modules or 
    applications requiring Gaia data. It retrieves data based on source IDs and 
    saves it to a temporary directory for further processing.
"""

import os
import logging
from astroquery.gaia import Gaia

# Set up module-level logger
logger = logging.getLogger(__name__)

class DataDownloadError(Exception):
    """
    Custom exception raised when there is an error in downloading data from Gaia.

    Attributes:
        message (str): The error message describing the cause of the failure.
    """
    pass

def pull_data(results: dict) -> str:
    """
    Downloads data from the Gaia database for a given source ID.

    This function retrieves data related to a specific source ID using the Gaia DR3 
    data release and stores the data in a temporary directory. It logs each step 
    of the process, including any errors that occur.

    Args:
        results (dict): A dictionary containing the resolved results, including 
                        the 'SOURCE_ID' used to identify the data to be downloaded.

    Returns:
        str: The path to the directory where the data has been downloaded.

    Raises:
        DataDownloadError: If there is any issue during the data retrieval or 
                           file writing process.
    """
    logger.info(f"Starting data pull for source ID: {results['SOURCE_ID']}")
    try:
        # Parameters for data retrieval from Gaia
        retrieval_type = 'XP_SAMPLED'  
        data_structure = 'INDIVIDUAL'
        data_release = 'Gaia DR3'

        # Log the parameters used for the data retrieval
        logger.debug(f"Retrieving data with parameters: retrieval_type={retrieval_type}, data_structure={data_structure}, data_release={data_release}")

        # Retrieve data from Gaia using the specified parameters
        datalink = Gaia.load_data(
            ids=results['SOURCE_ID'], 
            data_release=data_release, 
            retrieval_type=retrieval_type, 
            format='csv', 
            data_structure=data_structure
        )

        # Directory to store the downloaded data
        data_dir = './temp'
        os.makedirs(data_dir, exist_ok=True)

        # Save the retrieved data to the directory
        for dl_key in datalink.keys():
            if 'XP_SAMPLED' in dl_key:  # Filter to ensure correct data type
                product = datalink[dl_key][0]
                
                # Clean the filename for saving
                file_name = f"{dl_key.replace('.xml', '').replace(' ','_').replace('-','_')}"

                logger.info(f'Writing table as: {file_name}')
                product.write(os.path.join(data_dir, file_name), format='csv', overwrite=True)
        
        logger.info(f"Data successfully downloaded to {data_dir}")
        return data_dir
    
    except Exception as e:
        # Log the error and raise a custom exception
        logger.error(f"Error occurred while pulling data: {str(e)}", exc_info=True)
        raise DataDownloadError(f"Failed to download data: {str(e)}")