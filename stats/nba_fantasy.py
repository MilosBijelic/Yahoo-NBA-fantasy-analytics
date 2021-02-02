# core python libraries
import sys
import pip
import subprocess

# installs all non-core python libraries required
# --------------------------------------------------------------------------------------------------   
def install(package):
    pip.main(['install', package])

try:
    import pkg_resources
except ModuleNotFoundError:
    print("module 'pkg_resources' is not installed. Installing it now:")
    install("pkg_resources") 
    print('just installed pkg_resources, please rerun this script at your convenience')
    sys.exit(1)

# required libraries
required = {'yahoo_oauth', 'yahoo_fantasy_api'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)
 # --------------------------------------------------------------------------------------------------   

# finish imports
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import json

# authorization path - see readme for more details.
AUTH_PATH = '../authorization/authorization_info.json'

class YahooNBAF:
    def __init__(self): 
        # get session
        self.session = OAuth2(None, None, from_file='../authorization/authorization_info.json')
        
        # get game info
        self.__game = self.__setGame()

        # get league id
        try:
            json_file = open(AUTH_PATH,'r')
            data = json.load(json_file)
            self.__league_id = self.getGameKey() + '.l.' + data["league_id"] 
        except IOError:
            print('There was an error opening the authorization file! See Read Me for instructions.')
            sys.exit(1)
            
        # get league info
        self.__league = self.__setLeague()
        
        # get team info
        self.__team = self.__setTeam()
    
    # private setters
    def __setGame(self):
        game = yfa.Game(self.session, 'nba')
        return game
    
    def __setLeague(self):
        league = self.__game.to_league(self.__league_id)
        return league
    
    def __setTeam(self):
        team_key = self.__league.team_key()
        team = self.__league.to_team(team_key)
        return team
    
    # getters
    def getGameKey(self):
        return self.__game.game_id()
    
    def getLeagueID(self):
        return self.__league_id
    
    def getCurrentWeek(self):
        return self.__league.current_week()
    
    def getNumTeams(self):
        return len(self.__league.teams().keys())
    
    def getNextEditDate(self):
        return self.__league.edit_date()
    
    def getEndWeek(self):
        return self.__league.end_week()
    
    def getStandings(self):
        return self.__league.standings()
    
    def getStatCategories(self):
        return self.__league.stat_categories()
    
    # file dumps
    """
        TODO:
            create csv file
            pick# | round | team | player name | stat1 | stat2 | stat3 etc...
    """
    def dumpDraftResults(self):
        # create team map
        teams = self.__league.teams()
        team_map = {teams[e]['team_key']: teams[e]['name'] for e in teams}
        # get draft results
        draft_results = self.__league.draft_results()
        print("{} draft picks selected".format(len(draft_results)))
        ids = [e['player_id'] for e in draft_results]
        self.__league.player_details(ids)   # Prime the player detail cache
#        print(self.__league.player_details(ids[0]))
        for dp in draft_results:
            plyr = self.__league.player_details(dp['player_id'])
            if "cost" in dp:
                pick_and_cost = "Pick: {:4} Cost: ${:<2} ".format(
                    dp['pick'], dp['cost'])
            else:
                pick_and_cost = "Pick: {:4} ".format(dp['pick'])
            player_and_team = "Player: {:30} Team: {:30}".format(
                plyr[0]['name']['full'], team_map[dp['team_key']])
            print(pick_and_cost + player_and_team)        
        return
    
    def teamResults(self):
        return
    
    def teamStats(self):
        return
    
    def playerStats(self):
        return
    
    
# update output files for league
def updateFantasyLeague():
    # create class
    my_league = YahooNBAF()
    
    # print some week info
    # current week
    # standings
    # print stat categories
    # matchup against
    # your roster
    # their roster
    # next available edit date
    
    ### generate files for data vis / analytics
    # draft results
    my_league.dumpDraftResults()
    # team results
    
    # team stats
    
    # player stats
    
    return


def main():
    updateFantasyLeague()


# if this script is executed (double clicked or called in cmd)
if __name__ == "__main__":
    main()



