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

def send_command(sim, command):
  logging.main_logger.debug("[send_command] 'send_command' called")

  # check if simulator is running
  if not sim.is_alive():
    logging.main_logger.warning("[send_command] sim is not alive")
    return False

  # tmux sever
  tmux_server = tmuxp.Server()

  # check if there is already a session
  if not tmux_server.has_session(sim.name):
    logging.main_logger.warning("[send_command] No session found for %s", sim.name)
    return False
  else:
    session = tmux_server.findWhere({"session_name": sim.name})
    window = session.findWhere({'window_name':'OpenSimulator'})
    if not window:
      logging.main_logger.warning("[send_command] No window found for %s", sim.name)
      return False

  session.select_window('OpenSimulator')
  pane = window.select_pane(0)
  pane.enter()
  pane.send_keys(' '.join(command), True)

  logging.main_logger.debug("[send_command] Command sent to %s", sim.name)
  return True

if __name__ == '__main__':
  args = sys.argv[1:]
  logging.main_logger.debug("[send_command] send command with args %s", args)

  # get the sim
  mysim = sim.Sim(args[0], True)
  if not (mysim.valid):
    msg = "[send_command] Simulator is not valid"
    logging.main_logger.error(msg)
    sys.exit(msg)

  logging.main_logger.debug("[send_command] User is : %s", os.getuid())
  logging.main_logger.debug("[send_command] username is : %s", mysim.username)
  logging.main_logger.debug("[send_command] sim_name is : %s", mysim.name)
  logging.main_logger.debug("[send_command] Command is : %s", args[2:])

  send_command(mysim, args[1:])
