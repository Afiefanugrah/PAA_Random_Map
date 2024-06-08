import random
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import Canvas, Scrollbar, Button, Frame

background_imageries = ["texture/grass1.png", "texture/grass2.png", "texture/grass3.png", "texture/grass4.png", "texture/grass5.png",
                        "texture/grass6.png", "texture/grass7.png", "texture/grass8.png", "texture/grass9.png", "texture/grass10.png",
                        "texture/grass11.png" ]

building_textures = [
                     "texture/stadium.png",
                     "texture/taman.png",
                     "texture/rumah_1.png",
                     "texture/rumah_2.png",
                     "texture/rumah_3.png",
                     "texture/tumbuhan.png",
                     "texture/rumah_4.png",
                     "texture/rumah_5.png",
                     "texture/rumah_6.png",
                     "texture/rumah_7.png",
                     "texture/rumah_8.png",
                     "texture/rumah_9.png",
                     "texture/rumah_10.png",
                     "texture/rumah_11.png",
                     "texture/rumah_12.png",
                     "texture/rumah_13.png",
    ]

road_textures = ["image/asphalt2.jpg", "texture/road2.png", "texture/trotoar1.png"]

tree_and_rock_textures = ["texture/tree1.png", "texture/tree2.png", "texture/tree3.png"]  # Add tree and rock textures





global tk_image  # Keep a reference to avoid garbage collection
scale = 10
size = 150 * scale



def divide_and_conquer(draw, x, y, width, height, min_size=70, max_size=650, blocks=None, borders=None):
    if blocks is None:
        blocks = []
    
    if borders is None:
        borders = []

    if width <= max_size and height <= max_size:
        draw.rectangle([x, y, x + width, y + height])
        blocks.append((x, y, width, height))

        # Store border coordinates
        top_border = [(i, y) for i in range(x, x + width + 1)]
        bottom_border = [(i, y + height) for i in range(x, x + width + 1)]
        left_border = [(x, j) for j in range(y, y + height + 1)]
        right_border = [(x + width, j) for j in range(y, y + height + 1)]

        borders.extend([top_border, bottom_border, left_border, right_border])
        return blocks, borders

    if width > max_size:
        split_width = random.randint(min_size, min(max_size, width - min_size))
        divide_and_conquer(draw, x, y, split_width, height, min_size, max_size, blocks, borders)
        divide_and_conquer(draw, x + split_width, y, width - split_width, height, min_size, max_size, blocks, borders)
    elif height > max_size:
        split_height = random.randint(min_size, min(max_size, height - min_size))
        divide_and_conquer(draw, x, y, width, split_height, min_size, max_size, blocks, borders)
        divide_and_conquer(draw, x, y + split_height, width, height - split_height, min_size, max_size, blocks, borders)
    
    return blocks, borders

def create_random_city_map(size):
    background_image = Image.open("image/rumput.png").resize((size, size)).convert("RGBA")
    image = background_image.copy()
    draw = ImageDraw.Draw(image)
    blocks, borders = divide_and_conquer(draw, 0, 0, size, size)
    return image, blocks, borders


def is_valid_placement(existing_elements, new_x, new_y, new_width, new_height, min_distance=15):
    for (x, y, width, height) in existing_elements:
        if not (new_x + new_width + min_distance <= x or 
                new_x >= x + width + min_distance or 
                new_y + new_height + min_distance <= y or 
                new_y >= y + height + min_distance):
            return False
    return True

def place_building_group(image, draw, blocks, group_size, building_count, texture, existing_buildings, min_distance=15, border_spacing=25):
    for _ in range(building_count):
        placed = False

        while not placed:
            block = random.choice(blocks)
            x, y, block_width, block_height = block
            building_width, building_height = group_size

            # Ensure the building fits within the block and respects the border_spacing
            if building_width + 2 * border_spacing <= block_width and building_height + 2 * border_spacing <= block_height:
                # Calculate potential positions along the borders
                positions = []

                # Along the top border
                for bx in range(x + border_spacing, x + block_width - building_width - border_spacing + 1):
                    positions.append((bx, y + border_spacing))

                # Along the bottom border
                for bx in range(x + border_spacing, x + block_width - building_width - border_spacing + 1):
                    positions.append((bx, y + block_height - building_height - border_spacing))

                # Along the left border
                for by in range(y + border_spacing, y + block_height - building_height - border_spacing + 1):
                    positions.append((x + border_spacing, by))

                # Along the right border
                for by in range(y + border_spacing, y + block_height - building_height - border_spacing + 1):
                    positions.append((x + block_width - building_width - border_spacing, by))

                # Randomize the order of positions to avoid clustering
                random.shuffle(positions)

                for building_x, building_y in positions:
                    if is_valid_placement(existing_buildings, building_x, building_y, building_width, building_height, min_distance):
                        # Create a mask for the building texture
                        texture_resized = texture.resize((building_width, building_height))
                        image.paste(texture_resized, (building_x, building_y), texture_resized)
                        existing_buildings.append((building_x, building_y, building_width, building_height))
                        placed = True
                        break


