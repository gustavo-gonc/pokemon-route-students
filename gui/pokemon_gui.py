import tkinter as tk
from PIL import Image, ImageTk
from pyswip import Prolog
import re
import os

TILE_SIZE = 64

class PokemonGUI:
    def __init__(self, prolog_file="prolog/pokemon_game.pl", starter_id=1, image_folder="images"):
        self.prolog = Prolog()
        self.prolog.consult(prolog_file)
        self.starter_id = starter_id
        self.IMG_DIR = image_folder

        # Single map_images dictionary: (row,col) -> canvas image id
        self.map_images = {}

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Pokemon Route")

        # Load images
        self.images = {}
        self.load_images()

        # Load map from Prolog
        self.game_map = list(self.prolog.query("route(X)"))[0]['X']
        self.new_map = [[int(re.findall(r'\d+', c)[0]) for c in row] for row in self.game_map]

        self.rows = len(self.new_map)
        self.cols = len(self.new_map[0])

        self.canvas = tk.Canvas(self.root, width=self.cols*TILE_SIZE, height=self.rows*TILE_SIZE)
        self.canvas.pack()

        # Draw initial map
        self.draw_map()

    # -----------------------

    def load_images(self):
        # Automatically load all PNG images in the folder
        for filename in os.listdir(self.IMG_DIR):
            if filename.endswith(".png"):
                name = filename.split(".")[0]
                path = os.path.join(self.IMG_DIR, filename)
                img = Image.open(path).resize((TILE_SIZE, TILE_SIZE))
                self.images[name] = ImageTk.PhotoImage(img)

    # -----------------------

    def get_pokemon_name(self, pid):
        if pid == 0:
            return list(self.prolog.query(f"pokemon({self.starter_id},Name,Types)"))[0]['Name']
        else:
            return list(self.prolog.query(f"pokemon({pid},Name,Types)"))[0]['Name']

    # -----------------------

    def draw_map(self):
        for i, row in enumerate(self.new_map):
            for j, cell in enumerate(row):
                pname = self.get_pokemon_name(cell)
                img_id = self.canvas.create_image(j*TILE_SIZE, i*TILE_SIZE, anchor="nw", image=self.images[pname])
                self.map_images[(i,j)] = img_id

    # -----------------------

    def move_pokemon(self, old_pos, new_pos, steps=16):
        if new_pos in self.map_images:
            self.canvas.delete(self.map_images[new_pos])
            del self.map_images[new_pos]

        img_id = self.map_images[old_pos]
        dx = (new_pos[1]-old_pos[1])*TILE_SIZE
        dy = (new_pos[0]-old_pos[0])*TILE_SIZE
        step_x = dx / steps
        step_y = dy / steps

        def animate(step=0):
            if step < steps:
                self.canvas.move(img_id, step_x, step_y)
                self.root.after(20, animate, step+1)
            else:
                self.map_images[new_pos] = img_id
                del self.map_images[old_pos]

        animate()

    # -----------------------

    def start_game(self, game, delay=500):
        """
        Stepwise integration with PokemonGame
        """
        def step():
            old_pos, new_pos, prob, game_over = game.next_step()
            if old_pos is not None:
                self.move_pokemon(old_pos, new_pos)
            if not game_over:
                self.root.after(delay, step)
            else:
                print("Game Over. Final Level:", game.pokemon_level)

        self.root.after(delay, step)

    # -----------------------

    def run(self):
        self.root.mainloop()


def main():
    gui = PokemonGUI(prolog_file="prolog/pokemon_game.pl", starter_id=1, image_folder="images")

    # Example: move player from (0,0) to (0,1) after 1 second
    gui.root.after(1000, lambda: gui.move_pokemon((0,0),(0,1)))

    # Example: move another Pokémon
    gui.root.after(2000, lambda: gui.move_pokemon((2,3),(2,4)))

    gui.run()

if __name__ == "__main__":
    main()
