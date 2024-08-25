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
import logging
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
        dec (str, optional): The declination (Dec) of the source to resolve. Defaults to None.

    Returns:
        pd.DataFrame: A DataFrame containing the resolved source data.

    Raises:
        ValueError: If neither `id` nor `coords` (RA and Dec) are provided.
        NoSourceFoundError: If no sources are found matching the provided ID or coordinates.
        PoorSourceQualityError: If the resolved source does not meet the quality criteria.
        NoDataError: If the resolved source lacks necessary data in Gaia DR3.
    """
    logger.info(f"Resolving source. ID: {id}, RA: {ra}, DEC: {dec}")
    try:
        if id:
            query = (f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, "
                     f"gaia3.parallax_over_error, gaia3.ruwe, gaia3.has_xp_sampled, "
                     f"gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star "
                     f"FROM gaiadr3.gaia_source_lite AS gaia3 "
                     f"JOIN gaiadr3.astrophysical_parameters AS gaia3ap "
                     f"ON gaia3.source_id = gaia3ap.source_id "
                     f"WHERE gaia3.source_id = {id}")
        elif ra and dec:
            query = (f"SELECT gaia3.source_id, gaia3.ra, gaia3.dec, gaia3.parallax, "
                     f"gaia3.parallax_over_error, gaia3.ruwe, gaia3.has_xp_sampled, "
                     f"gaia3ap.classprob_dsc_combmod_star, gaia3ap.classprob_dsc_specmod_star "
                     f"FROM gaiadr3.gaia_source_lite AS gaia3 "
                     f"JOIN gaiadr3.astrophysical_parameters AS gaia3ap "
                     f"ON gaia3.source_id = gaia3ap.source_id "
                     f"WHERE gaia3.ra = {ra} AND gaia3.dec= {dec}")
        else:
            raise ValueError("Either 'id' or 'coords' (RA, Dec) must be provided!")

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

#####################
# Private Functions #
#####################

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
    
    if (results['classprob_dsc_combmod_star'] < 0.5).any() or (results['classprob_dsc_specmod_star'] < 0.5).any():
        issues.append("The source is most likely not a star.")
    
    # Check if the source has the necessary BP-RP spectrum data
    if (results['has_xp_sampled'] != True).any():
        logger.error("The source has no BP-RP spectrum data in Gaia Data Release 3")
        raise NoDataError("The source has no BP-RP spectrum data in Gaia Data Release 3!")

    # If there are any quality issues, raise an exception
    if issues:
        logger.warning(f"Quality issues detected: {'; '.join(issues)}")
        raise PoorSourceQualityError("; ".join(issues))

    logger.info("Quality check passed")