import os
import config
import logging
import archive

class Oar:
  def __init__(self, username, name):
    self.name = name
    self.username = username
    self.path = '/home/' + username + '/opensimulator/oar/' + self.name + '.oar'
    self.url = ''

  # get infos
  def load(self):
    logging.main_logger.debug("[oar] 'load' called")

    # build path and url
    self.path = '/home/' + self.username + '/opensimulator/oar/' + self.name + '.oar'
    self.url = archive.create_archive_url(self.path)

    # check if file exists
    if not os.path.isfile(self.path):
      logging.main_logger.warning("[oar] oar not found : %s" % (self.path))
      return False

    # no error
    return True

  # delete oar
  def delete(self):
    logging.main_logger.debug("[oar] 'delete' called")

    # check if file exists
    if os.path.isfile(self.path):
      os.remove(self.path)
      self.load()
      logging.main_logger.debug("[oar] oar deleted")
      return True
    logging.main_logger.warning("[oar] oar not found : %s" % (self.path))
    return False

  # load oar
  '''
  load oar [--merge] [--skip-assets] [<OAR path>]
  params are in a dict as :
  merge = False
  skip_assets = False
  diplacement = ""
  force_terrain = False
  force_parcels = False
  rotation = ""
  rotation_center = ""
  no_objects = False
  '''
  def os_load_oar(self, sim_path, params={}):
    logging.main_logger.debug("[oar] 'os_load_oar' called")

    # check if the file exists
    if not os.path.isfile(self.path):
      logging.main_logger.warning("[oar] oar not found : %s" % (self.path))
      return False

    # check if the sim exists
    if not os.path.isdir(sim_path):
      logging.main_logger.warning("[oar] no sim path : %s" % (sim_path))
      return False

    command = 'load oar'

    # add params
    if 'merge' in params and params['merge']:
      command += " --merge"
    if 'skip_assets' in params and params['skip_assets']:
      command += " --skip-assets"
    if 'diplacement' in params and params['diplacement']:
      command += " --diplacement"
    if 'force_terrain' in params and params['force_terrain']:
      command += " --force-terrain"
    if 'force_parcels' in params and params['force_parcels']:
      command += " --force-parcels"
    if 'rotation' in params and params['rotation']:
      command += " --rotation"
    if 'rotation_center' in params and params['rotation_center']:
      command += " --rotation-center"
    if 'no_objects' in params and params['no_objects']:
      command += " --no-objects"

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
    return True

  # save oar
  '''
  save oar [-h|--home=<url>] [--noassets] [--publish] [--perm=<permissions>] [--all] [<OAR path>]
  params are in a dict as :
  home = ''
  noassets = False
  publish = False
  perm = ''
  all_regions = False
  '''
  def os_save_oar(self, sim_path, params={}):
    logging.main_logger.debug("[oar] 'os_save_oar' called")

    # check the name
    if self.name == '':
      logging.main_logger.warning("[oar] no oar name defined")
      return False

    # check the sim path
    if not os.path.isdir(sim_path):
      logging.main_logger.warning("[oar] no sim path")
      return False

    # check if the folder is writable
    if not os.access('/home/' + self.username + '/opensimulator/oar/', os.W_OK):
      logging.main_logger.warning("[oar] folder not writable : %s" % ('/home/' + self.username + '/opensimulator/oar/'))
      return False

    command = 'save oar'

    # add the params
    if 'noassets' in params and params['noassets']:
      command += ' --noassets'
    if 'publish' in params and params['publish']:
      command += ' --publish'
    if 'perm' in params and params['perm'] != '':
      command += ' --perm=' + params['perm']
    if 'all_regions' in params and params['all_regions']:
      command += ' --all'
      self.name = os.path.basename(sim_path)[:-4]

    from time import strftime
    self.name += '-' + strftime("%y%m%d-%H%M")
    self.path = '/home/' + self.username + '/opensimulator/oar/' + self.name + '.oar'

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
