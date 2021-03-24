# -*- coding: utf-8 -*-
"""
Created on Fri Mar 12 13:08:07 2021

What if player swap prints what your matchup outcomes would be if you swapped one player on your roster for another player not on your roster.
"""
import time
import os
import pandas as pd
import datetime
import numpy as np
import ast

# import YahooNBAF class
import sys
sys.path.insert(1, '../data/')
from generate_nba_fantasy_data import YahooNBAF

def load_data_files():  
    timestr = time.strftime("%Y%m%d")

    # player daily stats: using BeautifulSoup and BasketballReference.com simply because yahoo api sucks and has major query clogs.
    outname_gl = '../data/fantasy_results/player_stats_daily_season_' + timestr + '.csv'
    if not os.path.exists(outname_gl):
        print("try generating the data files again")
        sys.exit()

    # matchup results 
    outname_mr = '../data/fantasy_results/league_matchup_results_' + timestr + '.csv'
    if not os.path.exists(outname_mr):
        print("try generating the data files again")
        sys.exit()
    
    # daily rosters    
    outname_dr = '../data/fantasy_results/league_daily_rosters_' + timestr + '.csv'
    if not os.path.exists(outname_dr):
        print("try generating the data files again")
        sys.exit()
    
    # load datafiles
    matchup_results = pd.read_csv(outname_mr)
    daily_rosters = pd.read_csv(outname_dr)
    gamelogs = pd.read_csv(outname_gl)
    return matchup_results, daily_rosters, gamelogs

def load_matchup_result(yahoo_league: YahooNBAF, matchup_results: pd.DataFrame()) -> [pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]:
    team_name = yahoo_league.getTeamName()
    col_names = ['week','team_name','opponent_name','FG%','FT%','3PTM','PTS','REB','AST','ST','BLK','TO']

    # get team output
    mr_team = matchup_results[matchup_results['team_name'] == team_name]
#    mr_team = matchup_results[matchup_results['team_id'] == "402.l.42709.t.1"]
    
    mr_team = mr_team[col_names]
    
    # get opponents output
    opp_team = matchup_results[matchup_results['opponent_name'] == team_name]
#    opp_team = matchup_results[matchup_results['opponent_id'] == "402.l.42709.t.1"]

    opp_team = opp_team[col_names]

    results = pd.DataFrame(columns=['week','team_name','opponent_name', 'DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO'])
    weekly_result = {}
    weekly_result['team_name'] = team_name
    for week in range(1,mr_team.week.max()+1):
        mr_team_week = mr_team[mr_team['week']==week]
        opp_team_week = opp_team[opp_team['week']==week]
        weekly_result['week'] = week
        weekly_result['opponent_name'] = mr_team_week['opponent_name'].values[0]
        weekly_result['DIFF_FG%'] = mr_team_week['FG%'].values[0] - opp_team_week['FG%'].values[0]
        weekly_result['DIFF_FT%'] = mr_team_week['FT%'].values[0] - opp_team_week['FT%'].values[0]
        weekly_result['DIFF_3PTM'] = mr_team_week['3PTM'].values[0] - opp_team_week['3PTM'].values[0]
        weekly_result['DIFF_PTS'] = mr_team_week['PTS'].values[0] - opp_team_week['PTS'].values[0]
        weekly_result['DIFF_REB'] = mr_team_week['REB'].values[0] - opp_team_week['REB'].values[0]
        weekly_result['DIFF_AST'] = mr_team_week['AST'].values[0] - opp_team_week['AST'].values[0]
        weekly_result['DIFF_ST'] = mr_team_week['ST'].values[0] - opp_team_week['ST'].values[0]
        weekly_result['DIFF_BLK'] = mr_team_week['BLK'].values[0] - opp_team_week['BLK'].values[0]
        weekly_result['DIFF_TO'] = opp_team_week['TO'].values[0] - mr_team_week['TO'].values[0]
        results = results.append(weekly_result,ignore_index=True)
    
    results_w = results[['DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO']]>0
    results['win'] = results_w.sum(axis=1)
    
    results_l = results[['DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO']]<0
    results['loss'] = results_l.sum(axis=1)
    
    results_t = results[['DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO']]==0
    results['tie'] = results_t.sum(axis=1)
    
    return mr_team, opp_team, results

