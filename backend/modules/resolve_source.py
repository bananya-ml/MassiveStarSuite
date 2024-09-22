"""
Source Resolution Module for Gaia Data

This module provides functions to resolve celestial sources using Gaia DR3 data. 
It includes custom exceptions for handling specific errors during source resolution 
and quality checks.

Classes:
    - NoSourceFoundError: Raised when no sources are found for the given ID or coordinates.
    - PoorSourceQualityError: Raised when the source does not meet the required quality criteria.
    - NoDataError: Raised when the source lacks necessary data in Gaia DR3.

Functions:
    - resolve(id: str = None, ra: str = None, dec: str = None) -> pd.DataFrame: 
      Resolves a source by either its ID or coordinates (RA, Dec) and checks its quality.
    - _check_quality(results: pd.DataFrame): 
      Performs quality checks on the resolved source data to ensure it meets criteria.

Dependencies:
    - astroquery.gaia.Gaia: Module from `astroquery` for querying Gaia data.
    - logging: Standard Python library for logging application events.

Usage:
    The `resolve` function is intended to be used by other modules or applications 
    that need to retrieve and validate Gaia source data. The `_check_quality` function 
    ensures the resolved sources meet specific quality thresholds before further processing.
"""

from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u
import logging
import re
import pandas as pd

# Set up module-level logger
logger = logging.getLogger(__name__)

#####################
# Custom Exceptions #
#####################

class NoSourceFoundError(Exception):
    """
    Custom exception raised when no sources are found during resolution.

    Attributes:
        message (str): The error message describing the cause of the failure.
    """
    pass

class PoorSourceQualityError(Exception):
    """
    Custom exception raised when a resolved source does not meet the required quality criteria.

    Attributes:
        message (str): The error message describing the quality issues found.
    """
    pass

class NoDataError(Exception):
    """
    Custom exception raised when the source lacks necessary data (e.g., BP-RP spectrum data) in Gaia DR3.

    Attributes:
        message (str): The error message describing the missing data issue.
    """
    pass

####################
# Public Functions #
####################

def resolve(id: str = None, ra: str = None, dec: str = None) -> pd.DataFrame:
    """
    Resolves a celestial source using Gaia DR3 data based on a given source ID or coordinates (RA, Dec).

    This function constructs a query to retrieve data for the specified source from Gaia DR3, 
    executes the query asynchronously, and checks the quality of the retrieved data.

    Args:
        id (str, optional): The source ID to resolve. Defaults to None.
        ra (str, optional): The right ascension (RA) of the source to resolve. Defaults to None.
        dec (str, optional): The declination (DEC) of the source to resolve. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the resolved source data.

    Raises:
        ValueError: If neither `id` nor `coords` (RA and DEC) are provided.
        NoSourceFoundError: If no sources are found matching the provided ID or coordinates.
        PoorSourceQualityError: If the resolved source does not meet the quality criteria.
        NoDataError: If the resolved source lacks necessary data in Gaia DR3.
    """
    logger.info(f"Resolving source. ID: {id}, RA: {ra}, DEC: {dec}")
    try:
        if id:
            if not id.isdigit():
                id = max(re.findall(r'\d+', id), key=len, default=None)
                if id is None:
                    raise ValueError("Invalid ID: No numeric values found.")
            query = (f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, "
                     f"gaia3.parallax_over_error, gaia3.ruwe, gaia3.has_xp_sampled, "
                     f"gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star, "
                     f"gaia3ap.classprob_dsc_combmod_binarystar, gaia3ap.classprob_dsc_specmod_binarystar, "
                     f"gaia3ap.classprob_dsc_combmod_galaxy, gaia3ap.classprob_dsc_specmod_galaxy, "
                     f"gaia3ap.classprob_dsc_combmod_quasar, gaia3ap.classprob_dsc_specmod_quasar, "
                     f"gaia3ap.classprob_dsc_allosmod_galaxy, gaia3ap.classprob_dsc_allosmod_star, "
                     f"gaia3ap.classprob_dsc_allosmod_quasar "
                     f"FROM gaiadr3.gaia_source_lite AS gaia3 "
                     f"JOIN gaiadr3.astrophysical_parameters AS gaia3ap "
                     f"ON gaia3.source_id = gaia3ap.source_id "
                     f"WHERE gaia3.source_id = {id}")
        elif ra and dec:
            if not (ra.replace('.', '', 1).isdigit() and dec.replace('.', '', 1).isdigit()):
                raise ValueError("RA and DEC must be numeric strings.")
            try:
                width = u.Quantity(0.1, u.deg)
                height = u.Quantity(0.1, u.deg)
                results_temp = Gaia.query_object_async(SkyCoord(ra=ra, dec=dec, unit=(u.degree, u.degree), frame='icrs'), width=width, height=height)
                
                if len(results_temp) == 0:
                    raise NoSourceFoundError(f"No sources found at RA={ra}, Dec={dec}")
                
                results_temp = results_temp[:1].to_pandas()  # Take only the first result
                
                query = (f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, "
                         f"gaia3.parallax_over_error, gaia3.ruwe, gaia3.has_xp_sampled, "
                         f"gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star, "
                         f"gaia3ap.classprob_dsc_combmod_binarystar, gaia3ap.classprob_dsc_specmod_binarystar, "
                         f"gaia3ap.classprob_dsc_combmod_galaxy, gaia3ap.classprob_dsc_specmod_galaxy, "
                         f"gaia3ap.classprob_dsc_combmod_quasar, gaia3ap.classprob_dsc_specmod_quasar, "
                         f"gaia3ap.classprob_dsc_allosmod_galaxy, gaia3ap.classprob_dsc_allosmod_star, "
                         f"gaia3ap.classprob_dsc_allosmod_quasar "
                         f"FROM gaiadr3.gaia_source_lite AS gaia3 "
                         f"JOIN gaiadr3.astrophysical_parameters AS gaia3ap "
                         f"ON gaia3.source_id = gaia3ap.source_id "
                         f"WHERE gaia3.ra = {results_temp['ra'].tolist()[0]} AND gaia3.dec= {results_temp['dec'].to_list()[0]}")
                del width, height, results_temp
            except Exception as e:
                logger.error(f"Error querying Gaia for RA={ra}, Dec={dec}: {str(e)}")
                raise ValueError("Either 'id' or 'coords' (ra, dec) must be provided!")
        else:
            raise ValueError("Either 'id' or 'coords' (ra, dec) must be provided!")

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

