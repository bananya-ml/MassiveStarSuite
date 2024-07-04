import os
from astroquery.gaia import Gaia

def pull_data(results):
    retrieval_type = 'XP_SAMPLED'  
    data_structure = 'INDIVIDUAL'
    data_release   = 'Gaia DR3'
    dl_key         = f'{retrieval_type}_{data_structure}.xml'

    datalink  = Gaia.load_data(ids=results['SOURCE_ID'], data_release = data_release, retrieval_type=retrieval_type, format = 'csv', data_structure = data_structure)
    
    for dl_key in datalink.keys():
        if 'XP_SAMPLED' in dl_key: 
            product = datalink[dl_key][0]
            
            file_name = f"{dl_key.replace('.xml', '').replace(' ','_').replace('-','_')}"

            print(f'Writing table as: {file_name}')
            data_dir = './temp'
            if os.path.exists(data_dir):
                product.write(os.path.join(data_dir,file_name), format = 'csv', overwrite = True)
            else:
                os.makedirs(data_dir)
                product.write(os.path.join(data_dir,file_name), format = 'csv', overwrite = True)
    return data_dir