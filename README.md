ascension-bot
=============

A system to play the Ascension: Chronicle of the Godslayer board game in an automated fashion for the purposes of game-theoretic analysis of various strategies.


Repository Structure
====================

  main.py
    This is the main program. Modify this to plug in which strategies to use
    for a given run.

  scripts/
    scripts for general usage.

  src/
    card_decoder/ - Handles the actual effects of the game.

      input/ - Text files that contain the encoded card data
      cards.py - Definitions of classes used for card stuff
      decoder.py - Entry point into this module. See the top of the file for
        how to use it.
      files.py - Utilities for reading the input
      test_decoder.py - Unit tests. Run py.test from the card_decoder directory.

    strategies/ - Where the AI lives
      strategy.py - Basic interface for defining a strategy
      basic_strategy.py - Very basic strategy for testing.

    board.py - Entry point for the game. Creates player objects and handles
      most of the resources.

    deck.py - Handles drawing/shuffling from a list of cards.

    moves.py - How the board is generally mutated. This happens with specific
      move types, such as "acquire", "play", or "defeat" from the AI.

    player.py - An object that has honor, runes remaining, a deck, etc.

Usage
=====

Modify `main.py` to use the strategies that you want, then run

`./main.py`

