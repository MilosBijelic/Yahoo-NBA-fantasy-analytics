import numpy as np
import pandas as pd
# initialize global variables
MATCHUP_FILE = "league_matchup_results.csv" # must be the output of func dumpMatchupResults
STAT_TYPES = ['PTS', 'REB', 'AST', 'ST', 'BLK', 'TO'] # colnames of league_matchup_results which correspond to stats; seems to be league dependent?
BAD_STAT_TYPES = ['TO']

data = (
    pd.read_csv(f'../data/fantasy_results/{MATCHUP_FILE}')
    .assign(matchupID=lambda df: df.apply(
        lambda row: str(row['week']) + '-' + '-'.join(sorted([str(row['team_id']), str(row['opponent_id'])])),
        axis=1
    ))
)

dataFirst = data.drop_duplicates(subset=['matchupID'], keep='first')
dataLast = data.drop_duplicates(subset=['matchupID'], keep='last')
data = (
    dataFirst.merge(dataLast[['matchupID']+STAT_TYPES].add_prefix('opponent_'), left_on='matchupID', right_on='opponent_matchupID')
             .assign(score=0, opponent_score=0)
)

for stat in STAT_TYPES:
    if stat in BAD_STAT_TYPES:
        stat_diff = data[f'opponent_{stat}'] - data[stat]
    else:
        stat_diff = data[stat] - data[f'opponent_{stat}']
    data = data.assign(
        **{f'diff_{stat}': stat_diff,
           'score': data['score'] + np.where(stat_diff > 0, 1, 0),
           'opponent_score': data['opponent_score'] + np.where(stat_diff < 0, 1, 0)}
    )
# Export data to CSV
(data
 .filter(items=['week', 'team_name', 'opponent_name', 'score', 'opponent_score'] + [statgroup for stat in STAT_TYPES for statgroup in (stat, "opponent_" + stat, "diff_" + stat)])
 .to_csv(f'../data/fantasy_results/wide_{MATCHUP_FILE}', index=False)
)