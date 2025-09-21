# cartomancy

a CLI for drawing tarot and minchiate cards, for quick, portable readings right in your terminal


## features

- supports two decks: **tarot** and **minchiate**
- draw any number of cards: 1-78 for tarot and 1-97 for minchiate
- optional reversals


## installation

cartomancy can be installed directly from [pypi](https://pypi.org/project/cartomancy).

```
# try without installing
uvx cartomancy

# install globally
uv tool insttall cartomancy

# or more traditionally
pip install --user cartomancy
pipx install cartomancy
```

## usage

```sh
usage: cards [-h] [-r] {tarot,minchiate} N

cartomancy in the terminal 🃏

positional arguments:
  {tarot,minchiate}  pick a deck
  N                  # of cards to draw

options:
  -h, --help         show this help message and exit
  -r, --reversals    allow reversals
```