def place_building_groups(image, blocks, building_groups, existing_buildings):
    draw = ImageDraw.Draw(image)

    for group in building_groups:
        group_size, building_count, texture = group
        place_building_group(image, draw, blocks, group_size, building_count, texture, existing_buildings)
        
    return image

def draw_road_lanes2(image, borders, road_texture):
    draw = ImageDraw.Draw(image)
    texture = road_texture.resize((50, 50))
    
    for border in borders:
        for i in range(0, len(border), 50):
            x, y = border[i]
            image.alpha_composite(texture, (x - 25, y - 25))
    
    return image

def draw_road_lanes(image, borders, road_texture):
    draw = ImageDraw.Draw(image)
    texture = road_texture.resize((36, 36))
    
    for border in borders:
        for i in range(0, len(border), 36):
            x, y = border[i]
            image.alpha_composite(texture, (x - 17, y - 17))
    
    return image

def draw_dotted_road_lanes(image, borders, dot_length=20, gap_length=30, reduction=25):
    draw = ImageDraw.Draw(image)
    processed_coords = set()  # Set to keep track of processed coordinates
    
    for border in borders:
        if len(border) <= 2 * reduction:
            continue  # Skip borders that are too short to be reduced

        # Adjust the border to reduce the start and end by the reduction value
        adjusted_border = border[reduction:-reduction]
        
        # Draw the dotted line
        for i in range(0, len(adjusted_border) - 1, dot_length + gap_length):
            # Calculate the end of the dot segment, ensuring it doesn't exceed the adjusted border length
            end_index = min(i + dot_length, len(adjusted_border) - 1)
            
            # Check if the current segment has been processed
            segment = tuple(adjusted_border[i:end_index])
            if not any(coord in processed_coords for coord in segment):
                draw.line(segment, fill=(255, 255, 255), width=3)
                processed_coords.update(segment)  # Mark this segment as processed

    return image


def place_trees_and_rocks(image, blocks, textures, existing_elements, tree_rock_count=70, min_distance=20):
    draw = ImageDraw.Draw(image)
    for _ in range(tree_rock_count):
        placed = False
        while not placed:
            block = random.choice(blocks)
            x, y, block_width, block_height = block
            texture = random.choice(textures)
            new_width, new_height = texture.size
            new_x = random.randint(x, x + block_width - new_width)
            new_y = random.randint(y, y + block_height - new_height)
            
            if is_valid_placement(existing_elements, new_x, new_y, new_width, new_height, min_distance):
                image.alpha_composite(texture, (new_x, new_y))
                existing_elements.append((new_x, new_y, new_width, new_height))
                placed = True
    return image

def create_image():
    # Generate the city map and get the list of blocks
    image, blocks, borders = create_random_city_map(size)

    # Load building textures
    textures = [Image.open(texture_path).convert("RGBA") for texture_path in building_textures]

    # Load tree and rock textures
    tree_rock_textures = [Image.open(texture_path).convert("RGBA") for texture_path in tree_and_rock_textures]

    road_texture = Image.open(road_textures[0]).convert("RGBA")  # Change to desired road texture
    sidewalk_texture = Image.open(road_textures[2]).convert("RGBA")  # Change to desired road texture

    # Define building groups as (size, count) where size is (width, height)
    building_groups = [
                    ((400, 150), 1, textures[1]),
                    ((220, 250), 1, textures[0]),
                    ((100, 50), 15, textures[2]),
                    ((50, 30), 35, textures[3]),
                    ((20, 20), 20, textures[4]),
                    ((50, 30), 15, textures[6]),
                    ((40, 40), 10, textures[7]),
                    ((52, 30), 7, textures[8]),
                    ((70, 40), 7, textures[9]),
                    ((80, 40), 5, textures[10]),
                    ((100, 100), 3, textures[11]),
                    ((100, 60), 5, textures[12]),
                    ((120, 100), 4, textures[14]),
                    ((120, 100), 3, textures[15]),
                    ]

    existing_elements = []
    
    # Place the building groups within the blocks
    image_with_buildings = place_building_groups(image, blocks, building_groups, existing_elements)

    # Draw the road lanes
    image_with_roads2 = draw_road_lanes2(image_with_buildings, borders, sidewalk_texture) 
    image_with_roads = draw_road_lanes(image_with_roads2, borders, road_texture)
    image_with_dotted_roads = draw_dotted_road_lanes(image_with_roads, borders)  # Draw the dotted road lanes

    # Place trees and rocks
    image_with_trees_and_rocks = place_trees_and_rocks(image_with_dotted_roads, blocks, tree_rock_textures, existing_elements)

    return image_with_trees_and_rocks

import tkinter as tk
from PIL import Image, ImageTk

