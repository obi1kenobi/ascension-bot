#!/usr/bin/python

import logging
import sys

extra = None

def setup_logging(player_index):
  global extra
  FORMAT = '%(asctime)-15s P%(player_index)-8s %(message)s'
  extra = {'player_index': player_index}
  logging.basicConfig(format=FORMAT, lvl=logging.INFO)
  handler = logging.StreamHandler()
  logging.getLogger().addHandler(handler)
