import pandas as pd
dist = pd.read_csv("distance_covered_since_last_game.csv")
time = pd.read_csv("time_since_last_game_complete.csv")
merged = dist.merge(time)
merged.to_csv("time_and_dist.csv", index=False)