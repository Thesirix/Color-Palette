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

