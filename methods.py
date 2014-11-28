import os
import sys
import json
import logging
import user
import sim
import region
import iar
import oar
import helpers
import archive
import config

# check password
wrong_password = {"accepted":False, "success":False, "error":"wrong password"}
def check_password(password_given):
  if password_given == config.server_password:
    return True
  return False

# answer to ping
def ping():
  logging.main_logger.debug("[xml-rpc] Method 'ping' called.")
  return "pong"

# get system users
def get_sim_users(password):
  logging.main_logger.debug("[xml-rpc] Method 'get_sim_users' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  return {"success":True, "sim_users":user.get_sim_users(load_all=True)}

# get system user
def get_sim_user(password, username):
  logging.main_logger.debug("[xml-rpc] Method 'get_sim_user' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  return {"success":True, "sim_user":user.get_sim_user(username=username, load_all=True)}

# get sims by user
def get_sims_by_user(password, username):
  logging.main_logger.debug("[xml-rpc] Method 'get_sims_by_user' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  new_user = user.User(username)
  if new_user.load_sims(load_all=True):
    return {"success":True, "sims":new_user.sims}
  return {"success":False, "message":'No sim found'}

# get_sim_infos
def get_sim(password, sim_path):
  logging.main_logger.debug("[xml-rpc] Method 'get_sim' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  if not os.path.isdir(sim_path):
    return {"success":False, "message":'Sim not found'}
  mysim = sim.Sim(sim_path, load_all=True)
  if mysim.load():
    mysim.is_alive()
    return {"success":True, "sim":mysim}
  return {"success":False, "message":'Sim not found'}

# show log
def show_log(password, sim_path, log_type):
  logging.main_logger.debug("[xml-rpc] Method 'show_log' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  import base64
  mysim = sim.Sim(sim_path)
  return {"success":True, "log":base64.b64encode(mysim.show_log(log_type))}

# run sim
def run_sim(password, sim_path, action):
  logging.main_logger.debug("[xml-rpc] Method 'run_sim' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  mysim = sim.Sim(sim_path)
  if mysim.load():
    return {"success":True, "run_sim":mysim.run(action)}
  return {"success":False, "message":'Sim not found'}

# save oar
def os_save_oar(password, sim_path, region_name, params={}):
  logging.main_logger.debug("[xml-rpc] Method 'os_save_oar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myregion = region.Region(sim_path, region_name)
  if myregion.os_save_oar(params):
    return {"success":True}
  return {"success":False, "message":'Error saving oar'}

# load oar
def os_load_oar(password, sim_path, region_name, oar_path, params={}):
  logging.main_logger.debug("[xml-rpc] Method 'os_load_oar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myregion = region.Region(sim_path, region_name)
  if myregion.os_load_oar(oar_path.split('/')[5][:-4], params):
    return {"success":True}
  return {"success":False, "message":'Error loading oar'}

# delete oar
def delete_oar(password, oar_path):
  logging.main_logger.debug("[xml-rpc] Method 'delete_oar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myoar = oar.Oar(oar_path.split('/')[2], oar_path.split('/')[5][:-4])
  if myoar.delete():
    return {"success":True}
  return {"success":False, "message":'Error deleting oar'}

# save iar
def os_save_iar(password, sim_path, params={}):
  logging.main_logger.debug("[xml-rpc] Method 'os_save_iar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myiar = iar.Iar(sim_path.split('/')[2], '')
  if myiar.os_save_iar(sim_path, params):
    return {"success":True}
  return {"success":False, "message":'Error saving iar'}

# load iar
def os_load_iar(password, sim_path, iar_path, params={}):
  logging.main_logger.debug("[xml-rpc] Method 'os_load_iar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myiar = iar.Iar(sim_path.split('/')[2], iar_path.split('/')[5][:-4])
  if myiar.load():
    if myiar.os_load_iar(sim_path, params):
      return {"success":True}
  return {"success":False, "message":'Error loading iar'}

# delete iar
def delete_iar(password, iar_path):
  logging.main_logger.debug("[xml-rpc] Method 'delete_iar' called.")

  # check password
  if not check_password(password):
    return wrong_password

  # compute the answer
  myiar = iar.Iar(iar_path.split('/')[2], iar_path.split('/')[5][:-4])
  if myiar.load():
    if myiar.delete():
      return {"success":True}
  return {"success":False, "message":'Error deleting iar'}