def plot_results(results):
    import matplotlib.pyplot as plt
    
    weeks = results.week.values
    
    a = results['DIFF_FG%'].values *100
    b = results['DIFF_FT%'].values *100
    c = results['DIFF_3PTM'].values
    d = results['DIFF_PTS'].values
    e = results['DIFF_REB'].values
    f = results['DIFF_AST'].values
    g = results['DIFF_ST'].values
    h = results['DIFF_BLK'].values
    i = results['DIFF_TO'].values
    

    
    fig = plt.figure()
    ax=fig.add_subplot(111)
    ax.set_ylabel("difference in category")
    ax.set_xlabel("week")
    bar1 = ax.bar(weeks-0.4, a, width=0.1, color='b', align='center')
    bar2 = ax.bar(weeks-0.3, b, width=0.1, color='g', align='center')
    bar3 = ax.bar(weeks-0.2, c, width=0.1, color='r', align='center')
    bar4 = ax.bar(weeks-0.1, d, width=0.1, color='c', align='center')
    bar5 = ax.bar(weeks, e, width=0.1, color='m', align='center')
    bar6 = ax.bar(weeks+0.1, f, width=0.1, color='y', align='center')
    bar7 = ax.bar(weeks+0.2, g, width=0.1, color='limegreen', align='center')
    bar8 = ax.bar(weeks+0.3, h, width=0.1, color='slategrey', align='center')
    bar9 = ax.bar(weeks+0.4, i, width=0.1, color='mediumblue', align='center')
    
    def autolabel(rects):
        for rect in rects:
            h = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%d'%int(h),
                    ha='center', va='bottom')

    autolabel(bar1)
    autolabel(bar2)
    autolabel(bar3)
    autolabel(bar4)
    autolabel(bar5)
    autolabel(bar6)
    autolabel(bar7)
    autolabel(bar8)
    autolabel(bar9)
    
    ax.legend((bar1[0], bar2[0], bar3[0], bar4[0], bar5[0], bar6[0], bar7[0], bar8[0], bar9[0]),
               ('DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO') )
    plt.show()
    return

def print_results(results):
    """
    print a summary of category wins
    """
    categories = ['DIFF_FG%','DIFF_FT%', 'DIFF_3PTM', 'DIFF_PTS', 'DIFF_REB', 'DIFF_AST', 'DIFF_ST', 'DIFF_BLK', 'DIFF_TO']
    
    results['DIFF_FG%'] = results['DIFF_FG%']*100
    results['DIFF_FT%'] = results['DIFF_FT%']*100
    
    ovr_win = 0
    ovr_loss = 0
    ovr_tie = 0
    for cat in categories:
        # get average
        average = sum(results[cat].values)/len(results[cat].values)
        stdev = results[cat].std()
        wins = sum(results[cat]>0)
        losses = sum(results[cat]<0)
        ties = sum(results[cat]==0)
        print("\n\n------------------------------\n\n")
        print("CATEGORY SUMMARY %s" %(cat))
        print("WINS: %d" %(wins))
        print("LOSSES: %d" %(losses))
        print("TIES: %d" %(ties))
        print("AVERAGE CAT DIFF: %f \n STANDARD DEVIATION DIFF: %f" %(average,stdev))
        ovr_win += wins
        ovr_loss += losses
        ovr_tie += ties
    
    print("\n\n------------------------------\n\nOVERALL WINS: %d" %ovr_win)
    print("OVERALL LOSSES: %d" %ovr_loss)
    print("OVERALL TIES: %d" %ovr_tie)
    return

