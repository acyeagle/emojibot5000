
import logging

"""
Logging levels, because I always forget:

CRITICAL : 50
ERROR : 40
WARNING : 30
INFO : 20
~Verbose~ : 15
DEBUG : 10
NOTSET : 0
"""

### Add custom 'VERBOSE' level ###
VERBOSE = 15
logging.addLevelName(VERBOSE, "VERBOSE")
def verbose(self, message, *args, **kws):
	if self.isEnabledFor(VERBOSE):
		self._log(VERBOSE, message, args, **kws)
logging.Logger.verbose = verbose

### General logging config ###
logging.basicConfig(filename='bot.log',
	filemode='a',
	format='%(asctime)s | %(name)-12s | %(levelname)-10s | %(message)s',
	datefmt='%H:%M:%S',
	level=15)