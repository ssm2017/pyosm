import os
import sys
import tmuxp
import log
import logging
import sim

import config
config.basepath = os.path.dirname(os.path.realpath(__file__))

#load the config
if not config.load():
  sys.exit(config.message)

def start_sim(sim):
  logging.main_logger.debug("[run_sim] 'start_sim' called")

  # check if simulator is running
  if sim.is_alive():
    logging.main_logger.debug("[run_sim] Sim is running")
    return False

  is_new = False

  # tmux sever
  tmux_server = tmuxp.Server()

  # check if there is already a session
  if not tmux_server.has_session(sim.name):
    logging.main_logger.warning("[run_sim] No session found for %s", sim.name)
    # create a tmux session if not exist
    session = tmux_server.new_session(session_name=sim.name)
    window = session.new_window(window_name='OpenSimulator')
    logging.main_logger.debug("[run_sim] Session and window created for %s", sim.name)
    is_new = True
  else:
    session = tmux_server.findWhere({"session_name": sim.name})
    window = session.findWhere({'window_name':'OpenSimulator'})
    if not window:
      logging.main_logger.warning("[run_sim] No window found for %s", sim.name)
      window = session.new_window(window_name='OpenSimulator', attach=False)
      logging.main_logger.debug("[run_sim] Window created for %s", sim.name)
      is_new = True

  session.select_window('OpenSimulator')
  pane = window.select_pane(0)
  pane.send_keys('cd ' + sim.path + '/bin', enter=False)
  pane.enter()
  if is_new:
    pane.send_keys("tmux pipe-pane -o -t " + sim.name + ":OpenSimulator 'cat >> " + sim.path + "/log/tmux.log'", enter=False)
    pane.enter()
  pane.send_keys('mono --server OpenSim.exe', enter=False)
  pane.enter()

  logging.main_logger.debug("[run_sim] OpenSimulator runned from %s", sim.name)
  return True

def stop_sim(sim):
  logging.main_logger.debug("[run_sim] 'stop_sim' called")

  # check if simulator is running
  if not sim.is_alive():
    logging.main_logger.warning("[run_sim] Sim %s is not running", sim.name)
    return False

  # tmux sever
  tmux_server = tmuxp.Server()

  # check if there is already a session
  if not tmux_server.has_session(sim.name):
    logging.main_logger.warning("[run_sim] No session found for %s", sim.name)
    return False
  else:
    session = tmux_server.findWhere({"session_name": sim.name})
    window = session.findWhere({'window_name':'OpenSimulator'})
    if not window:
      logging.main_logger.warning("[run_sim] No window found for %s", sim.name)
      return False

  session.select_window('OpenSimulator')
  pane = window.select_pane(0)
  pane.enter()
  pane.send_keys("quit", True)

  logging.main_logger.debug("[run_sim] OpenSimulator quitted from %s", sim.name)
  return True

def kill_sim(sim):
  logging.main_logger.debug("[run_sim] 'kill_sim' called")

  # tmux sever
  tmux_server = tmuxp.Server()

  # check if there is already a session
  if tmux_server.has_session(sim.name):
    tmux_server.kill_session(target_session=sim.name)

  logging.main_logger.debug("[run_sim] OpenSimulator killed from %s", sim.name)
  return True

if __name__ == '__main__':
  args = sys.argv[1:]
  logging.main_logger.debug("[run_sim] run_sim called with args %s", args)

  # get the sim
  mysim = sim.Sim(args[1], load=True)
  if not (mysim.valid):
    msg = "[run_sim] Simulator is not valid"
    logging.main_logger.warning(msg)
    sys.exit(msg)

  logging.main_logger.debug("[run_sim] User is : %s", os.getuid())
  logging.main_logger.debug("[run_sim] username is : %s", mysim.username)
  logging.main_logger.debug("[run_sim] sim_name is : %s", mysim.name)

  if (args[0] == 'start'):
    start_sim(mysim)
  elif (args[0] == 'stop'):
    stop_sim(mysim)
  elif (args[0] == 'kill'):
    kill_sim(mysim)
