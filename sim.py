import os
import config
import logging

class Sim:
  def __init__(self, path, load=False, load_all=False):
    self.username = path.split('/')[2]
    self.path = path
    self.name = path.split('/')[5][:-4]
    self.port = 0
    self.has_bin_folder = False
    self.pid_file = ''
    self.has_opensim_exe = False
    self.has_opensim_log = False
    self.has_opensim_ini = False
    self.has_regions_ini = False
    self.has_tmux_log = False
    self.radmin_ready = False
    self.radmin_password = ''
    self.valid = False
    self.regions = []
    self.alive = False
    if load or load_all:
      self.load()
      if load_all:
        if self.has_regions_ini:
          self.load_regions(load, load_all)

  # get sim infos
  def load(self):
    logging.main_logger.debug("[sim] 'load' called")

    # return if not a directory
    if not os.path.isdir(self.path):
      logging.main_logger.warning("[sim] sim %s not found" % (self.path))
      return False

    # check if there is a bin folder
    if os.path.isdir(self.path + '/bin'):
      self.has_bin_folder = True

    # check if there is an OpenSim.ini file
    if os.path.isfile(self.path + '/bin/OpenSim.exe'):
      self.has_opensim_exe = True

    # check if there is an OpenSim.ini file
    if os.path.isfile(self.path + '/bin/OpenSim.ini'):
      self.has_opensim_ini = True

    # check if there is an OpenSim.log file
    if os.path.isfile(self.path + '/log/OpenSim.log'):
      self.has_opensim_log = True

    # check if there is an OpenSim.log file
    if os.path.isfile(self.path + '/log/tmux.log'):
      self.has_tmux_log = True

    # check if there is a Regions.ini file
    if os.path.isfile(self.path + '/bin/Regions/Regions.ini'):
      self.has_regions_ini = True

    # check if RAdmin is enabled
    if self.has_opensim_ini:
      from ConfigParser import ConfigParser
      from helpers import sanitize
      opensim_ini = ConfigParser()
      opensim_ini.read(self.path + '/bin/OpenSim.ini')
      if opensim_ini.has_section('RemoteAdmin'):
        if opensim_ini.has_option('RemoteAdmin', 'enabled'):
          if opensim_ini.get('RemoteAdmin', 'enabled').lower() == 'true':
            if opensim_ini.has_option('RemoteAdmin', 'access_password'):
              self.radmin_password = sanitize(opensim_ini.get('RemoteAdmin', 'access_password'))
              self.radmin_ready = True
      if opensim_ini.has_section('Network'):
        if opensim_ini.has_option('Network', 'http_listener_port'):
          self.port = sanitize(opensim_ini.get('Network', 'http_listener_port'))
      if opensim_ini.has_section('Startup'):
        if opensim_ini.has_option('Startup', 'PIDFile'):
          self.pid_file = sanitize(opensim_ini.get('Startup', 'PIDFile')[1:-1])

    self.valid = self.has_bin_folder and self.pid_file != "" and self.has_opensim_exe and self.has_opensim_log and self.has_opensim_ini and self.has_regions_ini and self.has_tmux_log and self.radmin_ready
    return True

  # check radmin path
  def radmin_password_checked(self, password):
    logging.main_logger.debug("[sim] 'radmin_password_checked' called")

    if not self.has_opensim_ini:
      return False

    import ConfigParser
    opensim_ini = ConfigParser.ConfigParser()
    opensim_ini.read(self.path + '/bin/OpenSim.ini')

    if not opensim_ini.has_section('RemoteAdmin'):
      return False

    if not opensim_ini.has_option('RemoteAdmin', 'enabled'):
      return False

    if not opensim_ini.get('RemoteAdmin', 'enabled').lower() == 'true':
      return False

    if not opensim_ini.has_option('RemoteAdmin', 'access_password'):
      return False

    if opensim_ini.get('RemoteAdmin', 'access_password').lower() == password:
      return True

  # show log
  def show_log(self, log_type='os'):
    logging.main_logger.debug("[sim] 'show_log' called")

    #define path
    if (log_type == 'tx'):
      log_path = self.path + '/log/tmux.log'
    else:
      log_path = self.path + '/log/OpenSim.log'

    if not os.path.isfile(log_path):
      logging.main_logger.warning("[sim] log file not found from sim %s" % (self.path))
      return False

    import helpers
    return ''.join(helpers.tail(log_path, 10))

  # start sim
  def run(self, action):
    logging.main_logger.debug("[sim] 'run' called")

    # check for the right action
    if not action in ['start', 'stop', 'kill']:
      logging.main_logger.warning("[sim] wrong action called for run sim")
      return "Wrong action"

    # run the sub process
    import subprocessor
    sub = subprocessor.main([
      self.username,
      os.path.dirname(os.path.realpath(__file__)),
      "python",
      "run_sim.py",
      action,
      self.path
    ])
    return "Action " + action + " done"

  # sim if alive
  def is_alive(self):
    logging.main_logger.debug("[sim] 'is_alive' called")

    self.alive = False
    # check if there is a pid file
    check_pid = False
    if self.pid_file != '':
      check_pid = os.path.isfile(self.pid_file)

    # check if the sim is responding to simstatus
    check_simstatus = False
    from helpers import request
    req = request('http://127.0.0.1:' + str(self.port) + '/simstatus')
    if req:
      # check if status is 200
      if req.getcode() == 200:
        if req.read() == 'OK':
          check_simstatus = True

    if check_pid and check_simstatus:
      self.alive = True
      logging.main_logger.debug("[sim] sim %s is alive" % (self.path))
      return True
    else:
      logging.main_logger.debug("[sim] sim %s is not alive" % (self.path))
      return False

  # get regions
  def load_regions(self, load=False, load_all=False):
    logging.main_logger.debug("[sim] 'load_regions' called")

    # check if regions.ini exists
    if not os.path.isfile(self.path + '/bin/Regions/Regions.ini'):
      logging.main_logger.warning("[sim] No Regions.ini file found : %s" % (self.path + '/bin/Regions/Regions.ini'))
      return False

    import ConfigParser
    regions_ini = ConfigParser.ConfigParser()
    regions_ini.read(self.path + '/bin/Regions/Regions.ini')
    sections = regions_ini.sections()
    if not len(sections):
      logging.main_logger.warning("[sim] No region found in Regions.ini file")
      return False

    import region
    for section in sections:
      new_region = region.Region(self.path, section, load, load_all)
      self.regions.append(new_region)

    return True

  # send command
  def send_command(self, command):
    logging.main_logger.info("[sim] 'send_command' called")

    import subprocessor
    sub = subprocessor.main([
      self.username,
      os.path.dirname(os.path.realpath(__file__)),
      "python",
      "send_command.py",
      self.path,
      command
    ])
