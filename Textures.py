import random
from PIL import Image


def create_field(rows, columns, value=0):
    field = []
    [field.append([random.randint(0, 255) if value == 0 else 0 for _ in range(columns)]) for _ in range(rows)]
    return field


def interpolate_function(v1, v2, searching):
    return v1 * (1 - searching) + v2 * searching


def interpolate_field(field):
    h, w = len(field), len(field[0])
    interpolated = create_field(height, width, value=-1)
    for row in range(height):
        for col in range(width):
            r1, c1 = row // (height // h), col // (width // w)
            interpolated[row][col] = \
                interpolate_function(
                    interpolate_function(
                        field[r1][c1],
                        field[r1][(c1 + 1) % w],
                        col),
                    interpolate_function(
                        field[(r1 + 1) % h][c1],
                        field[(r1 + 1) % h][(c1 + 1) % w],
                        col),
                    row
                )
    return interpolated


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


size = width, height = 1024, 1024

im = Image.new("L", size)

texture_data = create_field(height, width, value=1)

texture_data_lv1 = smooth_field(create_field(height, width))
texture_data_lv2 = smooth_field(create_field(height // 2, width // 2))
texture_data_lv3 = smooth_field(create_field(height // 8, width // 8))
texture_data_lv4 = smooth_field(create_field(height // 16, width // 16))
texture_data_lv5 = smooth_field(create_field(height // 64, width // 64))

for row in range(height):
    for col in range(width):
        texture_data[row][col] = int(
            (
                    (
                            (
                                    (texture_data_lv1[row][col] + 3 * texture_data_lv2[row // 2][col // 2]) / 4 +
                                    3 * texture_data_lv3[row // 8][col // 8]) / 8 + 7 * texture_data_lv4[row // 16][
                                col // 16]) / 8) / 1)

# texture_data = (texture_data)
texture_data = interpolate_field(create_field(height//64, width//64))

for row in range(height):
    for col in range(width):
        im.putpixel((row, col), int(texture_data[row][col]))

im.save("test.png")
