from src.board import Board

NUM_PLAYERS = 2

def play_game(strategies):
  assert len(strategies) == NUM_PLAYERS

  board = Board(NUM_PLAYERS, strategies)
  last_moves = []

  while not board.game_over:
    # Give each strategy a chance to make a move before checking for game over
    # again.
    while board.current_player_index < len(strategies):
      strategies[board.current_player_index].play_turn(board, last_moves)
      last_moves = board.moves_played_this_turn
      board.end_turn()

    board.current_player_index = 0
    board.end_round()

  board.compute_victor()
  print "Rounds:", board.rounds

  for strategy in strategies:
    strategy.log_end_game(board.victor)

  return board

