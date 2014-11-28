"""
  This is the class that wraps all strategies. Simply implement this and then
  plug it into main.py.
"""

from .. import log
from src.card_decoder.decoder import CardDecoder

PLAYER_INDEX_TO_COLOR = {
  0: log.GREEN,
  1: log.BLUE
}


class Strategy(object):
  def __init__(self, tag, player_index):
    self.tag = tag
    self.player_index = player_index
    self.card_dictionary = CardDecoder.decode_cards()

    logger_name = "p%d.%s" % (player_index, tag)
    color = PLAYER_INDEX_TO_COLOR[player_index]
    self.logger = log.create_logger(logger_name)

    self.logging_extra = {
      "color_seq": color
    }

  def log(self, msg):
    # TODO(ddoucet): we should parametrize the logger name or something
    # so that we can have things like p0.basic.eval
    self.logger.info(msg, extra=self.logging_extra)

  # winner will either be str(index) or "tie"
  def log_end_game(self, winner):
    if winner == str(self.player_index):
      self.log("I won!")
    elif winner == "tie":
      self.log("We tied")
    else:
      self.log("I lost!")

  def play_move(self, board, move):
    self.log(str(move))
    move.apply_to_board(board)

  def play_turn(self, board, opponents_previous_moves):
    raise NotImplementedError('play_turn')

  def choose_construct_for_discard(self, board):
    raise NotImplementedError('choose_construct_for_discard')

  ### Card Events ###

  # Called when this strategy acquires a card
  # (including Mystic/Heavy/take card from opponent)
  def me_acquired_card(self, card):
    pass

  # Called when the opponent strategy acquires a card
  # (including Mystic/Heavy/take card from opponent)
  def opponent_acquired_card(self, card):
    pass

  # Called when this strategy defeats a card (including Cultist)
  def me_defeated_card(self, card):
    pass

  # Called when the opponent strategy defeats a card (including Cultist)
  def opponent_defeated_card(self, card):
    pass

  # Called when this strategy banishes a card from its deck
  # (including hand/discard pile/Tablet of Time's Dawn/take card from opponent)
  def me_banished_from_deck(self, card):
    pass

  # Called when the opponent strategy banishes a card from its deck
  # (including hand/discard pile/Tablet of Time's Dawn/take card from opponent)
  def opponent_banished_from_deck(self, card):
    pass

  # Called when this strategy banishes a card from the center row
  def me_banished_from_center(self, card):
    pass

  # Called when the opponent strategy banishes a card from the center row
  def opponent_banished_from_center(self, card):
    pass

  # Called whenever this strategy puts a construct into play
  def me_construct_placed(self, card):
    pass

  # Called whenever the opponent strategy puts a construct into play
  def opponent_construct_placed(self, card):
    pass

  # Called whenever this strategy discards or banishes a construct from play
  # (including Tablet of Time's Dawn)
  def me_construct_removed(self, card):
    pass

  # Called whenever the opponent strategy discards or banishes
  # a construct from play (including Tablet of Time's Dawn)
  def opponent_construct_removed(self, card):
    pass

  ### End of Card Events ###

  ### Other Events ###

  # Called when this strategy has exhausted its draw deck, causing its
  # discard pile to be shuffled.
  def me_deck_finished(self):
    pass

  # Called when the opponent strategy has exhausted its draw deck,
  # causing its discard pile to be shuffled.
  def opponent_deck_finished(self):
    pass

  # Called when both this strategy and the opponent strategy
  # have played their turn (i.e. they have played equal # of turns)
  def round_finished(self):
    pass

  ### End of Other Events ###