class Viewport(tk.Tk):
    def __init__(self):
        super().__init__()

        self.lebar = 1000
        self.tinggi = 730

        self.title("Generator Map")
        
        # Mendapatkan lebar dan tinggi layar
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()

        # Menghitung posisi koordinat x dan y
        newx = int((screenwidth / 2) - (self.lebar / 2))
        newy = int((screenheight / 2) - (self.tinggi / 2) - 50)

        # Mengatur ukuran dan posisi jendela
        self.geometry(f"{self.lebar}x{self.tinggi}+{newx}+{newy}")
        self.minsize(1000, 730)  # Atur ukuran maksimum
        # self.resizable(0, 0)

        # Membuat frame utama untuk gambar dan tombol
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Membuat frame dengan ukuran tetap untuk gambar
        self.frame = tk.Frame(self.main_frame, width=950, height=650)
        self.frame.pack_propagate(False)  # Mencegah frame meresize sesuai ukuran canvas
        self.frame.pack(pady=10, expand=True)  # Menambahkan padding untuk estetika dan expand

        # Membuat widget canvas di dalam frame
        self.canvas = tk.Canvas(self.frame, width=950, height=650, borderwidth=0)
        self.canvas.pack(fill="both", expand=True)

        # Membuat gambar dan menambahkannya ke canvas
        self.image_id = None
        self.zoom_factor = 1.0  # Initialize zoom factor
        self.generate_map()
        
        # Mengonfigurasi scroll region
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

        # Mengikat event mouse untuk dragging
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        # Variabel untuk menyimpan posisi mouse
        self.start_x = 0
        self.start_y = 0

        # Membuat frame untuk tombol di bagian bawah
        self.button_frame = tk.Frame(self.main_frame)
        # self.button_frame.pack(pady=10, expand=False)
        self.button_frame.pack(side="bottom", pady=10)
        # self.button_frame.pack(side="bottom", pady=10, fill="x")

        # Menambahkan tombol ke dalam frame tombol
        self.button1 = tk.Button(self.button_frame, text="Map generated", command=self.button1_action)
        self.button2 = tk.Button(self.button_frame, text="Save Map", command=self.button2_action)
        self.button3 = tk.Button(self.button_frame, text="Zoom in", command=self.button3_action)
        self.button4 = tk.Button(self.button_frame, text="Zoom out", command=self.button4_action)
        self.button1.pack(side="left", padx=15)
        self.button2.pack(side="left", padx=5)
        self.button3.pack(side="right", padx=5)
        self.button4.pack(side="right", padx=15)

    def generate_map(self):
        '''Menghasilkan peta kota dan menambahkannya ke canvas'''
        if self.image_id is not None:
            self.canvas.delete(self.image_id)
        
        self.image = create_image()
        self.display_image(self.image)

    def display_image(self, image):
        '''Display the image on the canvas'''
        self.img = ImageTk.PhotoImage(image)
        self.image_id = self.canvas.create_image(0, 0, anchor='nw', image=self.img)
        
        # Mengonfigurasi scroll region
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_id))

    def save_map(self):
        '''Simpan peta sebagai file gambar'''
        if self.image:
            self.image.save("map.png")  # Implementasi sederhana untuk menyimpan gambar
        else:
            raise Exception("Error", "No map generated yet!")
    
    def on_button_press(self, event):
        '''Menyimpan posisi awal mouse saat mulai dragging'''
        self.start_x = event.x
        self.start_y = event.y

    def on_mouse_drag(self, event):
        '''Menghandle dragging gambar'''
        dx = event.x - self.start_x
        dy = event.y - self.start_y

        self.canvas.move(self.image_id, dx, dy)

        self.start_x = event.x
        self.start_y = event.y

        # Memperbarui scroll region untuk menyertakan gambar yang sudah dipindahkan
        self.canvas.config(scrollregion=self.canvas.bbox(self.image_id))

    def button1_action(self):
        '''Aksi untuk tombol 1'''
        self.generate_map()
        print("Map generated")

    def button2_action(self):
        '''Aksi untuk tombol 2'''
        self.save_map()
        print("Button 2 clicked")

    def button3_action(self):
        '''Aksi untuk tombol 3'''
        self.zoom_factor *= 1.2  # Increase zoom factor by 20%
        self.zoom_image()
        print("Button 3 clicked")

    def button4_action(self):
        '''Aksi untuk tombol 4'''
        self.zoom_factor /= 1.2  # Decrease zoom factor by 20%
        self.zoom_image()
        print("Button 4 clicked")

    def zoom_image(self):
        '''Zoom the image based on the current zoom factor'''
        width, height = self.image.size
        new_size = int(width * self.zoom_factor), int(height * self.zoom_factor)
        resized_image = self.image.resize(new_size, Image.LANCZOS)
        self.display_image(resized_image)

def create_gui():
    app = Viewport()
    app.mainloop()

# Call the function to create the GUI
create_gui()

