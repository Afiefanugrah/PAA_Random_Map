import tkinter as tk
from tkinter import Canvas, Scrollbar, Button, Frame, Label
from PIL import Image, ImageDraw, ImageTk
import random
import math

def delete():
    global image, tk_image, canvas, edge
    # Clean up previous images
    if 'image' in globals():
        del image
    if 'tk_image' in globals():
        del tk_image

    # Clear the canvas
    canvas.delete("all")


# Function to generate city map
def generate_city_map():
    global image, tk_image, canvas, edge

    scale = 10
    imageWidth = 150 * scale
    imageHeight = 150 * scale

    image = Image.new("RGB", (imageWidth, imageHeight), (69, 118, 46))
    draw = ImageDraw.Draw(image)

    def generateVertex(imageWidth, imageHeight, previousVertex, vertexList):
        global edge
        min_distance = min(imageWidth, imageHeight) / 15
        
        padding_x = imageWidth * 0.04
        padding_y = imageHeight * 0.04

        min_x = max(padding_x, min(previousVertex[0], imageWidth - previousVertex[0]) - (imageWidth / 2))
        max_x = min(imageWidth - padding_x, max(previousVertex[0], imageWidth - previousVertex[0]) + (imageWidth / 2))
        min_y = max(padding_y, min(previousVertex[1] - (50 * scale), imageHeight - previousVertex[1]) - (imageHeight / 2))
        max_y = min(imageHeight - padding_y, max(previousVertex[1] - (50 * scale), imageHeight - previousVertex[1]) + (imageHeight / 2))

        max_attempts = 1000
        attempts = 0
        while attempts < max_attempts:
            edge = random.choice(['x', 'y']) if len(vertexList) > 1 else ('x' if edge in ['bawah', 'atas'] else 'y')

            if edge == 'x':
                x = previousVertex[0]
                y = random.randint(min_y, max_y)
            else:
                x = random.randint(min_x, max_x)
                y = previousVertex[1]

            valid_point = True
            for v in vertexList:
                distance = math.sqrt((x - v[0])**2 + (y - v[1])**2)
                if distance < min_distance:
                    valid_point = False
                    break

            if valid_point:
                for i in range(len(vertexList) - 1):
                    x1, y1, _ = vertexList[i]
                    x2, y2, _ = vertexList[i + 1]
                    distance = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1)**2 + (x2 - x1)**2)
                    if distance < min_distance:
                        valid_point = False
                        break

            if valid_point:
                return x, y, edge
            attempts += 1
        # raise Exception("Failed to generate a valid vertex")
        return x, y, edge

    def firstVertex(imageWidth, imageHeight):
        global edge
        edge = random.choice(['atas', 'bawah', 'kiri', 'kanan'])
        
        if edge == 'atas':
            x = random.randint(0, imageWidth)
            y = 0
        elif edge == 'bawah':
            x = random.randint(0, imageWidth)
            y = imageHeight
        elif edge == 'kiri':
            x = 0
            y = random.randint(0, imageHeight)
        elif edge == 'kanan':
            x = imageWidth
            y = random.randint(0, imageHeight)
        return x, y

    def lastVertex(imageWidth, imageHeight, previousVertex):
        global edge
        edge = previousVertex[2]
        if edge == 'x':
            edge = 'y'
        elif edge == 'y':
            edge = 'x'

        if edge == 'x':
            x = previousVertex[0]
            y = imageHeight if previousVertex[1] > imageHeight / 1.75 else 0
        else:
            x = imageWidth if previousVertex[0] > imageWidth / 1.75 else 0
            y = previousVertex[1]

        return x, y, edge
    
    def find_nearest_road_coord(building_coord, road_coords):
        x, y = building_coord
        min_dist = float('inf')
        nearest_road_coord = None
        for road_coord in road_coords:
            road_x, road_y = road_coord
            dist = (x - road_x) ** 2 + (y - road_y) ** 2
            if dist < min_dist:
                min_dist = dist
                nearest_road_coord = road_coord
        return nearest_road_coord

    num_vertices = 17
    vertexList = []
    road_coords = set()
    previousVertex = firstVertex(imageWidth, imageHeight)
    vertexList.append(previousVertex + ('',))
    line_width = 28
    
    # Function to draw a circle at a vertex?
    def draw_circle(draw, vertex, diameter, fill):
        x, y = vertex[:2]
        radius = diameter // 2
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill)

    def draw_dashed_line(draw, start, end, dash_length=10, fill='black', width=1):
        x1, y1 = start[:2]
        x2, y2 = end[:2]
        total_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        dashes = int(total_length / dash_length)
        for i in range(dashes):
            start_x = x1 + (x2 - x1) * (i / dashes)
            start_y = y1 + (y2 - y1) * (i / dashes)
            end_x = x1 + (x2 - x1) * ((i + 0.5) / dashes)
            end_y = y1 + (y2 - y1) * ((i + 0.5) / dashes)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=fill, width=width)
        
    for _ in range(num_vertices - 2):
        nextVertex = generateVertex(imageWidth, imageHeight, previousVertex, vertexList)
        draw_circle(draw, previousVertex, line_width, (44, 44, 44))
        draw.line((previousVertex[0], previousVertex[1], nextVertex[0], nextVertex[1]), fill=(44, 44, 44), width=3*scale)
        draw_dashed_line(draw, previousVertex, nextVertex, dash_length=50, fill='white', width=3)

    
        # Save road coordinates?
        for x in range(min(previousVertex[0], nextVertex[0]), max(previousVertex[0], nextVertex[0]) + 1):
            for y in range(min(previousVertex[1], nextVertex[1]), max(previousVertex[1], nextVertex[1]) + 1):
                road_coords.add((x, y))
        
        previousVertex = nextVertex
        vertexList.append(nextVertex)

    endVertex = lastVertex(imageWidth, imageHeight, previousVertex)
    vertexList.append(endVertex)
    draw_circle(draw, previousVertex, line_width, (44, 44, 44))
    draw.line((previousVertex[0], previousVertex[1], endVertex[0], endVertex[1]), fill=(44, 44, 44), width=3*scale)
    draw_dashed_line(draw, previousVertex, endVertex, dash_length=50, fill='white', width=3)


    # Save end segment road coordinates
    for x in range(min(previousVertex[0], endVertex[0]), max(previousVertex[0], endVertex[0]) + 1):
        for y in range(min(previousVertex[1], endVertex[1]), max(previousVertex[1], endVertex[1]) + 1):
            road_coords.add((x, y))



    # Define the minimum distance between buildings
    min_distance_buildings = 20

    kanvas = [[False for _ in range(imageWidth)] for _ in range(imageHeight)]

    def is_area_free(x, y, width, height, min_distance, canvas, road_coords):
        for i in range(max(0, x - min_distance), min(imageWidth, x + width + min_distance)):
            for j in range(max(0, y - min_distance), min(imageHeight, y + height + min_distance)):
                if canvas[j][i] or (i, j) in road_coords:
                    return False
        return True
    
    
    def mark_area(x, y, width, height, canvas):
        for i in range(x, x + width):
            for j in range(y, y + height):
                canvas[j][i] = True

    def place_building_group(group_width, group_height, num_buildings, min_distance_buildings, occupied_coords, road_coords, imageWidth, imageHeight):
        placed_buildings = []
        attempts = 0
        max_attempts = 1000  # Limit the number of attempts to avoid infinite loops

        while len(placed_buildings) < num_buildings and attempts < max_attempts:
            x = random.randint(0, imageWidth - group_width)
            y = random.randint(0, imageHeight - group_height)

            if is_area_free(x, y, group_width, group_height, min_distance_buildings, occupied_coords, road_coords):
                mark_area(x, y, group_width, group_height, occupied_coords)
                placed_buildings.append((x, y, group_width, group_height))

            attempts += 1

        if attempts == max_attempts:
            raise Exception("Couldn't place buildings after 1000 attempts. Try reducing the number or size of buildings.")

        return placed_buildings
    

    # Place building groups

    group_a = place_building_group(300, 300, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_b = place_building_group(280, 170, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_c = place_building_group(120, 120, 3, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_d = place_building_group(230, 100, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_e = place_building_group(120, 120, 2, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_f = place_building_group(200, 130, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_g = place_building_group(200, 170, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_h = place_building_group(150, 130, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_i = place_building_group(300, 200, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_j = place_building_group(250, 150, 1, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)

    group_1 = place_building_group(100, 50, 5, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_2 = place_building_group(50, 30, 10, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_3 = place_building_group(20, 20, 20, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    group_4 = place_building_group(10, 20, 20, min_distance_buildings, kanvas, road_coords, imageWidth, imageHeight)
    
    # group_5 = place_building_group(10, 10, 200, min_distance_buildings, kanvas, road_coords)

    stadium_image = Image.open("texture/stadium.png").convert("RGBA")
    president_image = Image.open("texture/presidentialpalace.png").convert("RGBA")
    patung_image = Image.open("texture/patung.png").convert("RGBA")
    taman_image = Image.open("texture/taman.png").convert("RGBA")
    landmark_image = Image.open("texture/landmark.png").convert("RGBA")
    gereja_image = Image.open("texture/gereja.png").convert("RGBA")
    masjid_image = Image.open("texture/masjid.png").convert("RGBA")
    mall_image = Image.open("texture/mall.png").convert("RGBA")

    # Draw the buildings

    for building in group_a: # Staduim -> Purple
            x, y, width, height = building     
            stadium_resize = stadium_image.resize((width, height), Image.LANCZOS) 
            image.paste(stadium_resize, (x, y), stadium_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(154, 130, 251), outline=(0, 0, 0))

    for building in group_b: # Presidential palace -> Plain white
            x, y, width, height = building      
            president_resize = president_image.resize((width, height), Image.LANCZOS) 
            image.paste(president_resize, (x, y), president_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(230, 230, 230), outline=(0, 0, 0))  

    for building in group_c: # Patung -> Dark gold
            x, y, width, height = building    
            patung_resize = patung_image.resize((width, height), Image.LANCZOS)
            image.paste(patung_resize, (x, y), patung_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(171, 165, 35), outline=(0, 0, 0))  

    for building in group_d: # Taman -> Hijau
            x, y, width, height = building  
            taman_resize = taman_image.resize((width, height), Image.LANCZOS)    
            image.paste(taman_resize, (x, y), taman_resize) 
            # draw.rectangle([x, y, x + width, y + height], fill=(21, 189, 17), outline=(0, 0, 0))

    for building in group_e: # Landmark -> Turqoise
            x, y, width, height = building    
            landmark_resize = landmark_image.resize((width, height), Image.LANCZOS)   
            image.paste(landmark_resize, (x, y), landmark_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(18, 224, 204), outline=(0, 0, 0))

    for building in group_f: # Gereja -> Abu-abu ringan
            x, y, width, height = building      
            gereja_resize = gereja_image.resize((width, height), Image.LANCZOS) 
            image.paste(gereja_resize, (x, y), gereja_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(180, 180, 180), outline=(0, 0, 0))  

    for building in group_g: # Masjid -> Abu-abu ringan
            x, y, width, height = building  
            masjid_resize = masjid_image.resize((width, height), Image.LANCZOS)   
            image.paste(masjid_resize, (x, y), masjid_resize)  
            # draw.rectangle([x, y, x + width, y + height], fill=(180, 180, 180), outline=(0, 0, 0))    

    for building in group_h: # Bus Station -> Abu-abu sedang
            x, y, width, height = building      
            draw.rectangle([x, y, x + width, y + height], fill=(130, 130, 130), outline=(0, 0, 0))

    for building in group_i: # Mall -> Abu-abu gelap
            x, y, width, height = building      
            mall_resize = mall_image.resize((width, height), Image.LANCZOS) 
            image.paste(mall_resize, (x, y), mall_resize)
            # draw.rectangle([x, y, x + width, y + height], fill=(70, 70, 70), outline=(0, 0, 0))  

    for building in group_j: # Waterpark -> Biru tua
            x, y, width, height = building      
            draw.rectangle([x, y, x + width, y + height], fill=(146, 250, 237), outline=(0, 0, 0))          

    for building in group_1 + group_2 + group_3 + group_4:
        x, y, width, height = building

        # Find the nearest road coordinate
        building_center = (x + width // 2, y + height // 2)
        nearest_road = find_nearest_road_coord(building_center, road_coords)
        
        # Draw the little road line from the building to the nearest road?
        if nearest_road:
            road_x, road_y = nearest_road
                    
            # Determine the direction of the connection
            if abs(building_center[0] - road_x) > abs(building_center[1] - road_y):
                # Draw horizontal line first, then vertical
                intermediate_point = (road_x, building_center[1])
                draw.line([building_center, intermediate_point], fill=(44, 44, 44), width=5)
                draw.line([intermediate_point, nearest_road], fill=(44, 44, 44), width=5)
                
            elif abs(building_center[0] - road_x) < abs(building_center[1] - road_y):
                # Draw vertical line first, then horizontal
                intermediate_point = (building_center[0], road_y)
                draw.line([building_center, intermediate_point], fill=(44, 44, 44), width=5)
                draw.line([intermediate_point, nearest_road], fill=(44, 44, 44), width=5)
    
            
        # draw_dashed_line(draw, previousVertex, endVertex, dash_length=50, fill='white', width=3)
        draw.rectangle([x, y, x + width, y + height], fill=(0, 0, 255), outline=(0, 0, 0))
 
    tk_image = ImageTk.PhotoImage(image.convert("RGBA"))
    canvas.create_image(0, 0, anchor='nw', image=tk_image)
    canvas.config(scrollregion=canvas.bbox(tk.ALL))


def create_gui():
    global canvas
    global canvas
    def on_drag_start(event):
        canvas.scan_mark(event.x, event.y)

    def on_drag_move(event):
        canvas.scan_dragto(event.x, event.y, gain=1)

    def on_mouse_wheel(event):
        if event.state & 0x0001:  # Shift key is pressed
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        else:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_touchpad_scroll(event):
        canvas.yview_scroll(int(-1*(event.delta)), "units")

    # Initialize tkinter window
    root = tk.Tk()
    root.title("City Map Generator")

    # Frame for canvas and scrollbar
    frame = Frame(root)
    frame.grid(row=0, column=0)

    # Canvas widget for displaying image
    canvas = Canvas(frame, width=1200, height=700)  # Viewport size
    canvas.grid(row=0, column=0)

    # Scrollbars for canvas
    hbar = Scrollbar(frame, orient=tk.HORIZONTAL, command=canvas.xview)
    hbar.grid(row=1, column=0, sticky='we')
    vbar = Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    vbar.grid(row=0, column=1, sticky='ns')
    canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

    # Button to regenerate the image
    button = Button(root, text="Regenerate City", command=generate_city_map)
    button2 = Button(root, text="Reset", command=delete)
    button.grid(row=1, column=0)
    button2.grid(row=2, column=0)

    # Bind mouse events for dragging
    canvas.bind("<ButtonPress-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag_move)
    canvas.bind_all("<MouseWheel>", on_mouse_wheel)
    canvas.bind_all("<Shift-MouseWheel>", on_mouse_wheel)

    # Bind touchpad scrolling (Linux systems)
    canvas.bind_all("<Button-4>", on_touchpad_scroll)
    canvas.bind_all("<Button-5>", on_touchpad_scroll)

    # Generate initial city map
    generate_city_map()

    # Run the tkinter event loop
    root.mainloop()

# Call the function to create the GUI
create_gui()