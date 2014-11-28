import os
import config
import logging

# get sim users
def get_sim_users(load=False, load_all=False):
  logging.main_logger.debug("[user] 'get_sim_users' called")

  # get system users
  import user
  sim_users = []
  system_users = get_system_users()
  for username in system_users:
    sim_user = user.User(username, load, load_all)
    if len(sim_user.sims):
      sim_users.append(sim_user)
  return sim_users

def get_sim_user(username, load=False, load_all=False):
  logging.main_logger.debug("[user] 'get_sim_user' called")

  # get system users
  import user
  sim_user = user.User(username, load, load_all)
  return sim_user

def get_system_users():
  logging.main_logger.debug("[user] 'get_system_users' called")

  stdin,stdout = os.popen2("cut -d: -f1,3 /etc/passwd | egrep ':[0-9]{4}$' | cut -d: -f1")
  stdin.close()
  lines = stdout.readlines();
  stdout.close()
  # remove the \n
  lines = map(lambda s: s.strip(), lines)
  return lines

class User:
  def __init__(self, name, load=False, load_all=False):
    self.name = name
    self.sims = []
    self.has_iar_folder = os.path.isdir('/home/' + self.name + '/opensimulator/iar/')
    self.iars = []
    self.has_oar_folder = os.path.isdir('/home/' + self.name + '/opensimulator/oar/')
    self.oars = []
    if load_all:
      self.load_sims(load, load_all)
      if self.has_oar_folder:
        self.load_oars()
      if self.has_iar_folder:
        self.load_iars()

  # get iars
  def load_iars(self):
    logging.main_logger.debug("[user] 'load_iars' called")

    if not os.path.isdir('/home/' + self.name + '/opensimulator/iar/'):
      self.has_iar_folder = False
      logging.main_logger.warning("[user] no iar folder found : %s" % ('/home/' + self.name + '/opensimulator/iar/'))
      return False

    import iar
    for entry in os.listdir('/home/' + self.name + '/opensimulator/iar/'):
      if entry.endswith('.iar'):
        iar_file = iar.Iar(self.name, entry[:-4])
        if iar_file.load():
          self.iars.append(iar_file)

    if not len(self.iars):
      logging.main_logger.warning("[user] no iar file found : %s" % ('/home/' + self.name + '/opensimulator/iar/'))
      return False

    return True

  # get oars
  def load_oars(self):
    logging.main_logger.debug("[user] 'load_oars' called")

    if not os.path.isdir('/home/' + self.name + '/opensimulator/oar/'):
      self.has_oar_folder = False
      logging.main_logger.warning("[user] no oar folder found for user %s" % (self.name))
      return False

    import oar
    for entry in os.listdir('/home/' + self.name + '/opensimulator/oar/'):
      if entry.endswith('.oar'):
        oar_file = oar.Oar(self.name, entry[:-4])
        if oar_file.load():
          self.oars.append(oar_file)

    if not len(self.oars):
      logging.main_logger.warning("[user] no oar files found for user %s" % (self.name))
      return False

    return True

  # get sims by user
  def load_sims(self, load=False, load_all=False):
    logging.main_logger.debug("[user] 'load_sims' called")

    user_sims = []
    # get the user folder
    user_os_folder_path = "/home/" + self.name + "/opensimulator/sims"
    if not os.path.isdir(user_os_folder_path):
      logging.main_logger.warning("[user] no simulator folder found for user : %s" % (self.name))
      return False

    # get the simulators folders
    for entry in os.listdir(user_os_folder_path):
      if entry.endswith('.sim'):
        sim_path = user_os_folder_path + '/' + entry
        if os.path.isdir(sim_path):
          import sim
          mysim = sim.Sim(sim_path, load, load_all)
          if not mysim is None:
            mysim.is_alive()
            user_sims.append(mysim)

    if not user_sims:
      logging.main_logger.warning("[user] no sim folder found for user : %s" % (self.name))
      return False

    self.sims = user_sims
    return True
