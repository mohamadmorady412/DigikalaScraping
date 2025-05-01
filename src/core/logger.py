#Copyright (C) 2025 MohammadjavadMorady

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

"""
This module configures and initializes the application's logger
using the loguru library. It sets up logging to a file and to the
standard error stream.
"""
from loguru import logger
import sys

def setup_logger():
    """
    Configures the global logger.

    Removes any default handlers, adds a file handler to 'logs/scraper.log'
    with a rotation size of 10 MB and INFO level, and adds a handler
    to sys.stderr with INFO level. Finally, it logs an initialization message.
    """
    logger.remove()
    logger.add("logs/scraper.log", rotation="10 MB", level="INFO")
    logger.add(sys.stderr, level="INFO")
    logger.info("Logger initialized")