def what_if_player_swap(my_league,mr,dr,gl,cur_plyr,new_plyr):
    """
    swaps players and returns results
    """
    # create new mr
    mr_new = mr.copy() #deep=True
    
    # get start date of season
    start_date_str = dr['current_date'].min()
    start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d')
    
    # get end date of season
    end_date_str = dr['current_date'].max()
    end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # get current player log
    cur_plyr_log = gl[gl['player_id']==cur_plyr]
    
    # get new player log
    new_plyr_log = gl[gl['player_id']==new_plyr]
    
    delta = datetime.timedelta(days=1)
    # loop through each date
    while start_date<=end_date:
        # get player stats for that day
        cur_plyr_has_game = np.any(cur_plyr_log['stat_type']==start_date_str)
        new_plyr_has_game = np.any(new_plyr_log['stat_type']==start_date_str)
        if(not(cur_plyr_has_game) and not(new_plyr_has_game)):
            start_date+=delta
            start_date_str = '{:%Y-%m-%d}'.format(start_date)
            continue
        
        # get daily rosters of all teams
        daily_rosters = dr[dr['current_date']==start_date_str]
        # get league results for that week
        week = daily_rosters['week'].iloc[0]
        
        # go through each daily_roster
        for index,row in daily_rosters.iterrows():
            # if cur_plyr is found
            team_id = row['team_id']
            roster = ast.literal_eval(row['selected_positions'])
            
            # get current results for week
            FGM_FGA = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FGM/A'].values[0].split('/')
            FGM = int(FGM_FGA[0])
            FGA = int(FGM_FGA[1])
            FTM_FTA = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FTM/A'].values[0].split('/')
            FTM = int(FTM_FTA[0])
            FTA = int(FTM_FTA[1])
            PTS = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'PTS'].item()
            PTM_3 = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), '3PTM'].item()
            REB = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'REB'].item()
            AST = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'AST'].item()
            ST = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'ST'].item()
            BLK = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'BLK'].item()
            TO = mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'TO'].item()
            
            if(roster.get(cur_plyr,0)):             
                # if cur plyr has played subtract stats from roster
                position = roster.get(cur_plyr)
                if((position != 'BN') and (position != 'IL') and (cur_plyr_has_game)):
                    
                    cur_stats = gl[(gl['stat_type']==start_date_str) & (gl['player_id']==cur_plyr)]
                    # subtract current player stats from matchup results
#                    print("MR BEFORE SUBTRACTING CURRENT PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])
#                    print(cur_stats)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), '3PTM'] = PTM_3 - cur_stats['3PTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'PTS'] = PTS - cur_stats['PTS'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'TO'] = TO - cur_stats['TO'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'REB'] = REB - cur_stats['REB'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'AST'] = AST - cur_stats['AST'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'BLK'] = BLK - cur_stats['BLK'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'ST'] = ST - cur_stats['ST'].iloc[0]
                    FGA -= cur_stats['FGA'].iloc[0]
                    FGM -= cur_stats['FGM'].iloc[0]
                    FTA -= cur_stats['FTA'].iloc[0]
                    FTM -= cur_stats['FTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FTM/FTA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FG%'] = float(FGM/FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FGM/A'] = '{}/{}'.format(FGM,FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FTM/A'] = '{}/{}'.format(FTM,FTA)
#                    print("MR AFTER SUBTRACTING CURRENT PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])
                    
                # if new plyr has played add their stats to roster
                if(new_plyr_has_game):
#                    print("MR BEFORE ADDING NEW PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])
                    # add new player stats from matchup results
                    new_stats = gl[(gl['stat_type']==start_date_str) & (gl['player_id']==new_plyr)]
#                    print(new_stats)
                    # subtract current player stats from matchup results
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), '3PTM'] = PTM_3 + new_stats['3PTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'PTS'] = PTS + new_stats['PTS'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'TO'] = TO + new_stats['TO'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'REB'] = REB + new_stats['REB'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'AST'] = AST + new_stats['AST'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'BLK'] = BLK + new_stats['BLK'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'ST'] = ST + new_stats['ST'].iloc[0]
                    FGA += new_stats['FGA'].iloc[0]
                    FGM += new_stats['FGM'].iloc[0]
                    FTA += new_stats['FTA'].iloc[0]
                    FTM += new_stats['FTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FTM/FTA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FGM/FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FGM/A'] = '{}/{}'.format(FGM,FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FTM/A'] = '{}/{}'.format(FTM,FTA)
#                    print("MR AFTER ADDING NEW PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])
                    
            # check to see if new_plyr is in the roster instead
            elif(roster.get(new_plyr,0)):
                # if new plyr has played subtract stats from roster
                position = roster.get(new_plyr)
                if((position != 'BN') and (position != 'IL') and new_plyr_has_game):
#                    print("MR BEFORE SUBTRACTING NEW PLAYER: ")
                    
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])                    
                    new_stats = gl[(gl['stat_type']==start_date_str) & (gl['player_id']==new_plyr)]
