from pathlib import Path
from simple_exersise import SimpleExercise
from rlbot.matchconfig.match_config import  PlayerConfig, Team
from rlbottraining.training_exercise import Playlist

def make_default_playlist() -> Playlist:
    team = Team.BLUE
    ex: SimpleExercise = SimpleExercise("Simple", team = 1 if team == Team.BLUE else -1)
    ex.match_config.player_configs = [
        PlayerConfig.bot_config(Path(__file__).absolute().parent / "simple_bot" / 'SimpleBot.cfg', team)
    ]
    return [ex]
