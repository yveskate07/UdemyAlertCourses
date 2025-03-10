import logging
import os
from mail_sender import read_log_file

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

    # if we have some errors, they are written in a .txt file and in the case only we send a mail to the owner of the app
    elif level == "error":
        logging.info(msg)
        with open(os.path.join("txt","logs.txt"), "a") as file:
            file.write(read_log_file())

    else:
        logging.info(msg)
        with open(os.path.join("txt","logs.txt"), "a") as file:
            file.write(read_log_file())
