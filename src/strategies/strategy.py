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
    self.card_dictionary = CardDecoder().decode_cards()

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
  # < raised from:
  #     moves.py#apply_acquire
  #     events.py#_take_random_card_from_each_opponent
  # >
  def me_acquired_card(self, card):
    pass

  # Called when an opponent strategy acquires a card
  # (including Mystic/Heavy/take card from opponent)
  # < raised from:
  #     moves.py#apply_acquire
  #     events.py#_take_random_card_from_each_opponent
  # >
  def opponent_acquired_card(self, opponent_index, card):
    pass

  # Called when this strategy defeats a card (including Cultist)
  # < raised from moves.py#apply_defeat >
  def me_defeated_card(self, card):
    pass

  # Called when an opponent strategy defeats a card (including Cultist)
  # < raised from moves.py#apply_defeat >
  def opponent_defeated_card(self, opponent_index, card):
    pass

  # Called when a card is banished from this strategy's deck
  # (including hand/discard pile/Tablet of Time's Dawn/take card from opponent)
  # < raised from:
  #     effects.py#_banish_card_from_hand
  #     effects.py#_banish_card_from_discard
  #     effects.py#_banish_for_additional_turn
  #     effects.py#_take_random_card_from_each_opponent
  # >
  def me_banished_from_deck(self, card):
    pass

  # Called when a card is banished from an opponent strategy's deck
  # (including hand/discard pile/Tablet of Time's Dawn/take card from opponent)
  # < raised from:
  #     effects.py#_banish_card_from_hand
  #     effects.py#_banish_card_from_discard
  #     effects.py#_banish_for_additional_turn
  #     effects.py#_take_random_card_from_each_opponent
  # >
  def opponent_banished_from_deck(self, opponent_index, card):
    pass

  # Called when this strategy banishes a card from the center row
  # < raised from effects.py#_banish_card_from_center >
  def me_banished_from_center(self, card):
    pass

  # Called when an opponent strategy banishes a card from the center row
  # < raised from effects.py#_banish_card_from_center >
  def opponent_banished_from_center(self, opponent_index, card):
    pass

  # Called whenever this strategy puts a construct into play
  # < raised from player.py#play_card >
  def me_construct_placed(self, card):
    pass

  # Called whenever an opponent strategy puts a construct into play
  # < raised from player.py#play_card >
  def opponent_construct_placed(self, opponent_index, card):
    pass

  # Called whenever this strategy discards or banishes a construct from play
  # (including Tablet of Time's Dawn, not including constructs taken from hand)
  # < raised from:
  #     effects.py#_banish_for_additional_turn
  #     effects.py#_destroy_opponent_construct
  # >
  def me_construct_removed(self, card):
    pass

  # Called whenever an opponent strategy discards or banishes
  # a construct from play (including Tablet of Time's Dawn,
  # not including constructs taken from hand)
  # < raised from:
  #     effects.py#_banish_for_additional_turn
  #     effects.py#_destroy_opponent_construct
  # >
  def opponent_construct_removed(self, opponent_index, card):
    pass

  ### End of Card Events ###

  ### Deck Events ###

  # Called when this strategy has exhausted its draw deck, causing its
  # discard pile to be shuffled.
  def me_deck_finished(self):
    pass

  # Called when an opponent strategy has exhausted its draw deck,
  # causing its discard pile to be shuffled.
  def opponent_deck_finished(self, opponent_index):
    pass

  ### End of Deck Events ###

  ### Other Events ###

  # Called when both this strategy and all opponent strategies
  # have played their turn (i.e. they have played equal # of turns)
  # < raised from events.py#raise_end_round_events (via board.py#end_round) >
  def round_finished(self, board):
    pass

  ### End of Other Events ###
