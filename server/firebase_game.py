from firebase import firebase
from collections import defaultdict
from time import sleep

FIREBASE_URL = 'https://ascension-bot.firebaseio.com'


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


class FirebaseGame(object):
  def __init__(self):
    self.firebase = firebase.FirebaseApplication(FIREBASE_URL, authentication=None)

  def create_game(self):
    result = self.firebase.post('/games/', '')
    self.game_id = result['name']
    return self.game_id

  def wait_for_players(self):
    result = self.firebase.get('/games/', self.game_id)

    while 'players' not in result or len(result['players']) != 2:
      result = self.firebase.get('/games/', self.game_id)
      sleep(1)

    self.player_ids = result['players'].keys()
    return self.player_ids

  def set_board(self, board):
    result = self.firebase.put('/games/', self.game_id, {
      'current_turn': self.player_ids[board.current_turn_index],
      'board': {
        'mystics': board.mystics,
        'heavy': board.heavy,
        'cultist': 1,
        'center': card_list_to_firebase_dict(board.center)
      },
      'players': {
        player_id: player_to_firebase_dict(board.players[player_id])
          for player_id in self.player_ids
      }
    })
    return result

