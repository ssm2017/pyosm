import os
import logging
import logging.handlers

# manage logging
logging.main_logger = logging.getLogger("main_log")
logging.main_logger.setLevel(logging.DEBUG)

# set the logging file path
if os.geteuid() == 0:
  logpath = "/var/log/pyosm.log"
else:
  logpath = os.path.expanduser("~") + '/opensimulator/pyosm/pyosm.log'

# build formatters
complete_formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(funcName)s (%(lineno)d) - %(levelname)s : %(message)s')
simple_formatter = logging.Formatter('%(levelname)s : %(message)s')

# build the file logger
filehandler = logging.handlers.TimedRotatingFileHandler(logpath, when='midnight', interval=1, backupCount=7, encoding=None, delay=False, utc=False)
filehandler.setLevel(logging.DEBUG)
filehandler.setFormatter(complete_formatter)
logging.main_logger.addHandler(filehandler)

# set the logger for the console
consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.ERROR)
consolehandler.setFormatter(simple_formatter)
logging.main_logger.addHandler(consolehandler)
