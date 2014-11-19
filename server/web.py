import os, os.path

import tornado.ioloop
import tornado.web
import tornado.log
import tornado.escape

from board import Board
from moves import Move
import dict_encoder

"""
  The webserver has three endpoints. /state and /moves both return a JSON-
  encoded state dictionary. /join returns which player index the requester
  is (or an error if enough players have already joined).

  POST /join -- join the game

    Only legal if less than two players have joined the game (i.e.,
    state["player_count"] < 2. This increments the player count, and if the
    game has reached two players, it initializes the board, inserts that into
    the state, and sets the status to "playing".

    Return values:
      {"player_index": <0-based index>}
        OR
      {"error": <error string>}

  GET /state -- request the current state

    Simply returns the current state. Players should poll this while either the
    game hasn't started, or it is not the player's turn.

  POST /moves -- submit moves

    Accepts a JSON dictionary of moves. The server applies each of the moves
    to the board and then returns the state.

"""

PLAYERS_PER_GAME = 2


class State(object):
  def __init__(self):
    self.player_count = 0
    self.status = "not started"
    self.error = ""

    self.board = None  # will get initialized once players join
    self.log_file = None  # gets initialized in WebServer.__enter__

  def encode(self):
    return dict_encoder.encode_state(self)

  def print_line(self, msg):
    self.log_file.write(msg + '\n')


class JoinHandler(tornado.web.RequestHandler):
  def initialize(self, state):
    self.state = state

  def post(self):
    if self.state.player_count >= PLAYERS_PER_GAME:
      self.write({"error": "Enough players have already joined."})
      return

    self.state.player_count += 1

    if self.state.player_count == PLAYERS_PER_GAME:
      self.state.board = Board(PLAYERS_PER_GAME)
      self.state.status = "playing"

    self.state.print_line(str(self.state.encode()))
    self.write({"player_index": self.state.player_count - 1})


class StateHandler(tornado.web.RequestHandler):
  def initialize(self, state):
    self.state = state

  def get(self):
    self.state.print_line(str(self.state.encode()))
    self.write(self.state.encode())


class MovesHandler(tornado.web.RequestHandler):
  def initialize(self, state):
    self.state = state

  def post(self):
    if self.state.status != "playing":
      self.write({"error": "Tried to make move while not playing"})
      return

    params = tornado.escape.json_decode(self.request.body)
    player_index = params["player_index"]
    move_dicts = params["moves"]

    msg = "MOVE: player_index: %s; moves: %s" % (player_index, move_dicts)

    for move_dict in move_dicts:
      move_type = move_dict["type"]
      card_name = move_dict["card_name"] if "card_name" in move_dict else ""

      move = Move(move_type, card_name)
      move.apply_to_board(self.state.board)

    self.write(self.state.encode())


class WebServer(object):
  def __init__(self, game_id, port):
    self.state = State()

    tornado.log.enable_pretty_logging()
    self.application = tornado.web.Application([
      (r"/join", JoinHandler, dict(state=self.state)),
      (r"/state", StateHandler, dict(state=self.state)),
      (r"/moves", MovesHandler, dict(state=self.state)),
    ])

    self.game_id = game_id
    self.port = port

  def __enter__(self):
    log_path = "logs/%s.txt" % self.game_id
    if not os.path.exists(os.path.dirname(log_path)):
      os.makedirs(os.path.dirname(log_path))

    self.state.log_file = open(log_path, "w")
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    self.state.log_file.close()

  def poll(self):
    print "Game Id:", self.game_id
    print "Listening on", self.port
    self.application.listen(self.port)
    tornado.ioloop.IOLoop.instance().start()

