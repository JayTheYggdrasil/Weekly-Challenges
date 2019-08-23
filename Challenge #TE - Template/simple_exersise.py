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
        pass

    def on_tick(self, training_packet: TrainingTickPacket):
        packet: GameTickPacket = training_packet.game_tick_packet
        my_car = packet.game_cars[0].physics
        team = packet.game_cars[0].team
        ball = packet.game_ball.physics
        pass

    def render(self, renderer: RenderingManager):
        pass

@dataclass
class SimpleExercise(TrainingExercise):
    team: int = field(default_factory=int)
    grader: Grader = field(default_factory=SimpleGrader)

    def make_game_state(self, rng: SeededRandomNumberGenerator) -> GameState:

        return GameState(
            ball=BallState(physics=Physics(
                location=Vector3(0, 0, 400),
                velocity=Vector3(0, 0, 0),
                angular_velocity=Vector3(0, 0, 0))),
            cars={
                0: CarState(
                    physics=Physics(
                        location=Vector3(0, 0, 20),
                        rotation=Rotator(0, 0, 0),
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
