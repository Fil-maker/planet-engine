import pygame
import random
from interpolation import get_planet


class Timer:

    def __init__(self, duration):
        self.duration = duration
        self.current_time = 0
        self.done = False
        self.func = None

    def set_func(self, func):
        self.func = func

    def update(self):
        self.current_time += time_to_frame
        if self.current_time >= self.duration:
            self.done = True
            if self.func is not None:
                self.func()

    def tick(self):
        if self.current_time >= self.duration:
            self.done = False
            self.current_time = 0


class PressingTimer(Timer):
    def tick(self):
        pass

    def press(self):
        if self.done:
            self.done = False
            self.current_time = 0
            return True
        return False


class LimitedSizeStack:

    def __init__(self, limit):
        self.limit = limit
        self.stack = []

    def append(self, unit):
        self.stack.append(unit)
        if len(self.stack) >= self.limit:
            self.stack.pop(0)


class Vector:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __truediv__(self, other):
        return Vector(self.x / other, self.y / other)

    def __mul__(self, other):
        return Vector(self.x * other, self.y * other)

    def get(self):
        return self.x, self.y

    @staticmethod
    def normalize(vector):
        distance = Vector.length(vector)
        return Vector(vector.x / distance, vector.y / distance)

    @staticmethod
    def length(vector):
        return (vector.x ** 2 + vector.y ** 2) ** 0.5


class Ball(pygame.sprite.Sprite):
    def __init__(self, mass, radius, color, start_point, path_color=None):
        pygame.sprite.Sprite.__init__(self)
        self.mass = mass
        self.radius = radius
        self.color = color
        self.position = start_point
        self.force = Vector()
        self.acceleration = Vector()
        self.velocity = Vector()
        self.path = LimitedSizeStack(PATH_LENGTH_SECONDS * FPS)
        if path_color is None:
            self.path_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.path_color = path_color
        image = get_planet(radius)
        mode = image.mode
        size = image.size
        data = image.tobytes()
        self.image = pygame.image.fromstring(data, size, mode)

    def calculate_force(self, balls):
        force = Vector()
        for ball in balls:
            direction = ball.position - self.position
            force += Vector.normalize(direction) * GRAVITY_CONSTANT * self.mass * ball.mass / Vector.length(
                direction) ** 2
        self.force = force

    def update(self, other_balls):
        self.acceleration = self.force / self.mass
        self.velocity += self.acceleration * time_to_frame
        self.position += self.velocity * time_to_frame
        self.path.append(self.position)
        for ball in other_balls:
            if Vector.length(ball.position - self.position) <= ball.radius + self.radius:
                self.velocity *= -1


def paint():
    screen.fill(pygame.Color("black"))
    if offset_object is not None:
        offset_vec = Vector(offset_object.position.x - width // 2, offset_object.position.y - height // 2)
        for ball in balls:
            path = ball.path.stack
            for point in range(1, len(path)):
                pygame.draw.line(screen, ball.path_color,
                                 (path[point - 1] - offset_vec - offset_object.position - basic_offset).get(),
                                 (path[point] - offset_vec - offset_object.position - basic_offset).get(), 3)
        for ball in balls:
            screen.blit(ball.image, (
                (ball.position - offset_object.position - basic_offset - offset_vec - Vector(ball.radius, ball.radius)).get()))
            # pygame.draw.circle(screen, ball.color, ((ball.position - offset_object.position - offset_vec).get()), ball.radius, width=2)
    else:
        for ball in balls:
            path = ball.path.stack
            for point in range(1, len(path)):
                pygame.draw.line(screen, ball.path_color, (path[point - 1] - basic_offset).get(),
                                 (path[point] - basic_offset).get(), 3)
        for ball in balls:
            screen.blit(ball.image, (
                (ball.position - basic_offset - Vector(ball.radius, ball.radius)).get()))
            # pygame.draw.circle(screen, ball.color, ball.position.get(), ball.radius)


def update_planets():
    if offset_object:
        offset = offset_object.position
        for ball in balls:
            ball.position -= offset
    for i in range(len(balls)):
        balls[i].calculate_force(balls[:i] + balls[i + 1:])
    for i in range(len(balls)):
        balls[i].update(balls[:i] + balls[i + 1:])


def process_keys():
    for key in pressed_keys:
        global basic_offset, offset_pointer, offset_object, balls
        if key == pygame.K_UP:
            basic_offset += Vector(0, -CAMERA_SPEED)
        if key == pygame.K_DOWN:
            basic_offset += Vector(0, CAMERA_SPEED)
        if key == pygame.K_LEFT:
            basic_offset += Vector(-CAMERA_SPEED, 0)
        if key == pygame.K_RIGHT:
            basic_offset += Vector(CAMERA_SPEED, 0)
        if key == pygame.K_KP_PLUS and change_focus.press() is True:
            offset_pointer = (offset_pointer + 1) % len(balls)
            for ball in balls:
                n_path = []
                # for point in ball.path.stack:
                #     if offset_object is not None:
                #         n_path.append(point + offset_object.position - balls[offset_pointer].position)
                ball.path.stack = n_path
            # if offset_object:
            #     basic_offset += Vector(offset_object.position.x - width // 2, offset_object.position.y - height // 2)
            offset_object = balls[offset_pointer]
            offset_object.path.stack = []
            # basic_offset -= Vector(offset_object.position.x - width // 2, offset_object.position.y - height // 2)
            basic_offset = Vector()


# Constants
GRAVITY_CONSTANT = 0.01
PATH_LENGTH_SECONDS = 7
CAMERA_SPEED = 25

size = width, height = 1900, 1000
FPS = 60
time_to_frame = 1000 / FPS
running = True
pressed_keys = []

offset_object = None
basic_offset = Vector()

pygame.init()
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

clock = pygame.time.Clock()
flip_timer = Timer(time_to_frame)
flip_timer.set_func(update_planets)
change_focus = PressingTimer(1000)
timers = [flip_timer, change_focus]

ball_green = Ball(40, 50, pygame.Color("green"), Vector(250, 0))
ball_red = Ball(200, 32, pygame.Color("red"), Vector(600, 0))
moon_of_red = Ball(15, 16, pygame.Color("white"), Vector(700, 0))
ball_blue = Ball(1000, 120, pygame.Color("blue"), Vector(0, 0))

ball_red.velocity += Vector(.0, -.15)
ball_green.velocity += Vector(.0, -.2)
moon_of_red.velocity += ball_red.velocity + Vector(.0, -0.15)

offset_pointer = 0
balls = [ball_red, ball_green, ball_blue, moon_of_red]
# offset_object = balls[2]
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.KEYDOWN:
            pressed_keys.append(event.key)
        if event.type == pygame.KEYUP:
            pressed_keys.remove(event.key)
        if event.type == pygame.WINDOWRESIZED:
            width, height = pygame.display.get_surface().get_size()
    for timer in timers:
        timer.update()
    process_keys()
    paint()
    for timer in timers:
        timer.tick()
    pygame.display.flip()
    clock.tick(FPS)
