import os
import config
import logging

class Region:
  def __init__(self, sim_path, name, load=False, load_all=False):
    self.name = name
    self.sim_path = sim_path
    self.username = sim_path.split('/')[2]
    self.region_uuid = ""
    self.location = ""
    self.sizex = 256
    self.sizey = 256
    self.internal_address = ""
    self.internal_port = ""
    self.allow_alternate_ports = ""
    self.external_host_name = ""
    self.nonphysical_prim_max = ""
    self.physical_prim_max = ""
    self.clamp_primSize = False
    self.max_prims = ""
    self.max_agents = ""
    self.scope_id = ""
    self.region_type = ""
    self.maptile_static_uuid = ""
    self.alive = False
    if load or load_all:
      self.load()
      if load_all:
        self.is_alive()

  def load(self):
    logging.main_logger.debug("[region] 'load' called")

    # get the regions.ini file
    ini_path = self.sim_path + '/bin/Regions/Regions.ini'
    if not os.path.isfile(ini_path):
      logging.main_logger.warning("[region] no Regions.ini file found : %s" % (ini_path))
      return False

    # check the region name
    if self.name == '':
      logging.main_logger.warning("[region] no name defined")
      return False

    from ConfigParser import ConfigParser
    from helpers import sanitize
    regions_ini = ConfigParser()
    regions_ini.read(ini_path)
    sections = regions_ini.sections()

    # check the region in Regions.ini
    if not self.name in sections:
      logging.main_logger.warning("[region] region not found in Regions.ini file")
      return False

    if regions_ini.has_option(self.name, 'RegionUUID'):
      self.region_uuid = sanitize(regions_ini.get(self.name, 'RegionUUID'))

    if regions_ini.has_option(self.name, 'Location'):
      self.location = sanitize(regions_ini.get(self.name, 'Location'))

    if regions_ini.has_option(self.name, 'SizeX'):
      self.sizex = sanitize(regions_ini.get(self.name, 'SizeX'))

    if regions_ini.has_option(self.name, 'SizeY'):
      self.sizey = sanitize(regions_ini.get(self.name, 'SizeY'))

    if regions_ini.has_option(self.name, 'InternalAddress'):
      self.internal_address = sanitize(regions_ini.get(self.name, 'InternalAddress'))

    if regions_ini.has_option(self.name, 'InternalPort'):
      self.internal_port = sanitize(regions_ini.get(self.name, 'InternalPort'))

    if regions_ini.has_option(self.name, 'AllowAlternatePorts'):
      self.allow_alternate_ports = sanitize(regions_ini.get(self.name, 'AllowAlternatePorts'))

    if regions_ini.has_option(self.name, 'ExternalHostName'):
      self.external_host_name = sanitize(regions_ini.get(self.name, 'ExternalHostName'))

    if regions_ini.has_option(self.name, 'NonphysicalPrimMax'):
      self.nonphysical_prim_max = sanitize(regions_ini.get(self.name, 'NonphysicalPrimMax'))

    if regions_ini.has_option(self.name, 'PhysicalPrimMax'):
      self.physical_prim_max = sanitize(regions_ini.get(self.name, 'PhysicalPrimMax'))

    if regions_ini.has_option(self.name, 'MaxPrims'):
      self.max_prims = sanitize(regions_ini.get(self.name, 'MaxPrims'))

    if regions_ini.has_option(self.name, 'MaxAgents'):
      self.max_agents = sanitize(regions_ini.get(self.name, 'MaxAgents'))

    if regions_ini.has_option(self.name, 'ScopeID'):
      self.scope_id = sanitize(regions_ini.get(self.name, 'ScopeID'))

    if regions_ini.has_option(self.name, 'RegionType'):
      self.region_type = sanitize(regions_ini.get(self.name, 'RegionType'))

    if regions_ini.has_option(self.name, 'MaptileStaticUUID'):
      self.maptile_static_uuid = sanitize(regions_ini.get(self.name, 'MaptileStaticUUID'))

    return True

  def exists(self):
    logging.main_logger.debug("[region] 'exists' called")

    # get the Regions.ini file
    ini_path = self.sim_path + '/bin/Regions/Regions.ini'
    if not os.path.isfile(ini_path):
      logging.main_logger.warning("[region] no Regions.ini file found : %s" % (ini_path))
      return False

    from ConfigParser import ConfigParser
    regions_ini = ConfigParser()
    regions_ini.read(ini_path)
    sections = regions_ini.sections()

    # check the region in Regions.ini
    if not self.name in sections:
      logging.main_logger.warning("[region] region not found in Regions.ini file")
      return False

    return True

  def set_active(self, name=''):
    logging.main_logger.debug("[region] 'set_active' called")

    if name != '':
      self.name = name
    if self.load():
      import sim
      act_sim = sim.Sim(self.sim_path)
      act_sim.send_command('change region ' + self.name)
      return True
    return False

  # save oar
  ''' params are in a dict as :
  home = ''
  noassets = False
  publish = False
  perm = ''
  all_regions = False
  '''
  def os_save_oar(self, params={}):
    logging.main_logger.debug("[region] 'os_save_oar' called")

    if self.set_active(self.name):
      import oar
      new_oar = oar.Oar(self.username, self.name)
      return new_oar.os_save_oar(self.sim_path, params)
    return False

  # load oar
  ''' params are in a dict as :
  merge = False
  skip_assets = False
  '''
  def os_load_oar(self, oar_name, params={}):
    logging.main_logger.debug("[region] 'os_load_oar' called")

    import oar
    new_oar = oar.Oar(self.username, oar_name)
    if new_oar.load():
      if self.set_active(self.name):
        return new_oar.os_load_oar(self.sim_path, params)
    return False

  # is alive
  def is_alive(self):
    logging.main_logger.debug("[region] 'is_alive' called")

    import sim
    self.alive = False
    mysim = sim.Sim(self.sim_path, True)
    # check if the sim is responding to simstatus
    check_monitorstats = False
    from helpers import request
    url = 'http://127.0.0.1:' + mysim.port + '/monitorstats/' + self.region_uuid
    logging.main_logger.debug('Url called : %s' % (url))
    req = request(url)
    if req:
      # check if status is 200
      if req.getcode() == 200:
        check_monitorstats = True
        self.alive = True

    return self.alive
