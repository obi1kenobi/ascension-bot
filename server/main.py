#! /usr/bin/python

from firebase import firebase
from time import sleep
from board import Board
from collections import defaultdict

FIREBASE_URL = 'https://ascension-bot.firebaseio.com'

def wait_for_players(firebase, game_id):
  result = firebase.get('/games/', game_id)

  while 'players' not in result or len(result['players']) != 2:
    result = firebase.get('/games/', game_id)
    sleep(1)

  return result['players'].keys()


def card_list_to_firebase_dict(card_list):
  D = defaultdict(int)
  for card in card_list:
    D[card.name] += 1
  return D


def player_to_firebase_dict(player):
  return {
    'hand': card_list_to_firebase_dict(player.hand),
    'discard': card_list_to_firebase_dict(player.discard),
    'constructs': card_list_to_firebase_dict(player.constructs),
    'honor': 0,
  }


def initialize_board(firebase, game_id, player_ids):
  board = Board(player_ids)
  result = firebase.put('/games/', game_id, {
    'current_turn': player_ids[board.current_turn_index],
    'board': {
      'mystics': board.mystics,
      'heavy': board.heavy,
      'cultist': 1,
      'center': card_list_to_firebase_dict(board.center)
    },
    'players': {
      player_id: player_to_firebase_dict(board.players[player_id])
        for player_id in player_ids
    }
  })
  print result


if __name__ == '__main__':
  firebase = firebase.FirebaseApplication(FIREBASE_URL, authentication=None)

  result = firebase.post('/games/', '')
  game_id = result['name']
  print "Game Id:", game_id

  player_ids = wait_for_players(firebase, result['name'])
  initialize_board(firebase, game_id, player_ids)

