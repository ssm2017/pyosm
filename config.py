import os
import sys
import logging

host_name = 'localhost'
port = 8008
paths = '/rpc, /backup'
server_password = 'abcd'
url_duration = 300

def load():
  global host_name, port, paths, server_password, url_duration
  logging.main_logger.info("[config] Pyosmw config read started.")

  # check if config exists
  if os.path.isfile("/etc/pyosm/pyosm.ini") != True:
    logging.main_logger.error("[config] Config_file file not found")
    return False

  # read the config file
  from ConfigParser import ConfigParser
  Config_file = ConfigParser()
  Config_file.read("/etc/pyosm/pyosm.ini")

  # get the server infos
  if not Config_file.has_section('Server'):
    logging.main_logger.error("[config] No Server section defined in config file")
    return False

  # hostname
  if not Config_file.has_option('Server', 'HostName'):
    logging.main_logger.error("[config] No HostName option defined in config file")
    return False

  host_name = Config_file.get('Server', 'HostName')

  # port
  if not Config_file.has_option('Server', 'Port'):
    logging.main_logger.error("[config] No Port option defined in config file")
    return False

  port = int(Config_file.get('Server', 'Port'))

  # password
  if not Config_file.has_option('Server', 'Password'):
    logging.main_logger.error("[config] No Password option defined in config file")
    return False

  server_password = Config_file.get('Server', 'Password')

  # url_duration
  if not Config_file.has_option('Server', 'UrlDuration'):
    logging.main_logger.error("[config] No UrlDuration option defined in config file")
    return False

  url_duration = Config_file.get('Server', 'UrlDuration')

  logging.main_logger.info("[config] Pyosmw config read succeeded.")
  return True
