import random
from PIL import Image, ImageDraw

scale = 10
size = 150 * scale

def divide_and_conquer(draw, x, y, width, height, min_size=70, max_size=500, blocks=None):
    if blocks is None:
        blocks = []

    if width <= max_size and height <= max_size:
        draw.rectangle([x, y, x + width, y + height], outline=(99, 99, 99), width = 15)
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

# Generate the city map and get the list of blocks
image, blocks = create_random_city_map(size)

# Define building groups as (size, count) where size is (width, height)
building_groups = [((100, 50), 15), ((50, 30), 35)]
building_groups = [((100, 50), 15), ((50, 30), 35)]

# Place the building groups within the blocks
image_with_buildings = place_building_groups(image, blocks, building_groups)

# Display the final image with buildings
image_with_buildings.show()
