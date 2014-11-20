#!/usr/bin/python

import requests
import logging
from time import sleep
import json
import log

class RestClient(object):
  def __init__(self, url=None, port=None):
    if url == None:
      url = "http://localhost"
    if port == None:
      port = 8000

    self.url = url
    self.port = port

  # Joins a new game, returns the player index
  def join_game(self):
    return self._get_response("join", "POST", {})["player_index"]

  # Returns the current state of the game
  def request_state(self):
    return self._get_response("state", "GET")

  # Posts a list of moves
  def post_moves(self, player_index, moves):
    # print_moves(moves)
    return self._get_response("moves", "POST", json.dumps({
      "player_index": player_index,
      "moves": moves
    }))

  def _url(self, endpoint):
    return "%s:%d/%s" % (self.url, self.port, endpoint)

  def _get_response(self, endpoint, protocol, data=None):
    assert protocol in ["GET", "POST"]

    fn = {"GET": requests.get, "POST": requests.post}[protocol]

    if data is not None:
      response = fn(self._url(endpoint), data).json()
    else:
      response = fn(self._url(endpoint)).json()

    if "error" in response and response["error"] != "":
      raise Exception(response["error"])
    return response


class AscensionClient(object):
  POLL_SLEEP_LENGTH = 0.05  # 50ms

  def __init__(self, url=None, port=None):
    self.client = RestClient(url, port)
    self.state = None
    self.logger = None

  def join_game(self):
    self.player_index = self.client.join_game()

    log.setup_logging(self.player_index)
    self.logger = logging.getLogger('web.asc')
    self.logger.info("Joined as player %d", self.player_index, log.extra)

    self.state = self.client.request_state()
    while self._status_is_not_ready(self.state):
      sleep(AscensionClient.POLL_SLEEP_LENGTH)
      self.state = self.client.request_state()

  def play(self, play_turn):
    def post_moves(moves):
      return self.client.post_moves(self.player_index, moves)

    while not self._game_is_over(self.state):
      if self._is_my_turn(self.state, self.player_index):
        play_turn(self.state, self.player_index, post_moves)

      sleep(AscensionClient.POLL_SLEEP_LENGTH)
      self.state = self.client.request_state()

  def _status_is_not_ready(self, state):
    return state["status"] == "not ready"

  def _game_is_over(self, state):
    return state["status"] == "ended"

  def _is_my_turn(self, state, player_index):
    return "board" in state and int(state["board"]["current_player_index"]) == player_index
