#! /usr/bin/python

from firebase import firebase
from time import sleep

FIREBASE_URL = 'https://ascension-bot.firebaseio.com'

if __name__ == '__main__':
  firebase = firebase.FirebaseApplication(FIREBASE_URL, authentication=None)

  game_id = raw_input("Game id? ")

  node = '/games/' + game_id + '/players/'
  print firebase.post(node, '')
