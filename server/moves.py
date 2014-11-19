
class Move(object):
  # These parameters should be passed directly from the dictionary.
  # This will parse the turn index and validate the move type
  def __init__(self, move_id, turn_index, move_type, card_name):
    assert move_type in ["acquire", "defeat", "play"]
    self.move_id = move_id
    self.turn_index = int(turn_index)
    self.move_type = move_type
    self.card_name = card_name

  @classmethod
  def parse_unacknowledged_moves_from_dict(cls, move_dict):
    return [
      cls(
          key,
          move_dict[key]['turn_index'],
          move_dict[key]['move_type'],
          move_dict[key]['card_name'])
        for key in move_dict.keys()
        if 'acknowledged' not in move_dict[key]
    ]

  # TODO(ddoucet): this involves parsing all of the effects and such...
  def apply_to_board(self, board):
    print "Applying move!"
    print "\tid:%s, turn index: %d, move type: %s, card name: %s" % (
      self.move_id, self.turn_index, self.move_type, self.card_name)

    move_type_to_fn = {
      'play': self.apply_play,
      'acquire': self.apply_acquire,
      'defeat': self.apply_defeat
    }
    move_type_to_fn[self.move_type](board)

    print "runes: %d, power: %d, honor: %d" % (
      board.current_player().runes,
      board.current_player().power,
      board.current_player().honor)

      # TODO(ddoucet): doesn't check for game over

  def apply_play(self, board):
    assert self.move_type == "play"

    msg = "Tried to play %s" % self.card_name
    assert self.card_name in ["Apprentice", "Militia"], msg

    # play_card raises an Exception if the card isn't there
    board.current_player().play_card(self.card_name)
    if self.card_name == "Apprentice":
      board.current_player().runes += 1
    else:
      board.current_player().power += 1

  def apply_acquire(self, board):
    assert self.move_type == "acquire"

    msg = "Tried to acquire %s" % self.card_name
    assert self.card_name == "Heavy Infantry", msg

    assert board.current_player().runes >= 2

    board.current_player().runes -= 2
    card = board.card_dictionary.find_card("Heavy Infantry")
    board.current_player().acquire(card)

  def apply_defeat(self, board):
    assert self.move_type == "defeat"
    assert self.card_name == "Cultist", "Tried to defeat %s" % self.card_name

    assert board.current_player().power >= 2

    board.current_player().power -= 2
    board.give_honor(board.current_player(), 1)
    

