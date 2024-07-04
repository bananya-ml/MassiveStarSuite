from astroquery.gaia import Gaia
from typing import List

def resolve(id:str=None, coords:List=None):
    
    if id:
        job = Gaia.launch_job_async(f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                            FROM gaiadr3.gaia_source_lite AS gaia3 \
                            JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                            ON gaia3.source_id = gaia3ap.source_id \
                            WHERE gaia3.source_id = {id}")
        results = job.get_results()
    elif coords:
        job = Gaia.launch_job_async(f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                    FROM gaiadr3.gaia_source_lite AS gaia3 \
                    JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                    ON gaia3.source_id = gaia3ap.source_id \
                    WHERE gaia3.ra = {coords[0]} AND gaia3.dec={coords[1]}")
        results = job.get_results()
    else:
        raise ValueError("Either 'id' or 'coords' must be provided!")
    
    if results.to_pandas().empty:
            print("No sources found!")
    else:
        _check_quality(results.to_pandas())
    return results.to_pandas()

def _check_quality(results):
    if (results['ruwe'] > 1.4).any() or results['parallax'].isnull().any() or (results['parallax_over_error'] <= 3).any():
        print("The source has poor parameters, it might not be properly resolved.")

    if (results['classprob_dsc_combmod_star']<0.5).any() or (results['classprob_dsc_specmod_star']<0.5).any():
        print("The source is most likely not a star.")
    
    if (results['has_xp_sampled'] != True).any():
        print("The source has no BP-RP spectrum data in Gaia Data Release 3!")


#if __name__ == "__main__":

    # test values
    #source_id = '4111834567779557376'
    #ra = '256.5229102004341'
    #dec = '-26.580565130784702'

    #results = resolve(id=source_id)#None,coords=list((ra,dec)))
