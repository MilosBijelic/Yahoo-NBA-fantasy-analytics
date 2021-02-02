# imports core python libraries
import os
import sys
import json


# installs all non-core python libraries required
# --------------------------------------------------------------------------------------------------   
def install(package):
    pip.main(['install', package])

try:
    import pkg_resources
    #print("module 'pkg_resources' is installed")
except ModuleNotFoundError:
    print("module 'pkg_resources' is not installed")
    # or
    install("pkg_resources") # the install function from the question
    # better option:
    print('just installed pkg_resources, please rerun this script at your convenience')
    sys.exit(1)

# enter in required libraries here
required = {'seaborn', 'pandas', 'matplotlib', 'numpy'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
 # --------------------------------------------------------------------------------------------------   
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pdb


with open('../data/league_info.json') as f:
	data = json.load(f)

num_teams = data['fantasy_content']['league'][0]['num_teams']
current_week = data['fantasy_content']['league'][0]['current_week']
team_list = os.listdir('../data/teams')

my_team = input("Please enter in your team name: ")
if my_team in team_list: 
	print("Program running..")
else:
	my_team = input("We think you've made a typo, please enter in your team name exactly as is on Yahoo NBA Fantasy: ")


league_data = {
 "FG%": [], "FGM/A": [], "FT%": [], "FTM/A": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
 }

team_data_json = {
 "FG%": [], "FGM/A": [], "FT%": [], "FTM/A": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
 }

stats_list = ["FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]

for team in team_list:
	for week in range(1, current_week+1):
		with open('../data/teams/'+team+'/team_weekly_stats/week'+str(week)+'/team_stats.json') as json_file: 
			data = json.load(json_file)

			for stat in data.items():
				# adds every teams 9 cat weeky result to league_data
				league_data[stat[0]].append(stat[1])

				# adds your teams 9 cat weekly result to team_data
				if team == my_team: 
					team_data_json[stat[0]].append(stat[1])



league_data = pd.DataFrame.from_dict(league_data)
league_data.replace('', np.nan, inplace=True)
league_data.dropna(inplace=True)
del league_data['FTM/A']
del league_data['FGM/A']
league_data = league_data.apply(pd.to_numeric)

team_data = pd.DataFrame.from_dict(team_data_json)
team_data.replace('', np.nan, inplace=True)
team_data.dropna(inplace=True)
del team_data['FTM/A']
del team_data['FGM/A']
del team_data_json['FTM/A']
del team_data_json['FGM/A']
team_data = team_data.apply(pd.to_numeric)

cat_league_mean = []
cat_league_std = []


for column in league_data.columns:
	cat_league_mean.append(league_data[column].mean())
	cat_league_std.append(league_data[column].std())

team_data_json = {
 "FG%": [], "FT%": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
 }

for row in team_data.iterrows():
	for index in range(9):
		z_score = ((row[1][index] - cat_league_mean[index])/cat_league_std[index])
		team_data_json[stats_list[index]].append(z_score) 

lst = np.array(team_data_json["TO"])
lst = -lst
team_data_json["TO"].clear()
team_data_json["TO"] = lst 

team_data = pd.DataFrame.from_dict(team_data_json)
sns.catplot(data=team_data, kind="box").set(
	title=my_team + ' Weekly 9-cat Performance',
	xlabel="Category",
	ylabel="Z-Score")

print("Enjoy your visualizations!")
plt.plot([9, 0], [0, 0], linewidth=2, linestyle="--", color="red")
plt.show()
