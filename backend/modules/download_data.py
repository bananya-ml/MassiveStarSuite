import os
import logging
from astroquery.gaia import Gaia

logger = logging.getLogger(__name__)

class DataDownloadError(Exception):
    pass

def pull_data(results):
    logger.info(f"Starting data pull for source ID: {results['SOURCE_ID']}")
    try:
        retrieval_type = 'XP_SAMPLED'  
        data_structure = 'INDIVIDUAL'
        data_release   = 'Gaia DR3'
        dl_key         = f'{retrieval_type}_{data_structure}.xml'

        logger.debug(f"Retrieving data with parameters: retrieval_type={retrieval_type}, data_structure={data_structure}, data_release={data_release}")
        datalink  = Gaia.load_data(ids=results['SOURCE_ID'], data_release=data_release, retrieval_type=retrieval_type, format='csv', data_structure=data_structure)
        
        data_dir = './temp'
        os.makedirs(data_dir, exist_ok=True)

        for dl_key in datalink.keys():
            if 'XP_SAMPLED' in dl_key: 
                product = datalink[dl_key][0]
                
                file_name = f"{dl_key.replace('.xml', '').replace(' ','_').replace('-','_')}"

                logger.info(f'Writing table as: {file_name}')
                product.write(os.path.join(data_dir, file_name), format='csv', overwrite=True)
        
        logger.info(f"Data successfully downloaded to {data_dir}")
        return data_dir
    except Exception as e:
        logger.error(f"Error occurred while pulling data: {str(e)}", exc_info=True)
        raise DataDownloadError(f"Failed to download data: {str(e)}")