#    def getMaxPlayers(self): 
#        players_url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+self.game_key+'.l.'+self.league_id+'.t.'+str(self.team_num)+'/roster/players'
#        players_count = self.getResponse(players_url)
#        max_players = players_count['fantasy_content']['team'][1]['roster']['0']['players']['count']
#        return max_players
#
#
#    # Defines a Look Up Table for the stat names. The Yahoo API returns stats with an id instead of a name - e.g. 'FG%' ID is 9007006
#    # This LUT will be used to rename the stats from their ID (9007006) to their recognizable names (FG%)
#    def createStatsLUT(self):
#        statsLUT = {}
#        league_settings_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/settings'
#        response = self.getResponse(league_settings_url)
#        stats_list = response['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
#        num_stats = len(stats_list)
#        for i in range(num_stats):
#            stat_id = stats_list[i]['stat']['stat_id']
#            stat_name = stats_list[i]['stat']['display_name']
#            statsLUT[stat_id] = stat_name
#
#        return statsLUT
#
#
#    # Creates the json files inside data/team/team_name/team_weekly_stats/weekx 
#    def createTeamWeeklyStatsJSON(self, data_obj, statsLUT): 
#        stats = {}
#        i = 0
#        for entry in statsLUT.items(): 
#            cat_name = str(entry[1])
#            cat_val = str(data_obj[i]['stat']['value'])
#            stats[cat_name] = cat_val
#            i = i+1
#        
#        return stats
#
#
#    def getLeagueInfo(self): 
#        league_info_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id
#        league_info = self.getResponse(league_info_url)
#        with open('./data/league_info.json', 'w+') as outfile:
#            json.dump(league_info, outfile)
#
#
#    # pulls each rostered players total season stats and saves it to: "./rosters/roster_total_stats_2020"
#    def getRosteredPlayersTotalStats(self, roster, roster_size): 
#        team_name = roster['fantasy_content']['team'][0][2]['name']
#        stats = {'team_name': str(team_name), 'players': []}
#
#        for player in range(roster_size):
#            player_key = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][0]['player_key']
#            player_id = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][1]['player_id']
#            player_name = roster['fantasy_content']['team'][1]['roster']['0']['players'][str(player)]['player'][0][2]['name']['full']
#
#            player_stats_url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/players;player_keys='+self.game_key+'.p.'+player_id+'/stats'
#            player_stats = self.getResponse(player_stats_url) 
#            
#            stats['players'].append({"player_name": player_name, "player_id": player_id, "player_stats": player_stats['fantasy_content']['league'][1]['players']['0']['player'][1]['player_stats']['stats']}) 
#            
#            path = './data/teams/'+team_name+'/players_total_stats/'
#            if not os.path.exists(path): 
#                os.makedirs(path)
#            with open('./data/teams/'+team_name+'/players_total_stats/'+'total_stats.json' , 'w+') as outfile:
#                json.dump(stats, outfile)
#
#
#    def getTeamsWeeklyStats(self):
#        for week in range(1, self.current_week+1):
#            for matchup in range(int(self.num_teams/2)): # 0-5 (6 matchups, 12 teams)
#                    url = 'https://fantasysports.yahooapis.com/fantasy/v2/league/'+self.game_key+'.l.'+self.league_id+'/scoreboard;week='+str(week)
#                    stats = self.getResponse(url)
#
#                    for team in range(2): # H2H - 2 teams 0 and 1
#                        team_name = stats['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][str(matchup)]['matchup']['0']['teams'][str(team)]['team'][0][2]['name']
#                        path = './data/teams/'+team_name+'/team_weekly_stats/week'+str(week)
#                        if not os.path.exists(path): 
#                            os.makedirs(path)
#                        stats_output = stats['fantasy_content']['league'][1]['scoreboard']['0']['matchups'][str(matchup)]['matchup']['0']['teams'][str(team)]['team'][1]['team_stats']['stats']
#                        weekly_stats = self.createTeamWeeklyStatsJSON(stats_output, self.statsLUT)
#                        with open('./data/teams/'+team_name+'/team_weekly_stats/week'+str(week)+'/'+'team_stats.json', 'w+') as outfile:
#                            json.dump(weekly_stats, outfile)
#
#
#    # Generates all of the league data - roster info, weekly stats, etc. 
#    def updateData(self): 
#        self.getLeagueInfo()
#        self.getTeamsWeeklyStats()
#        
#        # pulls each teams roster info and saves it to: "./rosters"
#        for team in range(1, self.num_teams + 1):
#            roster_url = 'https://fantasysports.yahooapis.com/fantasy/v2/team/'+self.game_key+'.l.'+self.league_id+'.t.'+str(team)+'/roster;week='+str(self.current_week)
#            roster = self.getResponse(roster_url) 
#            team_name = roster['fantasy_content']['team'][0][2]['name']
#            file_name = str(team_name) + '_roster.json'
#            with open('./data/teams/'+team_name+'/'+file_name, 'w') as outfile:
#                json.dump(roster, outfile)
#
#            roster_size = roster['fantasy_content']['team'][1]['roster']['0']['players']['count']
#
#            # TODO: 
#            # Commented out because overloads the API with calls and breaks wrapper
#            # See how long of a wait needs to be added to not overload API with calls
#
#            self.getRosteredPlayersTotalStats(roster, roster_size)