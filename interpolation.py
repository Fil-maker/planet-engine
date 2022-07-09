import random
from PIL import Image
from math import sin
from painting import create_map


def get_alpha(row, col, mrows, mcols, size):
    center_distance = ((col - mcols / 2) ** 2 + (row - mrows / 2) ** 2) ** 0.5
    if center_distance <= size:
        return 255
    return 0


def get_color(number, highest):
    if number <= highest * 0.001:
        return (66, 170, 255)
    if number <= highest * 0.06:
        return (255, 255, 0)
    if number <= highest * 0.2:
        return (0, 153, 0)
    if number <= highest * 0.4:
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

def get_planet(height, width, scales=4):
    planet_map = create_map(height, width, scales)
    amplitudes = a1, a2, a3, a4 = [random.randint(0, 255) for _ in range(4)]
    phases = b1, b2, b3, b4 = [random.randint(-180, 180) for _ in range(4)]
    size = height // 2, width // 2
    size2 = height, width
    compressions = (16, 8, 4, 4)
    # print(amplitudes, phases)

    texture = create_field(*size)

    field_lv1 = create_field(width // compressions[0], height // compressions[0])
    field_lv1 = interpolate_field(field_lv1, *size)

    field_lv2 = create_field(width // compressions[1], height // compressions[1])
    field_lv2 = interpolate_field(field_lv2, *size)

    field_lv3 = create_field(width // compressions[2], height // compressions[2])
    field_lv3 = interpolate_field(field_lv3, *size)

    field_lv4 = create_field(width // compressions[3], height // compressions[3])
    field_lv4 = interpolate_field(field_lv4, *size)

    for row in range(len(texture)):
        for col in range(len(texture[0])):
            texture[row][col] = (a1 * (sin(b1 * field_lv1[row][col]) + a2 * sin(b2 * field_lv2[row][col]) + a3 * sin(
                b3 * field_lv3[row][col]) + a4 * sin(b4 * field_lv4[row][col]))) / 255

    # texture = smooth_field(texture, rounding=3)
    highest = max(map(lambda a: max(a), texture))
    print(highest)

    im = Image.new("RGBA", size2)

    out = smooth_field(interpolate_field(texture, *size2))
    # for row in range(len(texture)):
    #     for col in range(len(texture[0])):
    #         im.putpixel((row, col), get_color(texture[row][col]))
    for row in range(len(out)):
        for col in range(len(out[0])):
            color = get_color(out[row][col])
            alpha = get_alpha(row, col, *size2, 32)
            im.putpixel((row, col), (*color, alpha))
    return im
    im.save("map.png")
