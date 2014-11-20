
class Move(object):
  # These parameters should be passed directly from the dictionary.
  # This will parse the turn index and validate the move type
  def __init__(self, turn, move_type, card_name):
    assert move_type in ["acquire", "defeat", "play", "end_turn"]
    self.turn = turn
    self.move_type = move_type
    self.card_name = card_name

  # TODO(ddoucet): need to actually do the effects
  def apply_to_board(self, board):
    print "%d: %s %s" % (
      board.current_player_index, self.move_type, self.card_name),

    move_type_to_fn = {
      'play': self.apply_play,
      'acquire': self.apply_acquire,
      'defeat': self.apply_defeat,
      'end_turn': self.end_turn
    }
    move_type_to_fn[self.move_type](board)

    if self.move_type != "end_turn":
      print "\t\trunes: %d, power: %d, honor: %d" % (
        board.current_player().runes_remaining,
        board.current_player().power_remaining,
        board.current_player().honor)

  def end_turn(self, board):
    board.end_turn()

  def apply_play(self, board):
    assert self.move_type == "play"

    msg = "Tried to play %s" % self.card_name
    assert self.card_name in ["Apprentice", "Militia", "Heavy Infantry"], msg

    # play_card raises an Exception if the card isn't there
    board.current_player().play_card(self.card_name)
    if self.card_name == "Apprentice":
      board.current_player().runes_remaining += 1
    elif self.card_name == "Militia":
      board.current_player().power_remaining += 1
    else:
      board.current_player().power_remaining += 2

  # TODO(ddoucet): mystics and heavies should decrement the counter in board
  # (and also check that there is one to be acquired)
  def apply_acquire(self, board):
    assert self.move_type == "acquire"

    msg = "Tried to acquire %s" % self.card_name
    assert self.card_name == "Heavy Infantry", msg

    assert board.current_player().runes_remaining >= 2

    board.current_player().runes_remaining -= 2
    card = board.card_dictionary.find_card("Heavy Infantry")
    board.current_player().acquire(card)

  def apply_defeat(self, board):
    assert self.move_type == "defeat"
    assert self.card_name == "Cultist", "Tried to defeat %s" % self.card_name

    assert board.current_player().power_remaining >= 2

    board.current_player().power_remaining -= 2
    board.give_honor(board.current_player(), 1)
    

