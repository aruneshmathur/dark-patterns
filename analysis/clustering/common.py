from __future__ import print_function
import datetime
import sys

# Prints a log statement, which includes a timestamp and a message.
def debug(message):
  timestamp = datetime.datetime.now()
  print('%s %s' % (str(timestamp), message))
  sys.stdout.flush()
