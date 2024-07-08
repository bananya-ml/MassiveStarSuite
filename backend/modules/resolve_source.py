from astroquery.gaia import Gaia

class NoSourceFoundError(Exception):
    pass

class PoorSourceQualityError(Exception):
    pass

class NoDataError(Exception):
    pass

def resolve(id:str=None, ra:str=None, dec:str=None):
    
    if id:
        job = Gaia.launch_job_async(f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                            FROM gaiadr3.gaia_source_lite AS gaia3 \
                            JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                            ON gaia3.source_id = gaia3ap.source_id \
                            WHERE gaia3.source_id = {id}")
        results = job.get_results()
    elif ra and dec:
        job = Gaia.launch_job_async(f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                    FROM gaiadr3.gaia_source_lite AS gaia3 \
                    JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                    ON gaia3.source_id = gaia3ap.source_id \
                    WHERE gaia3.ra = {ra} AND gaia3.dec= {dec}")
        results = job.get_results()
    else:
        raise ValueError("Either 'id' or 'coords' must be provided!")
    
    if results.to_pandas().empty:
        raise NoSourceFoundError("No sources found!")
    
    df_results = results.to_pandas()
    _check_quality(df_results)
    return df_results

def _check_quality(results):
    issues = []
    if (results['ruwe'] > 1.4).any() or results['parallax'].isnull().any() or (results['parallax_over_error'] <= 3).any():
        issues.append("The source has poor parameters, it might not be properly resolved.")

    if (results['classprob_dsc_combmod_star']<0.5).any() or (results['classprob_dsc_specmod_star']<0.5).any():
        issues.append("The source is most likely not a star.")
    
    if (results['has_xp_sampled'] != True).any():
        raise NoDataError("The source has no BP-RP spectrum data in Gaia Data Release 3!")
    
    if issues:
        raise PoorSourceQualityError("; ".join(issues))