import logging
import os


main_script_path = os.path.dirname(os.path.abspath(__file__))  # directory of this script

logging.basicConfig(level=logging.DEBUG,
                    filename=os.path.join(main_script_path, "logs", "logs.log"),
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s') # configuring the level of the logs to be displayed

def log_writer(msg, level='info'): # writing logs with msg depending on the level
    if level == "debug":
        logging.debug(msg)

    elif level == "info":
        logging.info(msg)

    elif level == "warning":
        logging.info(msg)

    elif level == "error":
        logging.info(msg)

    else:
        logging.info(msg)