#! /usr/bin/python

from firebase import firebase
from time import sleep

POLL_SLEEP_LENGTH = 0.25
FIREBASE_URL = 'https://ascension-bot.firebaseio.com'


# Loop while there is no victor. We poll until the current turn is ours, then
# we play a turn and mark the "turn ended" key as true.
def game_loop(firebase, game_id, player_id):
  result = firebase.get('/games/', game_id)

  while 'victor' not in result:
    if 'current_player_id' in result and result['current_player_id'] == player_id:
      play_turn(firebase, game_id, player_id, result)
      firebase.put('/games/' + game_id, 'turn_ended', 'true')

    sleep(POLL_SLEEP_LENGTH)
    result = firebase.get('/games/', game_id)

def get_card_count(hand_dict, card_name):
  return int(hand_dict[card_name]) if card_name in hand_dict else 0

def create_move(game_result, move_type, card_name):
  return {
    'turn_index': game_result['current_turn'],
    'move_type': move_type,
    'card_name': card_name
  }

def create_resource_moves(firebase, game_result):
  player = game_result['players'][player_id]
  print player.keys()
  print player
  hand_dict = player['hand']
  num_apprentices = get_card_count(hand_dict, "Apprentice")
  num_militia = get_card_count(hand_dict, "Militia")
  num_heavy = get_card_count(hand_dict, "Heavy Infantry")
  print "Hand: %d apprentices, %d militia, %d heavies" % (num_apprentices, num_militia, num_heavy)

  return ([create_move(game_result, "play", "Apprentice")] * num_apprentices +
    [create_move(game_result, "play", "Militia")] * num_militia +
    [create_move(game_result, "play", "Heavy Infantry")] * num_heavy)

# Returns the final result with all moves acknowledged
def wait_until_moves_acknowledged(firebase, game_id, player_id):
  def all_moves_acknowledged(result):
    moves = result['players'][player_id]['moves']
    for key in moves.keys():
      move = moves[key]
      if 'acknowledged' not in move:
        return False
      if move['acknowledged'] != 'accepted':
        raise Exception('bad acknowledged: ' + move['acknowledged'])

    print len(moves), "moves acknowledged"
    return True

  sleep(POLL_SLEEP_LENGTH)
  result = firebase.get('/games/', game_id)

  while not all_moves_acknowledged(result):
    print "waiting for server to acknowledge moves"
    sleep(POLL_SLEEP_LENGTH)
    result = firebase.get('/games/', game_id)

  return result

def post_list(firebase, node, L):
  for obj in L:
    firebase.post(node, obj)

# Plays a turn. Does not set turn_ended
def play_turn(firebase, game_id, player_id, game_result):
  player = game_result['players'][player_id]

  node = '/games/%s/players/%s/moves/' % (game_id, player_id)
  moves = create_resource_moves(firebase, game_result)

  post_list(firebase, node, moves)
  game_result = wait_until_moves_acknowledged(firebase, game_id, player_id)

  player = game_result['players'][player_id]
  print player
  runes = int(player['runes_remaining'])
  power = int(player['power_remaining'])

  # buy min(runes/2, heavies left) heavies
  # kill the cultist power/2 times
  print "Runes: %d, Power: %d" % (runes, power)
  heavies_to_buy = min(runes / 2, int(game_result['board']['heavy']))
  cultists_to_kill = power / 2
  print "Buying %d heavies, Killing the cultist %d times" % (heavies_to_buy, cultists_to_kill)

  moves = ([create_move(game_result, "acquire", "Heavy Infantry")]* heavies_to_buy +
    [create_move(game_result, "defeat", "Cultist")] * cultists_to_kill)

  post_list(firebase, node, moves)
  wait_until_moves_acknowledged(firebase, game_id, player_id)

  node = '/games/%s/players/%s' % (game_id, player_id)
  firebase.put(node, 'turn_ended', 'true')
  

if __name__ == '__main__':
  firebase = firebase.FirebaseApplication(FIREBASE_URL, authentication=None)

  game_id = raw_input("Game id? ")

  node = '/games/' + game_id + '/players/'
  player_id = firebase.post(node, '')['name']

  print "Player Id:", player_id

  game_loop(firebase, game_id, player_id)

