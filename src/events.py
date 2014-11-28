# All card-related events take (self, card) as arguments
# so we can call them generically using these methods as follows:
#
# raise_strategy_card_events(board,       \
#   Strategy.me_banished_from_deck,       \
#   Strategy.opponent_banished_from_deck, \
#   card_name)
#

def raise_strategy_card_events(board, me_func, others_func, card_name):
  card = board.card_dictionary.find_card(card_name)
  me_func(board.current_player().strategy, card)
  for p in board.other_players():
    others_func(p.strategy, board.current_player_index, card)

def raise_strategy_card_events_for_player(board, me_player_index, me_func, others_func, card_name):
  card = board.card_dictionary.find_card(card_name)
  me_player = board.players[me_player_index]
  other_players = [board.players[i] for i in xrange(len(board.players)) if i != me_player_index]
  me_func(me_player.strategy, card)
  for p in other_players:
    others_func(p.strategy, me_player_index, card)

def raise_strategy_deck_events(board, me_func, others_func):
  me_func(board.current_player().strategy)
  for p in board.other_players():
    others_func(p.strategy, board.current_player_index)

def raise_end_round_events(strategies):
  for s in strategies:
    s.round_finished()
