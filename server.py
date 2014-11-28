import os
import sys
import log
import logging
import archive
import methods
import config
config.basepath = os.path.dirname(os.path.realpath(__file__))

if not os.geteuid() == 0:
  sys.exit('Script must be run as root')

#load the config
if not config.load():
  sys.exit(config.message)

if __name__ == '__main__':
  # define the server
  from SimpleXMLRPCServer import SimpleXMLRPCServer
  from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

  # Restrict to a particular path.
  class RequestHandler(SimpleXMLRPCRequestHandler):
      rpc_paths = (config.paths)

      def do_GET(self):
        filepath = archive.parse_archive_url(self.path)
        if type(filepath) is bool:
          self.send_response(404)
          return False
        if not os.path.isfile(filepath):
          self.send_response(404)
          return False
        self.send_response(200)
        self.send_header('Content-type','archive/tar')
        self.end_headers()
        f = open(filepath)
        self.wfile.write(f.read())
        f.close()
        return

  # Create server
  server = SimpleXMLRPCServer((config.host_name, config.port), requestHandler=RequestHandler)
  server.register_introspection_functions()

  # declare methods
  server.register_function(methods.ping)
  server.register_function(methods.get_sim_users)
  server.register_function(methods.get_sim_user)
  server.register_function(methods.get_sims_by_user)
  server.register_function(methods.get_sim)
  server.register_function(methods.show_log)
  server.register_function(methods.run_sim)
  server.register_function(methods.os_save_oar)
  server.register_function(methods.os_load_oar)
  server.register_function(methods.delete_oar)
  server.register_function(methods.os_save_iar)
  server.register_function(methods.os_load_iar)
  server.register_function(methods.delete_iar)

  # Run the server's main loop
  logging.main_logger.critical("[server] Pyosmw server starting on host %s and port %s." % (config.host_name,config.port))
  try:
    server.serve_forever()
  except KeyboardInterrupt:
    logging.main_logger.critical("[server] Pyosmw server interrupted.")
    server.server_close()
    sys.exit(0)
