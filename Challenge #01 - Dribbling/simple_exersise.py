from rlbot.utils.game_state_util import GameState, BoostState, BallState, CarState, Physics, Vector3, Rotator
from rlbot.utils.rendering.rendering_manager import RenderingManager
from rlbot.utils.structures.game_data_struct import GameTickPacket

from rlbottraining.training_exercise import TrainingExercise
from rlbottraining.rng import SeededRandomNumberGenerator
from rlbottraining.training_exercise import Playlist
from rlbottraining.grading.grader import Grader
from rlbottraining.grading.training_tick_packet import TrainingTickPacket
from rlbot.training.training import Pass, Fail

from dataclasses import field, dataclass

from utils import add, sub, magnitude
import utils

class SimpleGrader(Grader):
    def __init__(self):
        self.fail_area: utils.RectPrism = utils.RectPrism(Vector3(0, 0, 95/2), 10000, 10000, 95)
        self.dribble_sphere: utils.Sphere = utils.Sphere(Vector3(0, 0, 0), 300)
        self.reached = False
        self.max_speed: float = 0
        self.info: utils.Info = None

    def on_tick(self, training_packet: TrainingTickPacket):
        packet: GameTickPacket = training_packet.game_tick_packet
        my_car = packet.game_cars[0].physics
        team = packet.game_cars[0].team
        ball = packet.game_ball.physics
        self.dribble_sphere.center = my_car.location
        if self.info == None:
            self.info: utils.Info = utils.Info(team, packet)
        self.info.update(packet)
        #Keep track of the balls max speed for score
        if magnitude(my_car.velocity) > self.max_speed:
            self.max_speed = magnitude(my_car.velocity)
        #Fail if ball is rolling on the ground
        if self.fail_area.is_in(ball.location) and abs(ball.velocity.z) < 10:
            return ScoredFail(0)
        #Fail if we've reached the ball but then thrown it away
        if self.dribble_sphere.is_in(ball.location):
            self.reached = True
        elif self.reached:
            return ScoredFail(0)
        #Fail if we've put it in our own net
        if self.info.scored_enemy:
            return ScoredFail(0)
        #Pass if we score on the enemy net
        if self.info.scored_me:
            return ScoredPass(self.max_speed)


    def render(self, renderer: RenderingManager):
        pass

@dataclass
class SimpleExercise(TrainingExercise):
    team: int = field(default_factory=int)
    grader: Grader = field(default_factory=SimpleGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        car_spawn_area: utils.Area = utils.RectPrism(Vector3(0, 0, 17), 8000, 8000, 0)
        ball_spawn_area: utils.Area = utils.RectPrism(Vector3(0, 0, 1000), 8000, 8000, 400)
        ball_velocity_area: utils.Area = utils.Sphere(Vector3(0, 0, 0), 600)
        ball_loc: Vector3 = ball_spawn_area.random_point_inside(rng)
        car_loc: Vector3 = car_spawn_area.random_point_inside(rng)
        return GameState(
            ball=BallState(physics=Physics(
                location=ball_loc,
                velocity=ball_velocity_area.random_point_inside(rng),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=car_loc,
                        rotation=utils.rotator_from_dir(sub(ball_loc, car_loc)),
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    boost_amount=100),
            },
            boosts={i: BoostState(0) for i in range(34)},
        )

class ScoredPass(Pass):
    def __init__(self, score = 0):
        self.score: float = score
    def __repr__(self):
        return "Score of: " + str(self.score)

class ScoredFail(Pass):
    def __init__(self, score = 0):
        self.score: float = score
    def __repr__(self):
        return "Score of: " + str(self.score)
