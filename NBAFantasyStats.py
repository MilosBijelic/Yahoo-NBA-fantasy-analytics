from yahoo_oauth import OAuth2
import json
from json import dumps
import os
import time
import pdb

class YahooNBAF:
	def __init__(self): 
		self.league_id = input("Please enter your league id: ")
		self.game_key = self.getGameKey()
		self.num_teams = self.getNumTeams()
		self.current_week = self.getCurrentWeek()
		self.team_num = self.getNumTeams()


	# gets response from Yahoo Fantasy API as a JSON object
	def yahooAPI(self, url): 
		oauth = OAuth2(None, None, from_file='./authorization/oauth2yahoo.json')
		if not oauth.token_is_valid():
		    oauth.refresh_access_token()

		api_json_response = oauth.session.get(url, params={'format': 'json'})
		time.sleep(1)
		return api_json_response.json()


	def getGameKey(self): 
		general_info = f'https://fantasysports.yahooapis.com/fantasy/v2/game/nba'
		general_response = self.yahooAPI(general_info)
		game_key = general_response['fantasy_content']['game'][0]['game_key']
		return game_key


	def getCurrentWeek(self):
		week_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+ self.game_key+'.l.'+self.league_id
		current_week = self.yahooAPI(week_url)['fantasy_content']['league'][0]['current_week']
		return current_week


	def getNumTeams(self):
		league_info_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+ self.game_key+'.l.'+self.league_id
		league_info = self.yahooAPI(league_info_url)
		num_teams = league_info['fantasy_content']['league'][0]['num_teams']
		return num_teams


	def getMaxPlayers(self): 
		players_url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+self.game_key+'.l.'+self.league_id+'.t.'+str(self.team_num)+'/roster/players'
		players_count = self.yahooAPI(players_url)
		max_players = players_count['fantasy_content']['team'][1]['roster']['0']['players']['count']
		return max_players


	# Defines a Look Up Table for the stat names. The Yahoo API returns stats with an id instead of a name - e.g. 'FG%' ID is 9007006
	# This LUT will be used to rename the stats from their ID (9007006) to their recognizable names (FG%)
	def createStatsLUT(self):
		statsLUT = {}
		league_settings_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/settings'
		response = self.yahooAPI(league_settings_url)
		stats_list = response['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
		num_stats = len(stats_list)
		for i in range(0, num_stats):
			stat_id = stats_list[i]['stat']['stat_id']
			stat_name = stats_list[i]['stat']['display_name']
			statsLUT[stat_id] = stat_name

		return statsLUT

	# TO DO:
	# Take a JSON object and replace all instances of stat_id with stat_name using createStatsLUT()
	def replaceStatIDwithStatName(self): 
		statsLUT = createStatsLUT(self.league_id, self.game_key)

	# Changes the key name of a dictionary entry 
	# To be used in replaceStatsIDwithStatName()
	def renameKey(obj, old_key, new_key): 
		# creates a new key value pair with the desired key name and contents of the old value
		obj[new_key] = obj[old_key]
		# now there is two entries with the same value contents, deletes the entry with the old name
		del obj[old_key]

	
	# pulls each rostered players total season stats and saves it to: "./rosters/roster_total_stats_2020"
	def getRosteredPlayersTotalStats(self, roster, roster_size): 
		team_name = roster['fantasy_content']['team'][0][2]['name']
		stats = {'team_name': str(team_name), 'players': []}

		for player in range(0, roster_size):
			player_key = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][0]['player_key']
			player_id = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][1]['player_id']
			player_name = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][2]['name']['full']

			player_stats_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/players;player_keys='+self.game_key+'.p.'+player_id+'/stats'
			player_stats = self.yahooAPI(player_stats_url) 
			
			stats['players'].append({"player_name": player_name, "player_id": player_id, "player_stats": player_stats['fantasy_content']['league'][1]['players']['0']['player'][1]['player_stats']['stats']}) 
			
			path = './data/teams/'+team_name+'/players_total_stats/'
			if not os.path.exists(path): 
				os.makedirs(path)
			with open('./data/teams/'+team_name+'/players_total_stats/'+'total_stats.json' , 'w+') as outfile:
				json.dump(stats, outfile)


	def getTeamsWeeklyStats(self):
		for week in range(1, self.current_week+1):
			for matchup in range(6): # 0-5 (6 matchups, 12 teams)
					url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/scoreboard;week='+str(week)
					stats = self.yahooAPI(url)

					for team in range(2): # H2H - 2 teams 0 and 1
						team_name = stats['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][str(matchup)]['matchup']['0']['teams'][str(team)]['team'][0][2]['name']
						path = './data/teams/'+team_name+'/team_weekly_stats/week'+str(week)
						if not os.path.exists(path): 
							os.makedirs(path)
						H2H_stats = stats['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][str(matchup)]['matchup']['0']['teams'][str(team)]['team'][1]['team_stats']['stats']
						with open('./data/teams/'+team_name+'/team_weekly_stats/week'+str(week)+'/'+'team_stats.json', 'w+') as outfile:
							json.dump(H2H_stats, outfile)


	# Generates all of the league data - roster info, weekly stats, etc. 
	def updateData(self): 
		self.getTeamsWeeklyStats()
		
		# pulls each teams roster info and saves it to: "./rosters"
		for team in range(1, self.num_teams + 1):
			roster_url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+self.game_key+'.l.'+self.league_id+'.t.'+str(team)+'/roster;week='+str(self.current_week)
			roster = self.yahooAPI(roster_url) 
			team_name = roster['fantasy_content']['team'][0][2]['name']
			file_name = str(team_name) + '_roster.json'
			with open('./data/teams/'+team_name+'/'+file_name, 'w') as outfile:
				json.dump(roster, outfile)

			player_list = roster['fantasy_content']['team'][1]['roster']['0']['players']
			roster_size = len(player_list)-2

			# TO DO: 
			# Commented out because overloads the API with calls and breaks wrapper
			# See how long of a wait needs to be added to not overload API with calls

			self.getRosteredPlayersTotalStats(roster, roster_size)








def main():
	bot = YahooNBAF()
	bot.updateData()


# if this script is executed (double clicked or called in cmd)
if __name__ == "__main__":
    main()

