import os
import logging

def tail(f, n):
  stdin,stdout = os.popen2("tail -n "+str(n)+" "+f)
  stdin.close()
  lines = stdout.readlines();
  stdout.close()
  return lines

# manage http requests
def request(url):
  from urllib2 import Request, urlopen, URLError
  req = Request(url)
  try:
    http_response = urlopen(req, timeout=5)
  except URLError as e:
    if hasattr(e, 'reason'):
      logging.main_logger.warning('[request] We failed to reach a server. Reason: %s' % (e.reason))
      return False
    elif hasattr(e, 'code'):
      logging.main_logger.warning('[request] The server couldn\'t fulfill the request. Error code: %s' % (e.code))
      return False
  else:
    return http_response

# to string
def to_string(item):
  for property, value in vars(item).iteritems():
    print property, ": ", value

def remove_quotes(string):
  if string.startswith('"') and string.endswith('"'):
    string = string[1:-1]
  return string

def sanitize(string):
  return remove_quotes(string)
