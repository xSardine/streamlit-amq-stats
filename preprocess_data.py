import pandas as pd
from pathlib import Path
import numpy as np

DATA_CSV_PATH = Path("data/csv/")

players_answers = pd.read_csv(DATA_CSV_PATH / Path("players_answers.csv"))
rankeds_games = pd.read_csv(DATA_CSV_PATH / Path("rankeds_games.csv"))

region_map = {1: "Asia", 2: "Europe", 3: "North America"}
rankeds_games.region = rankeds_games.region.map(region_map)
rankeds_games.to_csv(DATA_CSV_PATH / Path("rankeds_games.csv"))
