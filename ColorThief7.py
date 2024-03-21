import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw
from colorthief import ColorThief
from tkinterdnd2 import TkinterDnD
import urllib.parse
import re
import math
import threading
import queue
import io

class PaletteApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Palette Extractor")

        self.canvas = tk.Canvas(self.master, width=800, height=800, relief="raised")
        self.canvas.pack()

        # Chargez l'image d'arrière-plan
        self.background_image = Image.open("dd.png") # Remplacez "your_background_image.png" par le nom de votre fichier image
        self.update_canvas_size()  # Ajoutez cette ligne pour initialiser l'image d'arrière-plan

        self.save_button = tk.Button(self.master, text="Enregistrer la palette", command=self.save_palette, state="disabled")
        self.save_button.pack()

        self.master.bind("<Configure>", self.update_canvas_size)
        self.canvas.drop_target_register('DND_Files')
        self.canvas.dnd_bind('<<Drop>>', self.drop)

    def drop(self, event):
        if event.data:
            self.filepath = event.widget.tk.splitlist(event.data)[0]
            self.process_thread = threading.Thread(target=self.process_image, args=(self.filepath,))
            self.process_thread.start()

    def process_image(self, filepath):
        self.image = Image.open(filepath)

        # Redimensionnement de l'image
        max_size = (1920, 1080)
        self.image.thumbnail(max_size)

        # Utilisation d'un fichier temporaire pour éviter d'écrire sur le disque
        with io.BytesIO() as temp_file:
            self.image.save(temp_file, format="PNG")
            temp_file.seek(0)
            color_thief = ColorThief(temp_file)
            self.palette = color_thief.get_palette(color_count=8, quality=10)

        self.create_result_image()
        self.update_canvas_size()

    def create_result_image(self):
        palette_height = int(self.image.width / 5)
        palette_height = min(palette_height, self.image.height // 3)

        self.result_image = Image.new("RGB", (self.image.width, self.image.height + palette_height), color=(255, 255, 255))
        self.result_image.paste(self.image, (0, 0))

        draw = ImageDraw.Draw(self.result_image)
        num_colors = len(self.palette)

        # Épaisseur de la bordure autour des tuiles
        border_thickness = max(1, int(self.image.width * 0.005))
        border_color = (255, 255, 255)  # Couleur de la bordure (blanc)

        # Arrondir les coins des rectangles
        corner_radius = max(1, int(self.image.width * 0.01))

        # Calculer l'espace entre les tuiles et les bordures gauche et droite
        space_between_tiles = border_thickness * 2
        total_space = space_between_tiles * (num_colors + 1)
        remaining_space = self.result_image.width - total_space
        rect_width = remaining_space // num_colors
        rect_height = palette_height - border_thickness * 2

        # Calculer les bordures gauche et droite pour centrer les tuiles
        left_right_border = space_between_tiles

        for i, color in enumerate(self.palette):
            x0 = left_right_border + i * (rect_width + space_between_tiles)
            y0 = self.image.height + border_thickness
            x1 = x0 + rect_width
            y1 = y0 + rect_height

            # Dessiner le rectangle avec la couleur de la bordure
            draw.rounded_rectangle([x0, y0, x1, y1], radius=corner_radius, fill=border_color)

            # Dessiner le rectangle avec la couleur de la palette à l'intérieur de la bordure
            draw.rounded_rectangle([x0 + border_thickness, y0 + border_thickness, x1 - border_thickness, y1 - border_thickness], radius=corner_radius - 2, fill=color)

    def update_canvas_size(self, event=None):

        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        bg_image = self.background_image.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.tk_bg_image = ImageTk.PhotoImage(bg_image)
        self.canvas.create_image(0, 0, image=self.tk_bg_image, anchor="nw")

        if hasattr(self, "result_image"):

            self.display_image = self.result_image.copy()
            self.display_image.thumbnail((canvas_width, canvas_height))

            self.tk_image = ImageTk.PhotoImage(self.display_image)
            image_width, image_height = self.display_image.size
            x = (canvas_width - image_width) // 2
            y = (canvas_height - image_height) // 2
            self.canvas.create_image(x, y, image=self.tk_image, anchor="nw")
            self.save_button.config(state="normal")

    def save_palette(self):
        if hasattr(self, "result_image"):
            file = filedialog.asksaveasfile(mode="wb", defaultextension=".jpg", filetypes=[("JPEG Files", "*.jpg"), ("All Files", "*.*")])
            if file:
                self.result_image.save(file, "JPEG", quality=95)  # La qualité peut être ajustée entre 1 et 95, 95 étant la meilleure qualité.
                file.close()

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PaletteApp(root)
    root.mainloop()