#                    print(new_stats)
                    # subtract new player stats from matchup results
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), '3PTM'] = PTM_3 - new_stats['3PTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'PTS'] = PTS - new_stats['PTS'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'TO'] = TO - new_stats['TO'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'REB'] = REB - new_stats['REB'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'AST'] = AST - new_stats['AST'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'BLK'] = BLK - new_stats['BLK'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'ST'] = ST - new_stats['ST'].iloc[0]
                    FGA -= new_stats['FGA'].iloc[0]
                    FGM -= new_stats['FGM'].iloc[0]
                    FTA -= new_stats['FTA'].iloc[0]
                    FTM -= new_stats['FTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FTM/FTA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FGM/FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FGM/A'] = '{}/{}'.format(FGM,FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FTM/A'] = '{}/{}'.format(FTM,FTA)
#                    print("MR AFTER  SUBTRACTING NEW PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])  
                # if new plyr has played add their stats to roster
                if(cur_plyr_has_game):
                    # add new player stats from matchup results
                    cur_stats = gl[(gl['stat_type']==start_date_str) & (gl['player_id']==cur_plyr)]
#                    print("MR BEFORE ADDING CUR PLAYER: ")
#                    
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])  
#                    print(cur_stats)
                    # subtract current player stats from matchup results
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), '3PTM'] = PTM_3 + cur_stats['3PTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'PTS'] = PTS + cur_stats['PTS'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'TO'] = TO + cur_stats['TO'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'REB'] = REB + cur_stats['REB'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'AST'] = AST + cur_stats['AST'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'BLK'] = BLK + cur_stats['BLK'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'ST'] = ST + cur_stats['ST'].iloc[0]
                    FGA += cur_stats['FGA'].iloc[0]
                    FGM += cur_stats['FGM'].iloc[0]
                    FTA += cur_stats['FTA'].iloc[0]
                    FTM += cur_stats['FTM'].iloc[0]
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FTM/FTA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FT%'] = float(FGM/FGA) 
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FGM/A'] = '{}/{}'.format(FGM,FGA)
                    mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week), 'FTM/A'] = '{}/{}'.format(FTM,FTA)
#                    print("MR AFTER ADDING CUR PLAYER: ")
#                    print(mr_new.loc[(mr_new['team_id']==team_id) & (mr_new['week']==week)])  
        start_date+=delta
        start_date_str = '{:%Y-%m-%d}'.format(start_date)
        
    return mr_new

def main():
    mr, dr, gl = load_data_files()
    
    ########################
    #PLACEHOLDER FOR TESTING
    cur_plyr=5600 #BEN simmons
    new_plyr=3930 #cp3
#    # get player swap from user
#    cur_plyr = int(input("please enter 4-digit player id who you would like to drop: \n"))
#    # check input length
#    if not(999<cur_plyr<10000):
#        print("player id must be 4 digits in length")
#        sys.exit()
#    new_plyr = int(input("please enter 4-digit player id who you would like to replace with the dropped player: \n"))
#    # check input length
#    if not(999<new_plyr<10000):
#        print("player id must be 4 digits in length")
#        sys.exit()
    ########################
    
    # create fantasy object to get team details.
    my_league = YahooNBAF()
    
    # summarize current matchup results
    mr_team, opp_team, results = load_matchup_result(my_league,mr)
    print(results)
    print("printing current matchup results: ")
    plot_results(results)
    print_results(results)
    
    # summarize new matchup results
    mr_new = what_if_player_swap(my_league,mr,dr,gl,cur_plyr,new_plyr)
    mr_team_new, opp_team_new, results_new = load_matchup_result(my_league,mr_new)
    print("printing new matchup results: ")
    plot_results(results_new)
    print_results(results_new)
    return

# if this script is executed (double clicked or called in cmd)
if __name__ == "__main__":
    main()

