# All card-related events take (self, card) / (self, card, index) as arguments
# so we can call them as follows:
#
#   raise_strategy_card_events(self.board, 'construct_placed', card_name)
#
#
# All deck-related events take (self) / (self, index) as arguments,
# so we can call them as follows:
#
#   raise_strategy_deck_events(self.board, 'deck_finished')
#

def raise_strategy_card_events(board, event_key, card_name):
  card = board.card_dictionary.find_card(card_name)
  (me_func, others_func) = events[event_key]
  me_func(board.current_player().strategy, card)
  for p in board.other_players():
    others_func(p.strategy, board.current_player_index, card)

def raise_strategy_card_events_for_player(board, me_player_index, event_key, card_name):
  card = board.card_dictionary.find_card(card_name)
  (me_func, others_func) = events[event_key]
  me_player = board.players[me_player_index]
  other_players = [board.players[i] for i in xrange(len(board.players)) if i != me_player_index]
  me_func(me_player.strategy, card)
  for p in other_players:
    others_func(p.strategy, me_player_index, card)

def raise_strategy_deck_events(board, event_key):
  (me_func, others_func) = events[event_key]
  me_func(board.current_player().strategy)
  for p in board.other_players():
    others_func(p.strategy, board.current_player_index)

def raise_end_round_events(board):
  for s in board.strategies:
    s.round_finished(board)

events = { \
  'acquired_card': \
    (lambda strategy, card: strategy.me_acquired_card(card), \
     lambda strategy, index, card: strategy.opponent_acquired_card(index, card)), \
  'defeated_card': \
    (lambda strategy, card: strategy.me_defeated_card(card), \
     lambda strategy, index, card: strategy.opponent_defeated_card(index, card)), \
  'banished_from_deck': \
    (lambda strategy, card: strategy.me_banished_from_deck(card), \
     lambda strategy, index, card: strategy.opponent_banished_from_deck(index, card)), \
  'banished_from_center': \
    (lambda strategy, card: strategy.me_banished_from_center(card), \
     lambda strategy, index, card: strategy.opponent_banished_from_center(index, card)), \
  'construct_placed': \
    (lambda strategy, card: strategy.me_construct_placed(card), \
     lambda strategy, index, card: strategy.opponent_construct_placed(index, card)), \
  'construct_removed': \
    (lambda strategy, card: strategy.me_construct_removed(card), \
     lambda strategy, index, card: strategy.opponent_construct_removed(index, card)), \
  'deck_finished': \
    (lambda strategy: strategy.me_deck_finished(), \
     lambda strategy, index: strategy.opponent_deck_finished(index)) \
}
