import random
from PIL import Image
from math import sin, log2, ceil
from painting import create_map


def get_alpha(row, col, mrows, mcols, size):
    center_distance = ((col - mcols / 2) ** 2 + (row - mrows / 2) ** 2) ** 0.5
    if center_distance <= size:
        return 255
    return 0


def get_color(number, highest):
    if number <= highest * 0.001:
        return (66, 170, 255)
    if number <= highest * 0.1:
        return (255, 255, 0)
    if number <= highest * 0.7:
        return (0, 153, 0)
    if number <= highest * 0.9:
        return (75, 75, 75)
    return (255, 255, 255)


def smooth_field(field, rounding=2):
    h, w = len(field), len(field[0])
    smoothed = []
    [smoothed.append([0 for _ in range(w)]) for _ in range(h)]
    for row in range(h):
        for col in range(w):
            s = 0
            for dr in range(-rounding, rounding + 1):
                for dc in range(-rounding, rounding + 1):
                    if dr != 0 and dc != 0:
                        s += field[(row + dr) % h][(col + dc) % w]
            smoothed[row][col] = int(s / ((2 * rounding + 1) ** 2 - 1))
    return smoothed


def create_field(rows, columns, value=0):
    return [[random.randint(0, 255) if value == 0 else value for _ in range(columns)] for _ in range(rows)]


def interpolate_linearly(av, ax, bv, bx, x):
    return int(av + (x - ax) * (bv - av) / (bx - ax))


def interpolate_field(field, to_height, to_width):
    outer_field = create_field(to_height, to_width, value=None)
    fh, fc = len(field), len(field[0])
    height_ratio, width_ratio = to_height // fh, to_width // fc
    for row in range(len(field)):
        for col in range(len(field[0])):
            outer_field[row * height_ratio][col * width_ratio] = field[row][col]
    for row in range(len(outer_field)):
        for col in range(len(outer_field[0])):
            if outer_field[row][col] is None:
                top, left = row // height_ratio, col // width_ratio
                right, bottom = (left + 1) % fc, (top + 1) % fh
                # if top > bottom and left > right:
                #     # bottom = (to_height - 1) // height_ratio
                #     print(1)
                outer_field[row][col] = interpolate_linearly(
                    interpolate_linearly(field[top][left], left, field[top][right], right, col / width_ratio), top,
                    interpolate_linearly(field[bottom][left], left, field[bottom][right], right, col / width_ratio),
                    bottom, row / height_ratio)
    return outer_field


# seed = random.random()
# # seed = 844, 706, 183, 656, 349
# # seed = 959
# random.seed(seed)
# print(seed)

def get_planet(radius, scales=3):
    diameter = radius * 2
    im = Image.new("RGBA", (diameter, diameter))
    planet_small_map = create_map(16, 16, scales)
    planet_size = 2**ceil(log2(diameter))
    planet_map = interpolate_field(planet_small_map, planet_size, planet_size)
    for row in range(diameter):
        for col in range(diameter):
            color = get_color(planet_map[row][col], 255)
            alpha = get_alpha(row, col, diameter, diameter, radius)
            im.putpixel((row, col), (*color, alpha))
    # im.save("map.png")
    return im
