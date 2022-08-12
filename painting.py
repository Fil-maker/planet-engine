from math import log2, sin
from random import random, randint

from PIL import Image


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
    return [[randint(0, 255) if value == 0 else value for _ in range(columns)] for _ in range(rows)]


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


def create_map(height: int, width: int, scales=3):
    levels = min(int(log2(height)), int(log2(width)), scales)
    compressions = [2 ** (levels - s) for s in range(0, levels)]
    amplitudes = [randint(-255, 255) for _ in range(levels)]
    phases = [randint(-180, 180) for _ in range(levels)]
    maps = [smooth_field(
        interpolate_field(
            create_field(height // compressions[l], width // compressions[l]),
            height, width), rounding=2) for l in range(levels)]
    outer_map = create_field(height, width, 1)
    for row in range(height):
        for col in range(width):
            for f in range(levels):
                outer_map[row][col] += amplitudes[f] * sin(phases[f] * maps[f][row][col])
    maxa = max(map(lambda a: max(a), outer_map))
    mina = min(map(lambda a: min(a), outer_map))
    outer_map = list(map(lambda a: list(map(lambda b: int((b - mina) * 255 / (maxa - mina)), a)), outer_map))
    return outer_map


if __name__ == '__main__':
    expand_coefficient = 4
    paint_size = paint_height, paint_width = 256, 256
    map_r, map_g, map_b = [
        interpolate_field(create_map(*paint_size, scales=3), to_height=paint_height * expand_coefficient, to_width=paint_width * expand_coefficient) for _
        in range(3)]
    im = Image.new("RGB", (paint_height * expand_coefficient, paint_width * expand_coefficient))
    for row in range(paint_height * expand_coefficient):
        for col in range(paint_width * expand_coefficient):
            im.putpixel((row, col), (map_r[row][col], map_g[row][col], map_b[row][col]))

    im.save("paint.png")