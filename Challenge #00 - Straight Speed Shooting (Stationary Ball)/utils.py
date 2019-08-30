from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, Physics, Vector3, Rotator
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbot.utils.structures.game_data_struct import GameTickPacket
import math


class Area:
    def __init__(self):
        self.volume = 0

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        raise NotImplementedError()

    def is_in(self, point: Vector3) -> bool:
        raise NotImplementedError()

class Sphere(Area):
    def __init__(self, center: Vector3, radius: float):
        self.center: Vector3 = center
        self.radius: float = radius
        self.volume: float = (4*math.pi*self.radius**3)/3

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
        self.circle_area: float = (self.radius**2) * math.pi
        if self.circle_area == 0:
            self.volume: float = self.height
        elif self.height == 0:
            self.volume: float = self.circle_area
        else:
            self.volume: float = self.circle_area * self.height

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        offset: Vector3 = Vector3(math.cos(rng.random() * math.pi * 2) * self.radius, math.sin(rng.random() * math.pi * 2) * self.radius, rng.n11() * height)
        return add(self.center, offset)

    def is_in(self, point: Vector3) -> bool:
        zeroed: Vector3 = sub(point, self.center)
        in_circle: bool = magnitude(zeroed) < self.radius
        in_height: bool = zeroed.z > 0 and zeroed.z < self.height
        return in_circle and in_height

class RectPrism(Area):
    def __init__(self, center: Vector3, width: float, depth: float, height: float):
        self.center: Vector3 = center
        self.width: float = width
        self.height: float = height
        self.depth: float = depth
        self.volume = 1
        if self.depth != 0:
            self.volume *= self.depth
        if self.width != 0:
            self.volume *= self.width
        if self.height != 0:
            self.volume *= self.height

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        offset: Vector3 = Vector3(self.width/2 * rng.n11(), self.depth/2 * rng.n11(), self.height/2 * rng.n11())
        return add(self.center, offset)

    def is_in(self, point: Vector3) -> bool:
        zeroed: Vector3 = sub(point, self.center)
        return betwix(zeroed.x, self.width/2) and betwix(zeroed.y, self.depth/2) and betwix(zeroed.z, self.height/2)

class CompositeArea(Area):
    def __init__(self, area: Area):
        #Volume is highly approximate
        self.areas = [area]
        self.negative = []
        self.probs = [1]
        self._volume = area.volume
        self.volume = area.volume

    def add(self, area: Area):
        self.areas.append(area)
        self._volume += area.volume
        self.volume += area.volume
        self.probs = []
        for ar in self.areas:
            self.probs.append(ar.volume/self.volume)

    def subtract(self, area: Area):
        self.negative.append(area)
        self.volume -= area.volume

    def is_in_positive(self, point: Vector3) -> bool:
        for area in self.areas:
            if area.is_in(point):
                return True
        return False

    def is_in_negative(self, point: Vector3) -> bool:
        for area in self.negative:
            if area.is_in(point):
                return True
        return False

    def is_in(self, point: Vector3) -> bool:
        return not self.is_in_negative(point) and self.is_in_positive(point)

    def random_point_inside(self, rng: SeededRandomNumberGenerator) -> Vector3:
        # Not gaurenteed to be even distrobution because volume is approximate
        area: Area = rng.choices(self.areas, self.probs)[0]
        point: Vector3 = area.random_point_inside(rng)
        while not self.is_in(point):
            area = rng.choices(self.areas, self.probs)[0]
            point = area.random_point_inside(rng)
        return point

class Info:
    def __init__(self, team: int):
        self.team: int = team
        self.score_me: int = 0
        self.score_enemy: int = 0
        self.scored_me: bool = False
        self.scored_enemy: bool = False

    def update(self, packet: GameTickPacket):
        if self.score_enemy < packet.teams[(self.team - 1)*-1].score:
            self.score_enemy: int = packet.teams[(self.team - 1)*-1].score
            self.scored_enemy: bool = True
        else:
            self.scored_enemy: bool = False

        if self.score_me < packet.teams[self.team].score:
            self.scored_me: bool = True
            self.score_me: int = packet.teams[self.team].score
        else:
            self.scored_me: bool = False

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
