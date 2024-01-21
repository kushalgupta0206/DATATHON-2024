import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from scipy.cluster.hierarchy import dendrogram, linkage
from statistics import mean
import math
import numpy as np


df = pd.read_csv("time_and_dist.csv").merge(pd.read_csv("performance_metric_final.csv"), on=["game_date","home_team","away_team"])
# old implementation we are no longer persuing (EWP metric)
"""
metr_df = pd.read_csv("performance_metric_final.csv")
metr_df["new_metric_home"] = metr_df["home_EWP"]-metr_df["home_EWP_post"]
metr_df["new_metric_away"] = metr_df["away_EWP"]-metr_df["away_EWP_post"]
"""

# old implementation we are no longer persuing (totals)
"""df = pd.read_csv("time_and_dist.csv").merge(pd.read_csv("performance_metric_final.csv"), on = ["game_date", "home_team", "away_team"])
df["dist_tot"] = df["distance_from_last_location_home_team"] + df["distance_from_last_location_away_team"]
df["time_tot"] = df["tslg_home"] + df["tslg_away"]
df["score_tot"] = (df["home_score"]*df["distance_from_last_location_home_team"] + df["away_score"]*df["distance_from_last_location_away_team"])/df["dist_tot"]"""

# splits home and away teams and makes a team by team dataframe
home = df[["home_team","distance_from_last_location_home_team", "tslg_home", "diff_rel_home_EWP", "home_score"]]
home = home.rename(columns={'home_team': 'team', 'distance_from_last_location_home_team': 'dist', 'tslg_home': 'time',
                             'diff_rel_home_EWP': 'metr', 'home_score' : 'score'})
away = df[["away_team","distance_from_last_location_away_team", "tslg_away", "diff_rel_away_EWP", "away_score"]]
away = away.rename(columns={'away_team': 'team', 'distance_from_last_location_away_team': 'dist', 'tslg_away': 'time',
                             'diff_rel_away_EWP': 'metr', 'away_score' : 'score'})
onebyone_team = pd.concat([home,away])


# abandoned scatter implementation
"""
plt.scatter(df["dist_tot"], df["score_tot"])
plt.xlabel('Total Distance')
plt.ylabel('Total Score')
plt.show()
"""
# time and dist groupings
onebyone_team["dist_cat"] = ['stay' if x == 0 else 'small' if x <= 400 else 'medium' if x <= 4000 else 'large' for x in onebyone_team["dist"]]
onebyone_team["time_cat"] = ['first' if x == 0 else 'next_day' if x == 1 else 'break' if x >= 2 else 'large' for x in onebyone_team["dist"]]

# print(df)
counts = onebyone_team['dist_cat'].value_counts()

#prints for analyzing subgroups
print(onebyone_team[onebyone_team["dist_cat"]=="stay"]["score"].mean())
print(onebyone_team[onebyone_team["dist_cat"]=="small"]["score"].mean())
print(onebyone_team[onebyone_team["dist_cat"]=="medium"]["score"].mean())
print(onebyone_team[onebyone_team["dist_cat"]=="large"]["score"].mean())
print(onebyone_team[((onebyone_team["time"]<=1) & (onebyone_team["dist_cat"]=="large"))]["score"].mean())
print(onebyone_team[((onebyone_team["time"]>=2) & (onebyone_team["dist_cat"]=="small"))]["score"].mean())
u, p = mannwhitneyu(onebyone_team[(onebyone_team["dist_cat"]=="small")]["score"].values,
                    onebyone_team[(onebyone_team["dist_cat"]!="small")]["score"].values)
print(f'U = {u}, p = {p}')

# encodes distance groups
onebyone_team['dist_encoded'] = onebyone_team['dist_cat'].astype('category').cat.codes

# aggregates the time/dist points, the mean score at those points, and their frequency
add_up = {}
for i,r in onebyone_team.iterrows():

    if (r["time"],r["dist_encoded"]) not in add_up.keys():
        # adds row to add_up
        add_up[(r["time"],r["dist_encoded"])] = [[r["score"]],1]

    else:
        add_up.get((r["time"],r["dist_encoded"]))[1] += 1 
        add_up.get((r["time"],r["dist_encoded"]))[0].append(r["score"])

# converts add_up into a DataFrame
total_ammounts = pd.DataFrame()
for k, v in add_up.items():
    row = pd.DataFrame([{'time': k[0], 'dist_encoded': k[1], 'score': mean(v[0]), 'freq': math.log(v[1],1.05)}])
    total_ammounts = pd.concat([total_ammounts, row])

# plot
fig, ax = plt.subplots()
scatter = ax.scatter(total_ammounts['dist_encoded'], total_ammounts['time'], c=total_ammounts['score'], s=total_ammounts['freq'])
plt.xlabel('Distance')
plt.ylabel('Time')
plt.title('Colored Scatter Plot with Time on the X-Axis and Distance on the Y-Axis')
cbar = plt.colorbar(scatter, ax=ax, shrink=.5)
cbar.set_label('Score')
ax.yaxis.set_ticks(np.arange(0, 18, 1))
ax.yaxis.set_ticks(np.arange(0, 18, 1))
ax.set_xticklabels([" ","stay"," ", "close"," ", "medium"," ", "far"])
plt.show()

# abandoned dendrogram implementation
"""linkage_matrix = linkage(onebyone_team[['dist_cat', 'score']], 'ward')
plt.figure(figsize=(10, 5))
dendrogram(linkage_matrix,
           leaf_rotation=90.,
           leaf_font_size=8.,
           labels=onebyone_team['dist_cat'],
           distance_sort='descending')
plt.show




# ["score"].mean())
#plt.figure(figsize=(10, 5))
#plt.bar(counts.index, counts.values)
#plt.xlabel('Category')
#plt.ylabel('Frequency')
#plt.title('Histogram of Counts')
#plt.show()

#onebyone_team.to_csv("time_dist_metric.csv")

#plt.scatter(onebyone_team["time"], onebyone_team["dist"])
#plt.scatter(df["dist_tot"], df["score_tot"])
# plt.ylim(10, 25)
# plt.xlim(0,0)
#plt.show()
"""