#! /usr/bin/python

import string
import random
import argparse

from web import WebServer


# returns a string of ID_LENGTH lowercase/numeric digits
def generate_game_id():
  ID_LENGTH = 10
  DIGITS = string.ascii_lowercase + string.digits

  return ''.join(random.choice(DIGITS) for i in xrange(ID_LENGTH))

def parse_port():
  parser = argparse.ArgumentParser(description="Run an Ascension server")
  parser.add_argument("--port", default="8000", type=int)
  return parser.parse_args().port

if __name__ == "__main__":
  with WebServer(generate_game_id(), parse_port()) as server:
    server.poll()

