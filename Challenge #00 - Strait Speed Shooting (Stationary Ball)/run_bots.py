from rlbot.matchconfig.match_config import  PlayerConfig, Team
from rlbottraining.exercise_runner import run_playlist
from rlbottraining.training_exercise import Playlist
from simple_exersise import SimpleExercise
from rlbot.training.training import Pass
from typing import List, Tuple, Dict
from pathlib import Path
import random
import sys
import os

def run_bots():
    seed: int = int(input("Choose a Seed: "))
    random.seed(seed)
    runs = 2
    bots: List[Tuple[str]] = find_bots()
    with open("scoreboard.txt", "w+") as scorefile:
        print("file opened")
        scoreboard: Dict[str, float] = dict()
        for run in range(runs):
            seed = random.randint(0, 9999)
            print("Run number: ", run)
            team = round((run+1)/runs)*2 - 1 #-1 (orange): first half, 1 (blue): second half
            play = make_playlist(bots, team)
            results_generator = run_playlist(play, seed = seed)
            for bot_info, result in zip(bots, results_generator):
                if not bot_info[0] in scoreboard:
                    scoreboard[bot_info[0]] = 0
                scoreboard[bot_info[0]] += result.grade.score
        for bot_name, path in bots:
            entry = bot_name + " = " + str(scoreboard[bot_name]/runs)
            print(bot_name + " got an average score of:", scoreboard[bot_name]/runs)
            scorefile.write(entry + "\n")

def find_bots() -> List[Tuple[str, str]]:
    """
    Searches the current directory for any bot cfg files (cfg files that are not
    named appearance.cfg) and returns a list of (bot_name, path_to_bot_folder)
    """
    bots: List[Tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(os.path.dirname(__file__)):
        for file in filenames:
            if file.endswith(".cfg") and str(file) != "appearance.cfg":
                bot_name: str = str(file)[:-4]
                path: str = dirpath + "/" +  str(file)
                print("Bot: ", bot_name)
                bots.append((bot_name, path))
    return bots

def make_playlist(bot_info, team):
    playlist = []
    for bot_name, path in bot_info:
        ex: SimpleExercise = SimpleExercise(bot_name, team = team)
        t = Team.BLUE if team == 1 else Team.ORANGE
        ex.match_config.player_configs = [
            PlayerConfig.bot_config(Path(path), t)
        ]
        playlist.append(ex)
    return playlist

if __name__ == "__main__":
    run_bots()
