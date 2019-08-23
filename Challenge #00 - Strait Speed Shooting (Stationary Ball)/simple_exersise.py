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

@dataclass
class SimpleGrader(Grader):
    def __init__(self, timer = 10):
        self.timer = 10
        self.time = None
        self.score_me = None
        self.score_enemy = None

    def on_tick(self, training_packet: TrainingTickPacket):
        packet: GameTickPacket = training_packet.game_tick_packet
        my_car = packet.game_cars[0].physics
        team = packet.game_cars[0].team
        ball = packet.game_ball.physics
        # print("Rotation", my_car.rotation)
        if self.time == None:
            self.time = packet.game_info.seconds_elapsed
        if self.score_me == None:
            self.score_me = packet.teams[team].score
        if self.score_enemy == None:
            self.score_enemy = packet.teams[(team - 1)*-1].score
        if packet.game_info.seconds_elapsed - self.time > self.timer:
            return ScoredFail(-2000)
        if self.score_me < packet.teams[team].score:
            return ScoredPass(score = magnitude(ball.velocity))
        if self.score_enemy < packet.teams[(team - 1)*-1].score:
            return ScoredFail(-2000)
        return None

    def render(self, renderer: RenderingManager):
        pass

@dataclass
class SimpleExercise(TrainingExercise):
    team: int = field(default_factory=int)
    grader: Grader = field(default_factory=SimpleGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:
        enemy_goal_center: Vector3 = Vector3(0, 5120 * self.team, 93)
        car_spawn_block: utils.Area = utils.RectPrism(Vector3(0, 0, 17), 8000, 0, 8000)
        car_loc: Vector3 = car_spawn_block.random_point_inside(rng)
        car_facing: Rotator = utils.rotator_from_dir(sub(enemy_goal_center, car_loc))
        relative: Vector3 = sub(enemy_goal_center, car_loc)
        #Spawn the ball halfway between us and the enemy goal
        ball_loc: Vector3 = add(car_loc, Vector3(relative.x/2, relative.y/2, relative.z/2))
        ball_loc.z = 93

        return GameState(
            ball=BallState(physics=Physics(
                location=ball_loc,
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=car_loc,
                        rotation=car_facing,
                        velocity=Vector3(0, 0, 0),
                        angular_velocity=Vector3(0, 0, 0)),
                    boost_amount=33),
            },
            boosts={i: BoostState(0) for i in range(34)},
        )

class ScoredPass(Pass):
    def __init__(self, score = 0):
        self.score: float = score
    def __repr__(self):
        return "Score of" + str(self.score)

class ScoredFail(Pass):
    def __init__(self, score = 0):
        self.score: float = score
    def __repr__(self):
        return "Score of" + str(self.score)
