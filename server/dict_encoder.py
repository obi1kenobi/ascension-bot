"""
  Represents the objects as dictionaries so they can be returned as JSON to the
  client.
"""

def encode_player(player):
  return {
    "hand": [card.name for card in player.hand],
    "discard": [card.name for card in player.discard],
    "constructs": [card.name for card in player.constructs],
    "runes_remaining": player.runes_remaining,
    "power_remaining": player.power_remaining,
    "honor": player.honor
  }

def encode_board(board):
  board_dict = {
    "current_turn": board.turns,
    "current_player_index": board.current_player_index,
    "honor_remaining": board.honor_remaining,

    "void": [card.name for card in board.void],
    "center": [card.name for card in board.center],

    "mystics": board.mystics,
    "heavy": board.heavy,
    "cultist": 1,

    "players": [
      encode_player(player) for player in board.players
    ]
  }

  if board.victor:
    board_dict["victor"] = board.victor

  return board_dict

def encode_state(state):
  state_dict = {
    "player_count": state.player_count,
    "status": state.status,
    "error": state.error
  }

  if state.board:
    state_dict["board"] = encode_board(state.board)

  return state_dict