######################
# Internal Functions #
######################

def _check_quality(results: pd.DataFrame):
    """
    Performs quality checks on the resolved source data.

    This function checks for various quality metrics, such as RUWE, parallax, 
    and classification probabilities, to ensure the source data is reliable. 
    If the source does not meet the quality criteria, the function raises an 
    appropriate exception.

    Args:
        results (pd.DataFrame): The DataFrame containing the resolved source data.

    Raises:
        PoorSourceQualityError: If the source does not meet the quality criteria.
        NoDataError: If the source lacks BP-RP spectrum data in Gaia DR3.
    """
    issues = []
    
    # Check if the source has poor parameters or classification probabilities
    if (results['ruwe'] > 1.4).any() or results['parallax'].isnull().any() or (results['parallax_over_error'] <= 3).any():
        issues.append("The source has poor parameters, it might not be properly resolved.")
    
    # Check classification probabilities for all categories
    star_probs = [
        results['classprob_dsc_combmod_star'],
        results['classprob_dsc_specmod_star'],
        results['classprob_dsc_combmod_binarystar'],
        results['classprob_dsc_specmod_binarystar'],
        results['classprob_dsc_combmod_galaxy'],
        results['classprob_dsc_specmod_galaxy'],
        results['classprob_dsc_combmod_quasar'],
        results['classprob_dsc_specmod_quasar'],
        results['classprob_dsc_allosmod_galaxy'],
        results['classprob_dsc_allosmod_star'],
        results['classprob_dsc_allosmod_quasar']
    ]

    # Raise issues only for galaxy or quasar classifications
    if (results['classprob_dsc_combmod_galaxy'] >= 0.5).any() or (results['classprob_dsc_combmod_quasar'] >= 0.5).any() or (results['classprob_dsc_allosmod_galaxy'] >= 0.5).any() or (results['classprob_dsc_allosmod_quasar'] >= 0.5).any():
        issues.append("The source is most likely a galaxy or quasar.")

    # Check if the source has the necessary BP-RP spectrum data
    if (results['has_xp_sampled'] != True).any():
        logger.error("The source has no BP-RP spectrum data in Gaia Data Release 3")
        raise NoDataError("The source has no BP-RP spectrum data in Gaia Data Release 3!")

    # If there are any quality issues, raise an exception
    if issues:
        logger.warning(f"Quality issues detected: {'; '.join(issues)}")
        raise PoorSourceQualityError("; ".join(issues))

    logger.info("Quality check passed")