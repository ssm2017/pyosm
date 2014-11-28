import os
import config
import logging
import archive

class Iar:
  def __init__(self, username, name):
    self.name = name
    self.username = username
    self.path = '/home/' + self.username + '/opensimulator/iar/' + self.name + '.iar'
    self.url = ''

  # get infos
  def load(self):
    logging.main_logger.debug("[iar] 'load' called")

    # build path and url
    self.path = '/home/' + self.username + '/opensimulator/iar/' + self.name + '.iar'
    self.url = archive.create_archive_url(self.path)

    # check if file exists
    if not os.path.isfile(self.path):
      logging.main_logger.warning("[iar] iar not found : %s" % (self.path))
      return False

    # no error
    return True

  # delete oar
  def delete(self):
    logging.main_logger.debug("[iar] 'delete' called")

    # check if file exists
    if os.path.isfile(self.path):
      os.remove(self.path)
      self.load()
      logging.main_logger.debug("[iar] iar deleted")
      return True
    logging.main_logger.warning("[iar] iar not found : %s" % (self.path))
    return False

  # load iar
  '''
  load iar [-m|--merge] <first> <last> <inventory path> <password> [<IAR path>]
  params are in a dict as :
  merge = False
  first = ''
  last = ''
  inventory_path = '/'
  password = ''
  '''
  def os_load_iar(self, sim_path, params=[]):
    logging.main_logger.debug("[iar] 'os_load_iar' called")

    # check if the file exists
    if not os.path.isfile(self.path):
      logging.main_logger.warning("[iar] iar not found : %s" % (self.path))
      return False

    # check if the sim exists
    if not os.path.isdir(sim_path):
      logging.main_logger.warning("[iar] no sim path : %s" % (sim_path))
      return False

    command = 'load iar'

    # add params
    if 'merge' in params and params['merge']:
      command += ' --merge'

    if 'first' in params and params['first'] != '':
      command += ' ' + params['first']
    else:
      logging.main_logger.warning("[iar] no firstname defined")
      return False

    if 'last' in params and params['last'] != '':
      command += ' ' + params['last']
    else:
      logging.main_logger.warning("[iar] no lastname defined")
      return False

    if 'inventory_path' in params and params['inventory_path'] != '':
      command += ' ' + params['inventory_path']
    else:
      command += ' /'

    if 'password' in params and params['password'] != '':
      command += ' ' + params['password']
    else:
      logging.main_logger.warning("[iar] no password defined")
      return False

    command += ' ' + self.path

    # send command to the console
    import subprocessor
    sub = subprocessor.main([
      self.username,
      os.path.dirname(os.path.realpath(__file__)),
      "python",
      "send_command.py",
      sim_path,
      command
    ])
    return True

  # save iar
  '''
  save iar [-h|--home=<url>] [--noassets] <first> <last> <inventory path> <password> [<IAR path>] [-c|--creators] [-e|--exclude=<name/uuid>] [-f|--excludefolder=<foldername/uuid>] [-v|--verbose]
  params are in a dict as :
  home = ''
  noassets = False
  first = ''
  last = ''
  inventory_path = '/'
  password = ''
  creators = True
  exclude = ''
  excludefolder = ''
  verbose = False
  '''
  def os_save_iar(self, sim_path, params={}):
    logging.main_logger.debug("[iar] 'os_save_iar' called")

    # check the sim path
    if not os.path.isdir(sim_path):
      logging.main_logger.warning("[iar] no sim path")
      return False

    # check if the folder is writable
    iar_folder = '/home/' + self.username + '/opensimulator/iar'
    if not os.access(iar_folder, os.W_OK):
      logging.main_logger.warning("[iar] folder not writable : %s" % (iar_folder))
      return False

    command = 'save iar'

    # add the params
    if 'home' in params and params['home'] != '':
      command += ' --home=' + params['home']

    if 'noassets' in params and params['noassets']:
      command += ' --noassets'

    if 'first' in params and params['first'] != '':
      command += ' ' + params['first']
    else:
      logging.main_logger.warning("[iar] no firstname defined")
      return False

    if 'last' in params and params['last'] != '':
      command += ' ' + params['last']
    else:
      logging.main_logger.warning("[iar] no lastname defined")
      return False

    if 'inventory_path' in params and params['inventory_path'] != '':
      command += ' ' + params['inventory_path']
    else:
      command += ' /'

    if 'password' in params and params['password'] != '':
      command += ' ' + params['password']
    else:
      logging.main_logger.warning("[iar] no password defined")
      return False

    if 'creators' in params and params['creators']:
      command += ' --creators'

    if 'exclude' in params and params['exclude'] != '':
      command += ' --exclude=' + params['exclude']

    if 'excludefolder' in params and params['excludefolder'] != '':
      command += ' --excludefolder=' + params['excludefolder']

    from time import strftime
    self.name = params['first'] + '.' + params['last'] + '-' + strftime("%y%m%d-%H%M")
    self.path = iar_folder + '/' + self.name + '.iar'

    command += ' ' + self.path

    # send the command to the console
    import subprocessor
    sub = subprocessor.main([
      self.username,
      os.path.dirname(os.path.realpath(__file__)),
      "python",
      "send_command.py",
      sim_path,
      command
    ])
    self.load()
    return True
