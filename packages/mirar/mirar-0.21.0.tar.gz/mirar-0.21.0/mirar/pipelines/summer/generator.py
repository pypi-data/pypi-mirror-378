"""
Module containing functions to generate astrometric/photometric calibration catalogs
for SUMMER
"""

import logging

from astropy.table import Table

from mirar.catalog import BaseCatalog, Gaia2Mass
from mirar.catalog.vizier import PS1, SkyMapper
from mirar.catalog.vizier.sdss import SDSS, NotInSDSSError, in_sdss
from mirar.data.image_data import Image
from mirar.pipelines.summer.config import (
    psfex_config_path,
    sextractor_photometry_config,
    swarp_config_path,
)
from mirar.processors.astromatic import PSFex, Sextractor, Swarp
from mirar.processors.astromatic.sextractor.sextractor import SEXTRACTOR_HEADER_KEY
from mirar.references import BaseReferenceGenerator, PS1Ref, SDSSRef

logger = logging.getLogger(__name__)


def summer_astrometric_catalog_generator(image: Image) -> Gaia2Mass:
    """
    Returns an astrometric catalog for summer,
    which is just a Gaia/2MASS one

    :param image: image to generate a catalog for
    :return: Gaia/2MASS catalog around image
    """
    temp_cat_path = image[SEXTRACTOR_HEADER_KEY]
    cat = Gaia2Mass(
        min_mag=10,
        max_mag=20,
        search_radius_arcmin=7.5,
        trim=True,
        image_catalog_path=temp_cat_path,
        filter_name="j",
        acceptable_j_ph_quals=["A", "B", "C"],
    )
    return cat


def summer_photometric_catalog_generator(image: Image) -> BaseCatalog:
    """
    Generate a photometric calibration catalog for SUMMER images

    For u band: SDSS if possible, otherwise Skymapper, otherwise fail
    For g/r1: use PS1

    :param image: Image
    :return: catalog at image position
    """
    filter_name = image["FILTERID"]
    dec = image["DEC"]

    if filter_name in ["u", "U"]:
        if in_sdss(image["RA"], image["DEC"]):
            return SDSS(
                min_mag=10,
                max_mag=20,
                search_radius_arcmin=7.5,
                filter_name=filter_name,
            )

        if dec < 0.0:
            return SkyMapper(
                min_mag=10,
                max_mag=20,
                search_radius_arcmin=7.5,
                filter_name=filter_name,
            )

        err = "U band image is in a field with no reference image."
        logger.error(err)
        raise NotInSDSSError(err)

    return PS1(
        min_mag=10, max_mag=20, search_radius_arcmin=7.5, filter_name=filter_name
    )


def summer_reference_image_generator(image: Image) -> BaseReferenceGenerator:
    """
    Get a reference image generator for a SUMMER image

    For u band: SDSS if possible, otherwise fail
    For g/r1: use PS1

    :param image: image
    :return: Reference image generator
    """
    filter_name = image["FILTER"]
    logger.debug(f"Filter is {filter_name}")

    if filter_name in ["u", "U"]:
        if in_sdss(image["RA"], image["DEC"]):
            logger.debug("Will query reference image from SDSS")
            return SDSSRef(filter_name=filter_name)

        err = "U band image is in a field with no reference image."
        logger.error(err)
        raise NotInSDSSError(err)

    logger.debug("Will query reference image from PS1")
    return PS1Ref(filter_name=filter_name)


def summer_reference_image_resampler(**kwargs) -> Swarp:
    """
    Generates a resampler for reference images

    :param kwargs: kwargs
    :return: Swarp processor
    """
    return Swarp(
        swarp_config_path=swarp_config_path, cache=True, subtract_bkg=True, **kwargs
    )


def summer_reference_sextractor(output_sub_dir: str) -> Sextractor:
    """
    Generates a sextractor processor for reference images

    :param output_sub_dir: output sui directory
    :param gain: gain of image
    :return: Sextractor processor
    """
    return Sextractor(
        output_sub_dir=output_sub_dir,
        cache=True,
        **sextractor_photometry_config,
    )


def summer_reference_psfex(output_sub_dir: str, norm_fits: bool) -> PSFex:
    """
    Generates a PSFex processor for reference images

    :param output_sub_dir: output sui directory
    :param norm_fits: boolean
    :return: Sextractor processor
    """
    return PSFex(
        config_path=psfex_config_path,
        output_sub_dir=output_sub_dir,
        norm_fits=norm_fits,
    )


def summer_zogy_catalogs_purifier(sci_catalog: Table, ref_catalog: Table):
    """
    :param sci_catalog: science catalog
    :param ref_catalog: reference catalog
    :return: good_sci_sources, good_ref_sources
    """
    # Need to do this because the summer data is typically much
    # shallower than the PS1 data, and only the brightest
    # sources in PS1 xmatch to it.
    good_sci_sources = (
        (sci_catalog["FLAGS"] == 0)
        & (sci_catalog["SNR_WIN"] > 5)
        & (sci_catalog["FWHM_WORLD"] < 4.0 / 3600)
        & (sci_catalog["FWHM_WORLD"] > 0.5 / 3600)
        & (sci_catalog["SNR_WIN"] < 1000)
    )

    good_ref_sources = (
        (ref_catalog["SNR_WIN"] > 5)
        & (ref_catalog["FWHM_WORLD"] < 5.0 / 3600)
        & (ref_catalog["FWHM_WORLD"] > 0.5 / 3600)
    )

    return good_sci_sources, good_ref_sources
