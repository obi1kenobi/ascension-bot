#! /usr/bin/python

from board import Board
from firebase_game import FirebaseGame

if __name__ == '__main__':
  firebase_game = FirebaseGame()
  game_id = firebase_game.create_game()
  print "Game Id:", game_id

  player_ids = firebase_game.wait_for_players()

  board = Board(player_ids)
  firebase_game.set_board(board)

  while not board.game_over:
    # Poll for a single turn. The FirebaseGame tells the board that the turn
    # has ended.
    firebase_game.poll_moves(board)

