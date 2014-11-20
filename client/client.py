#!/usr/bin/python

import argparse
from web import AscensionClient

client = None

def print_moves(moves):
  for move in moves:
    move_type = move["type"]
    card_name = move["card_name"] if "card_name" in move else ""
    print "\t%s %s" % (move_type, card_name)

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

def play_turn(state, player_index, post_moves):
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

  new_state = post_moves(moves)
  # print_state(new_state, player_index)

  player = get_player_from_state(new_state, player_index)
  runes = player["runes_remaining"]
  power = player["power_remaining"]

  moves = ([create_move("acquire", "Heavy Infantry")] * (runes / 2) +
    [create_move("defeat", "Cultist")] * (power / 2) +
    [{"type": "end_turn"}])

  post_moves(moves)


def parse_port():
  parser = argparse.ArgumentParser(description="Run an Ascension client")
  parser.add_argument("--port", default="8000", type=int)
  return parser.parse_args().port


if __name__ == "__main__":
  port = parse_port()
  client = AscensionClient(port=port)

  client.join_game()

  client.play(play_turn)

  print "Game over!"
