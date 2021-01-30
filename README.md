# NBA-fantasy-analytics

Welcome! This is a wrapper I made for the Yahoo Fantasy API. I thought the documentation was a little unintuitive so I made this program to pull all of your relevant Basketball Fantasy Stats.

If you'd like to pull your own custom data you can add this class to your python file and use the code snippet below: 
```python 
YahooAPI = YahooNBAF() 
# url refers to the http address of the request you want to send 
# for more examples refer to the developer guide linked at the bottom of this page
YahooAPI.getResponse(url) 
```

Current data pulled: 
* Team rosters 
* Team's weekly stats (week 1 to current week)
* Each rostered player's total season stats 

# League Details
* Categories tracked:
  * field goals made / attempted
  * field goal percentage
  * free throws made / attempted
  * free throw percentage
  * 3 pointers made
  * points
  * rebounds
  * assists
  * steals
  * blocks
  * turnovers 

# Setup 
1) __Register for the Yahoo Developer Network and get your credentials:__
* 1.1) Sign into the account with your fantasy team at https://yahoo.com/

* 1.2) Go to https://developer.yahoo.com/ --> 'Apps' --> 'Create a new app'

* 1.3) Name your app whatever you please (i.e. "Fantasy Basketball Stats") in the 'Application Name' block. Add a Description if you would like. You can leave Homepage URL blank. For Redirect URl(s) you can add 'https://localhost:8080'

* 1.4) Under the 'API Permissions' sections select 'Fantasy Sports' and then make sure that 'Read' is selected. 'Read/Write' would only be used if you wanted to be able to control your league via Python scripting vice just reading the data from your league. You can come back and change these options in the future

* 1.5) You have now successfully created a Yahoo Developer App and you will see App ID, Client ID(Consumer Key), and Client Secret(Consumer Secret) with a long string of random letters and numbers

2) __Enter in your consumer key and consumer secret into ./authorization/oauth2yahoo.json__

* 2.1) Save the json file and close it

3) __Double click NBAFantasyStats.py__

* 3.1) This will cause a window to pop up

4) __Enter in your league ID__

* 4.1) This can be found on the homepage URL of your league. For example: https://basketball.fantasysports.yahoo.com/nba/<LEAGUE_ID>/<TEAM_ID>

5) __If prompted "Enter Verifier : " a new webpage popup looking like this should have appeared:__

* 5.1)
  ![image](https://user-images.githubusercontent.com/16578851/106080931-035b6d00-60e6-11eb-8851-c8c4454230c5.png)

* 5.2) Enter in this code into the python window 

6) __Wait while the program finishes executing__

* 6.1) This could take >10 minutes

7) __Have fun exploring your data!__

* 7.1) Run this each week to pull the latest data

<br/>
<br/>

Resources and documentation for future development and data that can be extracted from Yahoo's developer guide:
https://developer.yahoo.com/fantasysports/guide/
