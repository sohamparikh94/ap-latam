#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Train a detection model from a set of preprocessed rasters and a vector file of
polygons.

"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
import rasterio
import fiona 
from aplatam import __version__
from aplatam.util import all_raster_files


__author__ = "Dymaxion Labs"
__copyright__ = __author__
__license__ = "new-bsd"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """
    Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace

    """
    parser = argparse.ArgumentParser(
        description="...")
    parser.add_argument(
        '--version',
        action='version',
        version='aplatam {ver}'.format(ver=__version__))

    parser.add_argument(
        'rasters_dir',
        help='directory containing raster images')
    parser.add_argument(
        'vector',
        help='vector file of polygons')
    parser.add_argument(
        '-c',
        '--config-file',
        help='configuration file')
    parser.add_argument(
        '-o',
        '--output-model',
        default='model.h5',
        help='filename for output model')
    parser.add_argument(
        '--seed',
        type=int,
        help='seed number for the random number generator')

    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """
    Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages

    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """
    Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    """
    args = parse_args(args)
    setup_logging(args.loglevel)

    _logger.debug('Collect all rasters')
    rasters = all_raster_files(args.rasters_dir)
    _logger.debug(rasters)
    validate_rasters_crs(rasters)
    validate_vector_crs(rasters, args.vector)


    #_logger.debug("Validate rasters")

    _logger.info("Done")

def validate_rasters_crs(rasters):
    _logger.debug('Validate rasters crs')
    prev_crs = None 
    for raster_path in rasters:
        with rasterio.open(raster_path) as dataset: 
            if prev_crs is not None and prev_crs != dataset.crs :
                raise RuntimeError('CRC mismatch in some raster')
            prev_crs = dataset.crs

def validate_vector_crs(rasters, vector):
    _logger.debug('Validate vector crs')
    with fiona.open(vector) as vector_src:
        vect_crs = vector_src.crs
    with rasterio.open(rasters[0]) as raster_src:
        raster_crs = raster_src
    if vect_crs != raster_crs:
        raise RuntimeError('CRS mismatch between vector file and rasters')

def run():
    """Entry point for console_scripts"""
    main(sys.argv[1:])


if __name__ == "__main__":
        
    run()