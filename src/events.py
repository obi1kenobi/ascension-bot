# All card-related events take (self, card) as arguments
# so we can call them generically like this
def raise_strategy_card_events(board, me_func, others_func, card_name):
  card = board.card_dictionary.find_card(card_name)
  me_func(board.current_player(), card)
  for p in board.other_players():
    others_func(p, card)
