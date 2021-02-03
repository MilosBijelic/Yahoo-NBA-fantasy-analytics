# core python libraries
import sys
import pip
import subprocess
import os
import time

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
import pandas as pd

# authorization path - see readme for more details.
AUTH_PATH = '../authorization/authorization_info.json'

class YahooNBAF:
    def __init__(self): 
        # get session
        self.session = OAuth2(None, None, from_file=AUTH_PATH)
        
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
    
    def getPlayerOverallStats(self, plyr, stat_map):
        """
        gets current player stats
            input:
                self - YAHOONBAF object
                plyr - player details for current season
            output:
                ply_stats - dict of stats for current season ['FG%','FT%','3PT','PTS','REB','ASSITS','STEALS','BLOCKS','TOS','FGM_A','FTM_A']
        """
        # get player stats
        stat_id_map = stat_map
        stats = {stat_id_map[stat['stat']['stat_id']]: stat['stat']['value'] for stat in plyr[0]['player_stats']['stats']}  
        return stats
    
    def getImpactFG(self,df):
        """
        gets impact fg. impact fg defined as:
        p-P=d
        d*a=m
        where:
            p = player average
            P = league average
            d = difference of player average against league average
            a = player attempts
            m = impact score
        input:
            df - with player name and category stats
        output:
            df_impact_fg - df with included impact scores
        """        
        P = df['FG%'].mean()
            
        def attempts(x):
            a = int(x['FGM/A'].split('/')[0])
            return a
        
        df['IMPACT_FG'] = df.apply(lambda x: ((x['FG%']-P)*attempts(x)),axis=1)
        return df
    
    def getImpactFT(self,df):
        """
        gets impact ft. impact ft defined as:
        p-P=d
        d*a=m
        where:
            p = player average
            P = league average
            d = difference of player average against league average
            a = player attempts
            m = impact score
        input:
            df - with player name and category stats
        output:
            df_impact_ft - df with included impact scores
        """        
        P = df['FT%'].mean()
            
        def attempts(x):
            a = int(x['FTM/A'].split('/')[0])
            return a
        
        df['IMPACT_FT'] = df.apply(lambda x: ((x['FT%']-P)*attempts(x)),axis=1)
        return df

    # helper functions
    def createStatsLUT(self):
        """
        define a look up table for the stat names. i.e. translate ID(9007006) to ('FG%')
        """
        stat_list=self.__league.yhandler.get_settings_raw(self.__league_id)['fantasy_content']['league'][1]['settings'][0]['stat_categories']['stats']
        statsLUT = {str(stat['stat']['stat_id']): stat['stat']['display_name'] for stat in stat_list}
        return statsLUT
    
    def replaceWithZero(self, df):
        """
        replaces empty stats with zero. convert stats to proper data type.
        """ 
        df['FGM/A'] = df['FGM/A'].replace('-/-', '0/0')
        df['FGM/A'] = df['FGM/A'].astype(str)
        df['FG%'] = df['FG%'].replace('-', '0')
        df['FG%'] = df['FG%'].astype(float)
        df['FTM/A'] = df['FTM/A'].replace('-/-', '0/0')
        df['FTM/A'] = df['FTM/A'].astype(str)
        df['FT%'] = df['FT%'].replace('-', '0')
        df['FT%'] = df['FT%'].astype(float)
        df['3PTM'] = df['3PTM'].replace('-', '0')
        df['3PTM'] = df['3PTM'].astype(int)
        df['PTS'] = df['PTS'].replace('-', '0')
        df['PTS'] = df['PTS'].astype(int)
        df['REB'] = df['REB'].replace('-', '0')
        df['REB'] = df['REB'].astype(int)
        df['AST'] = df['AST'].replace('-', '0')
        df['AST'] = df['AST'].astype(int)
        df['ST'] = df['ST'].replace('-', '0')
        df['ST'] = df['ST'].astype(int)
        df['BLK'] = df['BLK'].replace('-', '0')
        df['BLK'] = df['BLK'].astype(int)
        df['TO'] = df['TO'].replace('-', '0')
        df['TO'] = df['TO'].astype(int)
        return df
        
    
    # file dump functions
    """
        TODO:
            create csv file
            pick# | round | team | player name | stat1 | stat2 | stat3 etc...
    """
    def dumpDraftResults(self):
        # create team map
        teams = self.__league.teams()
        team_map = {teams[e]['team_key']: teams[e]['name'] for e in teams}
        stat_map = self.createStatsLUT()
        num_teams = self.getNumTeams()
        # get draft results
        draft_results = self.__league.draft_results()
        print("{} draft picks selected".format(len(draft_results)))
        ids = [e['player_id'] for e in draft_results]
        self.__league.player_details(ids)   # Prime the player detail cache
        
        # create dataframe
        stat_columns = [sc['display_name'] for sc in self.getStatCategories()]
        cols = ['pick', 'round', 'team', 'player', 'position'] + stat_columns + ['FGM/A', 'FTM/A']
        output = pd.DataFrame(columns=cols)   
        for dp in draft_results:
            plyr = self.__league.player_details(dp['player_id'])
            if "cost" in dp:
                pick_and_cost = "Pick: {:4} Cost: ${:<2} ".format(
                    dp['pick'], dp['cost'])
            else:
                pick_and_cost = "Pick: {:4} ".format(dp['pick'])
            player_and_team = "Player: {:30} Team: {:30}".format(
                plyr[0]['name']['full'], team_map[dp['team_key']])
            
            # get draft info
            basic_info = {}
            basic_info['pick'] = dp['pick']
            basic_info['round'] = ((dp['pick']-1)//num_teams) + 1
            basic_info['team'] = team_map[dp['team_key']]
            basic_info['player'] = plyr[0]['name']['full']
            basic_info['position'] = plyr[0]['primary_position']
            
            # get stats of player
            stats = self.getPlayerOverallStats(plyr,stat_map)

            draft_pick_summary = {**basic_info, **stats} # merge dicts

            # append draft result to df
            output = output.append(draft_pick_summary, ignore_index=True)
            
            print(pick_and_cost + player_and_team)
        
        # create impact columns
        output = self.replaceWithZero(output) # convert empty stats to 0
        output = self.getImpactFG(output)
        output = self.getImpactFT(output)
        
        # export to .csv
        outname = 'draft_results.csv'
        
        outdir = './fantasy_results/'
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        
        fullname = os.path.join(outdir, outname)    
        
        output.to_csv(fullname,index=False) 
        
        return
    
    """
    CSV OUTPUT
    """
    def dumpPlayerOverallStats(self):
        return
    
    """
    CSV OUTPUT
    team | opponent | week | TCAT1 | OPPCAT1 | 
    """
    def dumpLeagueStats(self):
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

