#!/usr/bin/env python3

from gen_lib import loadPokedex
from pok_lib import PokemonObject
from pok_ui import PokemonMenu
import sys

pokedex = loadPokedex("pokedex/pokedex.pickle")
pokemon = PokemonObject(pokedex[sys.argv[1]])
PokemonMenu(pokemon).mainloop()
