



# imports core python libraries
import os
import subprocess
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


class BoxPlotViz: 
	def __init__(self, year): 
		self.data = pd.read_csv(f'../data/fantasy_results/player_stats_season_{year}.csv')
		teams = self.data['ownership'].unique().tolist()
		self.team_list = []
		for entry in teams: 
			self.team_list.append(entry)
		self.team_list.remove('0')

		self.num_teams = len(self.team_list)



		# Takes in the name of your team and your weekly opponent
		self.my_team = input("Please enter in your team name: ") 
		while self.my_team not in self.team_list: 
			self.my_team = input(f"We think you've made a typo, team must be one of {self.team_list}: ")
			if self.my_team in self.team_list: 
				break 	

		self.opp_team = input("Please enter your opponent's team name: ")
		while self.opp_team not in self.team_list: 
			self.opp_team = input(f"We think you've made a typo, team must be one of {self.team_list}: ")
			if self.opp_team in self.team_list: 
				break

	# pulls a team's 9-cat performance from week 1 to current week 
	def getTeamStats(self, team_name):
		team_data_json = {
		 "IMPACT_FG": [], "IMPACT_FT": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
		 }
#						28				29		17		19		22		23	 24     25		26
		stats_list = ["IMPACT_FG", "IMPACT_FT", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]


		for stat in stats_list:
			for index, row in self.data.iterrows():
				if row[5] == team_name: 
					team_data_json["IMPACT_FG"].append(row[28])
					team_data_json["IMPACT_FT"].append(row[29])
					team_data_json["3PTM"].append(row[17])
					team_data_json["PTS"].append(row[19])
					team_data_json["REB"].append(row[22])
					team_data_json["AST"].append(row[23])
					team_data_json["ST"].append(row[24])
					team_data_json["BLK"].append(row[25])
					team_data_json["TO"].append(row[26])


		# removes blank values - if script is run Monday morning (beginning of week before any games)
		# will get populated with blanks in current week
		team_data_json = self.cleanData(team_data_json)
		return team_data_json


	# pulls every 9-cat value 
	# e.g. week 10, 12 teams = 120 different FG%/PTS/RBS etc. values 
	def getLeagueDataStats(self):
		team_data_json = {
		 "IMPACT_FG": [], "IMPACT_FT": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
		 }
		#				28				29		  17   	 19		 22	    23	  24     25	   26
		stats_list = ["IMPACT_FG", "IMPACT_FT", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]


		for index, row in self.data.iterrows():
				team_data_json["IMPACT_FG"].append(row[28])
				team_data_json["IMPACT_FT"].append(row[29])
				team_data_json["3PTM"].append(row[17])
				team_data_json["PTS"].append(row[19])
				team_data_json["REB"].append(row[22])
				team_data_json["AST"].append(row[23])
				team_data_json["ST"].append(row[24])
				team_data_json["BLK"].append(row[25])
				team_data_json["TO"].append(row[26])


		# removes blank values - if script is run Monday morning (beginning of week before any games)
		# will get populated with blanks in current week
		league_data = self.cleanData(team_data_json)
		return league_data


	# calculates the mean and std dev of each category across the league
	def getLeagueMeanSD(self, league_dataset):
		cat_league_mean = []
		cat_league_SD = []
		for column in league_dataset.columns:
			cat_league_mean.append(league_dataset[column].mean())
			cat_league_SD.append(league_dataset[column].std())
		return cat_league_mean, cat_league_SD

	# removes any blank values 
	# these occur if script is run early in week before any games have happened
	def cleanData(self, dataset):
		dataset = pd.DataFrame.from_dict(dataset)
		dataset.replace('', np.nan, inplace=True)
		dataset.dropna(inplace=True)
		dataset = dataset.apply(pd.to_numeric)

		return dataset

	# Converts each cat value to z-score: (val-mean)/SD
	def convertToZScore(self, dataset, mean, SD):
		team_data_json = {
		 "FG%": [], "FT%": [], "3PTM": [], "PTS": [], "REB": [], "AST": [], "ST": [], "BLK": [], "TO": []
		 }
		stats_list = ["FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]
		for row in dataset.iterrows():
			for index in range(9):
				z_score = ((row[1][index] - mean[index])/SD[index])
				team_data_json[stats_list[index]].append(z_score)
		
		team_data_json = pd.DataFrame.from_dict(team_data_json)
		return team_data_json


	# The goal of the turnover category is to minimze it so the z scores need to be inverted
	def fixTurnOvers(self, dataset): 
		lst = np.array(dataset["TO"])
		lst = -lst
		dataset.drop("TO", axis=1)
		dataset["TO"] = lst 

		return dataset

def userInputSeasonYear():
    season_year = input("Enter the season year (4 digits): ")
    while len(season_year) != 4 or not season_year.isdigit():
        season_year = input("Invalid input. Please enter a 4-digit year.")
    return season_year
# -----------------------------------------------------------------------------------------------------------------------------------------------#

# TO DO: 
# put all function calls in a contained class 
def main():
	SEASON_YEAR = userInputSeasonYear()
	bot = BoxPlotViz(year=SEASON_YEAR)
	my_team_data = bot.getTeamStats(bot.my_team)
	opp_team_data = bot.getTeamStats(bot.opp_team)

	league_data = bot.getLeagueDataStats()

	cat_league_mean, cat_league_SD = bot.getLeagueMeanSD(league_data)

	my_team_data = bot.convertToZScore(my_team_data, cat_league_mean, cat_league_SD) 
	opp_team_data = bot.convertToZScore(opp_team_data, cat_league_mean, cat_league_SD)

	my_team_data = bot.fixTurnOvers(my_team_data)
	opp_team_data = bot.fixTurnOvers(opp_team_data)

	
	# converts the data fram to Category, Team, Value:
	# Cat  Team           Val
	# PTS  Milos's Team   654
	# RBS  Milos's Team   109
	# AST  Opponent Team  144 
	# ...... 
	#Cat is x, Val is y, Team is the sort variable
	stats_list = ["FG%", "FT%", "3PTM", "PTS", "REB", "AST", "ST", "BLK", "TO"]
	viz_data = []
	
	for row in my_team_data.iterrows():
		for index in range(9):
			viz_data.append([stats_list[index], bot.my_team, row[1][index]])
	
	for row in opp_team_data.iterrows():
		for index in range(9):
			viz_data.append([stats_list[index], bot.opp_team, row[1][index]])

	viz_data = pd.DataFrame(viz_data, columns = ["Categories", "Team", "Z-Scores"])


	sns.boxplot(data=viz_data, x='Categories', y='Z-Scores', hue='Team').set(
		title="This Weeks H2H Matchup")
	plt.legend(title='Teams', loc='upper left', bbox_to_anchor=(1, 1))
	plt.show()

# if this script is executed (double clicked or called in cmd)
if __name__ == "__main__":
    main()