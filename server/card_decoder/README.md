Dependencies:
  * `py.test` (`pip install pytest`)

To test, run `py.test`

To decode the cards:

    from decoder import CardDecoder
    cards = CardDecoder().decode_cards()

The module contains the definitions of all the cards, with each card being a
a row in a csv (either `input/acquirables.csv` or `input/defeatables.csv`).
The columns for the csv are the parameters to the constructors for the
respective classes in cards.py.

In addition, each effect is described in `input/effects.txt` as a format string
with at most one integer parameter (specified as `%d`). The effects are
referenced by their one-index in the card files. There is one effect that gains
a negative amount of runes (for the Yggdrasil Staff); this of course means that
a player must have at least that many runes to use the effect. This should be
taken into account for all of the "gain" effects.

