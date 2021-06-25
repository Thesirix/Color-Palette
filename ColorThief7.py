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

