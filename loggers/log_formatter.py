import logging
import os
from datetime import datetime
import getpass


def create_logger(name: str, output_path: str) -> object:
    """function to create a root logger object
    Parameters
    __________
    name : str
        name of the program being run this is the __name__ value of the initial
        program

    log_filename : str
        name of the log file that will be created

    Returns
    _______
    object
        returns a logger object that the program will log information to
    """
    current_day: str = datetime.now().strftime("%m_%d_%Y")

    log_filename: str = os.path.join(output_path, "".join([current_day, "_log.log"]))
    # check if file exists and if it does then deleting the file from the previous run
    if os.path.exists(log_filename):
        os.remove(log_filename)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logger = logging.getLogger(name)

    # setting the logging level to the lowest level
    logger.setLevel("DEBUG")

    # Use FileHandler() to log to a file
    file_handler = logging.FileHandler(log_filename)
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)

    # Don't forget to add the file handler
    logger.addHandler(file_handler)
    logger.info("created log file for the DRIVE analysis")
    logger.info("initializing run...")
    logger.info(f"run started by {getpass.getuser()}")

    return logger
