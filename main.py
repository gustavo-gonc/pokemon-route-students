from game.pokemon_game import PokemonGame
from gui.pokemon_gui import PokemonGUI
from gui.starter_gui import StarterGUI

def main():

    starter_gui = StarterGUI()
    starter = starter_gui.run()

    if starter is None:
        return
    prolog_file="prolog/pokemon_game.pl"
        
    gui = PokemonGUI(
        prolog_file=prolog_file, 
        starter_id=starter
    )

    game = PokemonGame(
        prolog_file=prolog_file,
        starter_id=starter
    )

    # Start stepwise game + GUI updates
    gui.start_game(game, delay=800)

    gui.run()


if __name__ == "__main__":
    main()