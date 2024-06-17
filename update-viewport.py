import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import random

scale = 10
size = 150 * scale

def divide_and_conquer(draw, x, y, width, height, min_size=70, max_size=500, blocks=None):
    if blocks is None:
        blocks = []

    if width <= max_size and height <= max_size:
        draw.rectangle([x, y, x + width, y + height], outline=(99, 99, 99), width=15)
        blocks.append((x, y, width, height))
        return blocks

    if width > max_size:
        split_width = random.randint(min_size, min(max_size, width - min_size))
        divide_and_conquer(draw, x, y, split_width, height, min_size, max_size, blocks)
        divide_and_conquer(draw, x + split_width, y, width - split_width, height, min_size, max_size, blocks)
    elif height > max_size:
        split_height = random.randint(min_size, min(max_size, height - min_size))
        divide_and_conquer(draw, x, y, width, split_height, min_size, max_size, blocks)
        divide_and_conquer(draw, x, y + split_height, width, height - split_height, min_size, max_size, blocks)
    
    return blocks

def create_random_city_map(size):
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    blocks = divide_and_conquer(draw, 0, 0, size, size)
    return image, blocks

def is_valid_placement(existing_buildings, new_x, new_y, new_width, new_height, min_distance=20):
    for (x, y, width, height) in existing_buildings:
        if not (new_x + new_width + min_distance <= x or 
                new_x >= x + width + min_distance or 
                new_y + new_height + min_distance <= y or 
                new_y >= y + height + min_distance):
            return False
    return True

def place_building_group(draw, blocks, group_size, building_count, existing_buildings, min_distance=20, border_spacing=30):
    for _ in range(building_count):
        placed = False

        while not placed:
            block = random.choice(blocks)
            x, y, block_width, block_height = block
            building_width, building_height = group_size

            if building_width + 2 * border_spacing <= block_width and building_height + 2 * border_spacing <= block_height:
                positions = []

                for bx in range(x + border_spacing, x + block_width - building_width - border_spacing + 1):
                    positions.append((bx, y + border_spacing))

                for bx in range(x + border_spacing, x + block_width - building_width - border_spacing + 1):
                    positions.append((bx, y + block_height - building_height - border_spacing))

                for by in range(y + border_spacing, y + block_height - building_height - border_spacing + 1):
                    positions.append((x + border_spacing, by))

                for by in range(y + border_spacing, y + block_height - building_height - border_spacing + 1):
                    positions.append((x + block_width - building_width - border_spacing, by))

                random.shuffle(positions)

                for building_x, building_y in positions:
                    if is_valid_placement(existing_buildings, building_x, building_y, building_width, building_height, min_distance):
                        draw.rectangle([building_x, building_y, building_x + building_width, building_y + building_height], outline="blue", fill="grey")
                        existing_buildings.append((building_x, building_y, building_width, building_height))
                        placed = True
                        break

def place_building_groups(image, blocks, building_groups):
    draw = ImageDraw.Draw(image)
    existing_buildings = []

    for group in building_groups:
        group_size, building_count = group
        place_building_group(draw, blocks, group_size, building_count, existing_buildings)

    return image

def create_image():
    image, blocks = create_random_city_map(size)
    building_groups = [((100, 50), 15), ((50, 30), 35)]
    image_with_buildings = place_building_groups(image, blocks, building_groups)
    return image_with_buildings

# Fungsi untuk mendapatkan nama file berikutnya yang belum ada
def rename_file(base_name="gambar_map", ext=".png"):
    index = 1
    while os.path.exists(f"{base_name}{index}{ext}"):
        index += 1
    return f"{base_name}{index}{ext}"

class Viewport(tk.Tk):
    def __init__(self):
        super().__init__()

        self.lebar = 1000
        self.tinggi = 730

        self.title("Generator Map")
        
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()

        newx = int((screenwidth / 2) - (self.lebar / 2))
        newy = int((screenheight / 2) - (self.tinggi / 2) - 50)

        self.geometry(f"{self.lebar}x{self.tinggi}+{newx}+{newy}")
        self.minsize(1000, 730)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        self.frame = tk.Frame(self.main_frame, width=950, height=650)
        self.frame.pack_propagate(False)
        self.frame.pack(pady=10, expand=True)

        self.canvas = tk.Canvas(self.frame, width=950, height=650, borderwidth=0)
        self.canvas.pack(fill="both", expand=True)

        self.image_id = None
        self.generate_map()
        
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        self.start_x = 0
        self.start_y = 0

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side="bottom", pady=10)

        self.button1 = tk.Button(self.button_frame, text="Map generated", command=self.button1_action)
        self.button2 = tk.Button(self.button_frame, text="Save Map", command=self.button2_action)
        self.button3 = tk.Button(self.button_frame, text="Zoom in", command=self.button3_action)
        self.button4 = tk.Button(self.button_frame, text="Zoom out", command=self.button4_action)
        self.button1.pack(side="left", padx=15)
        self.button2.pack(side="left", padx=5)
        self.button3.pack(side="right", padx=5)
        self.button4.pack(side="right", padx=15)

    def generate_map(self):
        if self.image_id is not None:
            self.canvas.delete(self.image_id)
        
        self.image = create_image()
        self.img = ImageTk.PhotoImage(self.image)
        self.image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_id))

    def save_map(self):
        if self.image:
            confirm = messagebox.askyesno("Save Map", "Apakah Anda ingin menyimpan peta?")
            if confirm:
                try:
                    filename = rename_file()
                    self.image.save(filename)
                    messagebox.showinfo("Success", f"Map saved successfully as {filename}!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save map: {e}")
        else:
            messagebox.showerror("Error", "No map generated yet!")
    
    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        self.canvas.move(self.image_id, dx, dy)

        self.start_x = event.x
        self.start_y = event.y

        self.canvas.config(scrollregion=self.canvas.bbox(self.image_id))

    def button1_action(self):
        self.generate_map()
        print("Map generated")

    def button2_action(self):
        self.save_map()
        print("Map saved")

    def button3_action(self):
        self.zoom(1.1)

    def button4_action(self):
        self.zoom(0.9)

    def zoom(self, factor):
        canvas_coords = self.canvas.coords(self.image_id)
        self.canvas.scale(self.image_id, canvas_coords[0], canvas_coords[1], factor, factor)
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_id))

def create_gui():
    app = Viewport()
    app.mainloop()

create_gui()
