#! /usr/bin/python

import requests
import argparse
from time import sleep
import json

POLL_SLEEP_LENGTH = 0.05  # 50ms
port = 8000

def url(endpoint):
  return "http://localhost:%d/%s" % (port, endpoint)

def get_response(endpoint, protocol, data=None):
  assert protocol in ["GET", "POST"]

  fn = {"GET": requests.get, "POST": requests.post}[protocol]

  if data is not None:
    response = fn(url(endpoint), data).json()
  else:
    response = fn(url(endpoint)).json()

  if "error" in response and response["error"] != "":
    raise Exception(response["error"])
  return response


# Returns the player index
def join_game():
  return get_response("join", "POST", {})["player_index"]

def request_state():
  return get_response("state", "GET")

def print_moves(moves):
  for move in moves:
    move_type = move["type"]
    card_name = move["card_name"] if "card_name" in move else ""
    print "\t%s %s" % (move_type, card_name)

# data should be a dict with keys "player_index" and "moves"
def post_moves(player_index, moves):
  # print_moves(moves)
  return get_response("moves", "POST", json.dumps({
    "player_index": player_index,
    "moves": moves
  }))

def status_is_not_ready(state):
  return state["status"] == "not ready"

def game_is_over(state):
  return state["status"] == "ended"

def is_my_turn(state, player_index):
  return "board" in state and int(state["board"]["current_player_index"]) == player_index

def create_move(move_type, card_name):
  return {
    "type": move_type,
    "card_name": card_name
  }

def get_player_from_state(state, player_index):
  return state["board"]["players"][player_index]

def print_state(state, player_index):
  board = state["board"]
  me = board["players"][player_index]

  print "Current State:"
  print """\tcurrent turn: %s
\tcurrent player index: %s
\thonor remaining: %s
\tvoid: %s
\tcenter: %s
\tmystics: %s
\theavy: %s

\thand: %s
\tdiscard: %s
\trunes remaining: %s
\tpower remaining: %s
\thonor: %s
""" % (board["current_turn"],
      board["current_player_index"],
      board["honor_remaining"],
      str(board["void"]),
      str(board["center"]),
      board["mystics"],
      board["heavy"],
      str(me["hand"]),
      str(me["discard"]),
      me["runes_remaining"],
      me["power_remaining"],
      me["honor"])

def play_turn(state, player_index):
  # We employ a very simple strategy to demonstrate the client:
  #
  #   On any given turn, do the following:
  #     1) Play all cards.
  #     2) Buy RUNES/2 heavy infantry.
  #     3) Kill the cultist POWER/2 times.
  #
  # Since we never buy anything that isn't simple, we never have to deal with
  # specifying targets of effects.

  # print_state(state, player_index)
  hand = get_player_from_state(state, player_index)["hand"]
  moves = [create_move("play", card_name) for card_name in hand]

  new_state = post_moves(player_index, moves)
  # print_state(new_state, player_index)

  player = get_player_from_state(new_state, player_index)
  runes = player["runes_remaining"]
  power = player["power_remaining"]

  moves = ([create_move("acquire", "Heavy Infantry")] * (runes / 2) +
    [create_move("defeat", "Cultist")] * (power / 2) +
    [{"type": "end_turn"}])

  post_moves(player_index, moves)


def parse_port():
  parser = argparse.ArgumentParser(description="Run an Ascension client")
  parser.add_argument("--port", default="8000", type=int)
  return parser.parse_args().port


if __name__ == "__main__":
  port = parse_port()

  player_index = join_game()
  print "Joined as player", player_index

  state = request_state()
  while status_is_not_ready(state):
    sleep(POLL_SLEEP_LENGTH)
    state = request_state()

  while not game_is_over(state):
    if is_my_turn(state, player_index):
      play_turn(state, player_index)

    sleep(POLL_SLEEP_LENGTH)
    state = request_state()

  print "Game over!"
