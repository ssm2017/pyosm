import os
import time
import hashlib
import config
import urllib
import logging

def create_archive_url(filepath):
  logging.main_logger.debug("[archive] 'create_archive_url' called")
  # check if path exist
  if not os.path.isfile(filepath):
    logging.main_logger.warning("[archive] file not found : %s" % (filepath))
    return False

  # parse the path
  splitted = filepath.split('/')
  if splitted[1] != "home" or splitted[3] != "opensimulator" or (splitted[4] != 'iar' and splitted[4] != 'oar'):
    logging.main_logger.warning("[archive] wrong file path : %s" % (filepath))
    return False

  username = splitted[2]
  archive_type = splitted[4]
  expiration = int(time.time()+300)
  m = hashlib.md5()
  m.update(str(expiration) + ':' + config.server_password)
  url = '/archive/' + archive_type + '/' + username + '/' + m.hexdigest() + '/' + str(expiration) + '/' + urllib.quote_plus(splitted[5])
  return url

def parse_archive_url(url):
  logging.main_logger.debug("[archive] 'parse_archive_url' called")
  splitted = url.split('/')
  if splitted[1] != 'archive' or (splitted[2] != 'oar' and splitted[2] != 'iar'):
    logging.main_logger.warning("[archive] wrong url : %s" % (url))
    return False

  filename = urllib.unquote(splitted[6])
  username = splitted[3]

  # check expiration
  expiration = int(splitted[5])
  now = int(time.time())
  if now > expiration:
    logging.main_logger.warning("[archive] url expired : %s" % (url))
    return False

  # check password
  m = hashlib.md5()
  m.update(str(expiration) + ':' + config.server_password)
  if splitted[4] != m.hexdigest():
    logging.main_logger.warning("[archive] wrong password")
    return False

  filepath = '/home/' + username + '/opensimulator/' + splitted[2] + '/' + filename
  return filepath
