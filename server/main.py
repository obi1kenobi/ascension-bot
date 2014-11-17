#! /usr/bin/python

from board import Board
from firebase_game import FirebaseGame

if __name__ == '__main__':
  firebase_game = FirebaseGame()
  game_id = firebase_game.create_game()
  print "Game Id:", game_id

  player_ids = firebase_game.wait_for_players()

  board = Board(player_ids)
  print firebase_game.set_board(board)

