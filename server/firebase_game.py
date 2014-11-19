from time import sleep
from collections import defaultdict
from firebase import firebase
from moves import Move

FIREBASE_URL = 'https://ascension-bot.firebaseio.com'
POLL_SLEEP_LENGTH = 0.25  # seconds


def card_list_to_firebase_dict(card_list):
  D = defaultdict(int)
  for card in card_list:
    D[card.name] += 1
  return D

def update_player_firebase(firebase, node, player):
  # TODO(ddoucet): I think this is going to overwrite the moves list :/
  # we would like to patch to update the player but without modifying the
  # moves list. does this do that? not really sure
  firebase.put(node, 'hand', card_list_to_firebase_dict(player.hand))
  firebase.put(node, 'discard', card_list_to_firebase_dict(player.discard))
  firebase.put(node, 'constructs', card_list_to_firebase_dict(player.constructs))
  firebase.put(node, 'runes_remaining', str(player.runes))
  firebase.put(node, 'power_remaining', str(player.power))
  firebase.put(node, 'honor', str(player.honor))
  print "hand:", player.hand
  print "dict hand:", card_list_to_firebase_dict(player.hand)
  print "putting player: runes: %d power: %d" % (player.runes, player.power)


class FirebaseGame(object):
  def __init__(self):
    self.firebase = firebase.FirebaseApplication(FIREBASE_URL, authentication=None)

  # cb takes a firebase result from getting at parent/child_id. Should return
  # None if it is not ready. Otherwise, the value it returns will be returned
  # by wait_for_result
  def wait_for_result(self, parent, child_id, cb):
    result = self.firebase.get(parent, child_id)
    ret = cb(result)

    while ret is None:
      sleep(POLL_SLEEP_LENGTH)

      result = self.firebase.get(parent, child_id)
      ret = cb(result)

    return ret

  # Adds a node to the games and returns the id.
  def create_game(self):
    result = self.firebase.post('/games/', '')
    self.game_id = result['name']
    self.game_node = '/games/' + self.game_id + '/'
    return self.game_id

  def player_node(self, player_id):
    return '%splayers/%s/' % (self.game_node, player_id)

  def move_node(self, player_id, move_id):
    return '%smoves/%s' % (self.player_node(player_id), move_id)

  # Poll until two players have connected to the firebase.
  # Returns the ids of the players.
  def wait_for_players(self):
    def get_players(result):
      if result is None or len(result.keys()) != 2:
        return None

      return result.keys()

    self.player_ids = self.wait_for_result(self.game_node, 'players', get_players) 
    return self.player_ids

  # Sets the board in the firebase.
  def set_board(self, board):
    self.firebase.put(self.game_node, 'current_turn', str(board.turns))
    self.firebase.put(self.game_node, 'board', {
      'honor_remaining': board.honor_remaining,
      'mystics': board.mystics,
      'heavy': board.heavy,
      'cultist': 1,

      'center': card_list_to_firebase_dict(board.center),
      'void': card_list_to_firebase_dict(board.void)
    })

    for player_id in self.player_ids:
      update_player_firebase(
        self.firebase,
        self.player_node(player_id),
        board.players[player_id])

    self.firebase.put(self.game_node, 'current_player_id',
      board.player_ids[board.current_player_index])

  # Sets the Firebase state to the error state, and optionally rejects a move.
  def on_error(self, error_str, move_node=None):
    self.firebase.put(self.game_node, 'current_turn', '-1')
    self.firebase.put(self.game_node, 'error', error_str)

    if move_node is not None:
      self.firebase.put(move_node, '/acknowledged', 'rejected')

  # Acknowledges any unacknowledged moves from the current player in result.
  # If any of the moves throw an exception, this will catch the exception,
  # insert an error into the firebase, reject the move (so the player knows
  # which move), and then reraise the Exception.
  def acknowledge_moves(self, board, result):
    player_id = board.player_ids[board.current_player_index]
    player_dict = result['players'][player_id]
    if 'moves' not in player_dict:
      return

    print len(player_dict['moves'].keys()), "total moves"

    unacknowledged_moves = Move.parse_unacknowledged_moves_from_dict(
      player_dict['moves'])

    print len(unacknowledged_moves), "unacknowledged moves"

    for move in unacknowledged_moves:
      print "found a move!"
      move_node = self.move_node(player_id, move.move_id)
      try:
        move.apply_to_board(board)
        self.firebase.put(move_node, '/acknowledged', 'accepted')
      except Exception as e:
        self.on_error(str(e), move_node)
        raise e

    # Check if the turn should be changed
    if 'turn_ended' in player_dict and player_dict['turn_ended'] == 'true':
      board.end_turn()

    # We've gotten through all of the moves. Now update the board
    self.set_board(board)

  # Reads and acknowledges moves. Returns once a turn has ended and it has
  # acknowledged all moves for that turn.
  # It also notifies the board that the turn has ended (e.g. so that the board
  # can discard any leftover cards and draw a new hand).
  # Note that this may raise an exception (from acknowledge_moves) if a move
  # has bad input.
  def poll_moves(self, board):
    def get_turn_ended(result, player_id):
      player = result['players'][player_id]
      return player['turn_ended'] if 'turn_ended' in player else 'false'

    player_id = board.player_ids[board.current_player_index]
    result = self.firebase.get('/games/', self.game_id)

    while get_turn_ended(result, player_id) != 'true':
      self.acknowledge_moves(board, result)
      result = self.firebase.get('/games/', self.game_id)
      sleep(POLL_SLEEP_LENGTH)

    # Acknowledge any leftovers
    self.acknowledge_moves(board, result)
    board.end_turn()

