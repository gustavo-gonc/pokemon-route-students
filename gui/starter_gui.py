import tkinter as tk
from PIL import Image, ImageTk
import os


class StarterGUI:

    def __init__(self, image_folder="images"):
        self.root = tk.Tk()
        self.root.title("Choose your Starter Pokémon")

        self.selected_starter = None
        self.images = {}

        starters = {
            1: "bulbasaur",
            4: "charmander",
            7: "squirtle"
        }

        tk.Label(self.root, text="Choose your Starter!", font=("Arial", 16)).pack(pady=10)

        frame = tk.Frame(self.root)
        frame.pack()

        for pid, name in starters.items():

            img_path = os.path.join(image_folder, f"{name}.png")
            img = Image.open(img_path).resize((96, 96))
            img = ImageTk.PhotoImage(img)

            self.images[name] = img

            btn = tk.Button(
                frame,
                image=img,
                command=lambda p=pid: self.choose(p)
            )
            btn.pack(side="left", padx=20)

    def choose(self, starter_id):
        self.selected_starter = starter_id
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.selected_starter