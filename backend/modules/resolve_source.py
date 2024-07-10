from astroquery.gaia import Gaia
import logging

logger = logging.getLogger(__name__)

class NoSourceFoundError(Exception):
    pass

class PoorSourceQualityError(Exception):
    pass

class NoDataError(Exception):
    pass

def resolve(id:str=None, ra:str=None, dec:str=None):
    logger.info(f"Resolving source. ID: {id}, RA: {ra}, DEC: {dec}")
    try:
        if id:
            query = f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                                FROM gaiadr3.gaia_source_lite AS gaia3 \
                                JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                                ON gaia3.source_id = gaia3ap.source_id \
                                WHERE gaia3.source_id = {id}"
        elif ra and dec:
            query = f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, gaia3.parallax_over_error,gaia3.ruwe, gaia3.has_xp_sampled, gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star \
                        FROM gaiadr3.gaia_source_lite AS gaia3 \
                        JOIN gaiadr3.astrophysical_parameters AS gaia3ap \
                        ON gaia3.source_id = gaia3ap.source_id \
                        WHERE gaia3.ra = {ra} AND gaia3.dec= {dec}"
        else:
            raise ValueError("Either 'id' or 'coords' must be provided!")
        
        logger.debug(f"Executing query: {query}")
        job = Gaia.launch_job_async(query)
        results = job.get_results()
        
        if results.to_pandas().empty:
            logger.warning("No sources found")
            raise NoSourceFoundError("No sources found!")
        
        df_results = results.to_pandas()
        _check_quality(df_results)
        logger.info("Source resolved successfully")
        return df_results
    except Exception as e:
        logger.error(f"Error occurred while resolving source: {str(e)}", exc_info=True)
        raise

def _check_quality(results):
    issues = []
    if (results['ruwe'] > 1.4).any() or results['parallax'].isnull().any() or (results['parallax_over_error'] <= 3).any():
        issues.append("The source has poor parameters, it might not be properly resolved.")

    if (results['classprob_dsc_combmod_star']<0.5).any() or (results['classprob_dsc_specmod_star']<0.5).any():
        issues.append("The source is most likely not a star.")
    
    if (results['has_xp_sampled'] != True).any():
        logger.error("The source has no BP-RP spectrum data in Gaia Data Release 3")
        raise NoDataError("The source has no BP-RP spectrum data in Gaia Data Release 3!")
    
    if issues:
        logger.warning(f"Quality issues detected: {'; '.join(issues)}")
        raise PoorSourceQualityError("; ".join(issues))
    
    logger.info("Quality check passed")