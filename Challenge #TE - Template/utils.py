from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.rng import SeededRandomNumberGenerator
import math


class Area:
    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        raise NotImplementedError()

    def is_in(self, point: Vector3) -> bool:
        raise NotImplementedError()

class Sphere(Area):
    def __init__(self, center: Vector3, radius: float):
        self.center: Vector3 = center
        self.radius: float = radius

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        phi: float = rng.random() * math.pi * 2
        theta: float = rng.random() * math.pi
        radius: float = rng.random() * self.radius

        offset: Vector3 = Vector3(r * math.sin(theta) * math.cos(phi), r * math.sin(theta) * math.sin(phi), r * math.cos(theta))
        return add(self.center, offset)

    def is_in(self, point: Vector3) -> bool:
        return magnitude(sub(point, self.center)) < self.radius

class VerticalCyl(Area):
    def __init__(self, center: Vector3, height: float, radius: float):
        self.center: Vector3 = center
        self.height: float = height
        self.radius: float = radius

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        offset: Vector3 = Vector3(math.cos(rng.random() * math.pi * 2) * self.radius, math.sin(rng.random() * math.pi * 2) * self.radius, rng.n11() * height)
        return add(self.center, offset)

    def is_in(self, point: Vector3) -> bool:
        zeroed: Vector3 = sub(point, self.center)
        in_circle: bool = magnitude(zeroed) < self.radius
        in_height: bool = zeroed.z > 0 and zeroed.z < self.height
        return in_circle and in_height

class RectPrism(Area):
    def __init__(self, center: Vector3, width: float, height: float, depth: float):
        self.center: Vector3 = center
        self.width: float = width
        self.height: float = height
        self.depth: float = depth

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        offset: Vector3 = Vector3(self.width/2 * rng.n11(), self.depth/2 * rng.n11(), self.height/2 * rng.n11())
        return add(self.center, offset)

    def is_in(self, point: Vector3) -> bool:
        zeroed: Vector3 = sub(point, self.center)
        return betwix(zeroed.x, self.width/2) and betwix(zeroed.y, self.depth/2) and betwix(zeroed.z, self.height/2)

def betwix(point: Vector3, value: float) -> bool:
    return point > value * -1 and point < value

def magnitude(vec: Vector3) -> float:
    return (vec.x**2 + vec.y**2 + vec.z**2)**0.5

def add(v1: Vector3, v2: Vector3):
    return Vector3(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def sub(v1: Vector3, v2: Vector3):
    return Vector3(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def rotator_from_dir(dir: Vector3):
    yaw = math.atan(dir.y/dir.x)
    pitch = math.asin(dir.z/magnitude(dir))
    if dir.x < 0:
        yaw = (yaw + math.pi) % (2 * math.pi)
    return Rotator(pitch, yaw, 0)
