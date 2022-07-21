import requests
import pandas as pd
import json
import time
import creds

# Step 1: Copy and paste this link into your browser
# http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

# Step 2: Retrieve the Authorization Code
# The link will look like this: http://localhost/exchange_token?state=&code=[THIS_IS_THE_CODE_YOU_NEED_TO_COPY]&scope=read,activity:read_all,profile:read_all

# Step 3: Retrieve your access and refresh tokens 
##Make Strava auth API call with your client_code, client_secret and authorization code
#response = requests.post(
#                    url = 'https://www.strava.com/oauth/token',
#                    data = {
#                            'client_id': creds.CLIENT_ID,
#                            'client_secret': creds.CLIENT_SECRET,  
#                            'code': creds.AUTHORIZATION_CODE,
#                            'grant_type': 'authorization_code'
#                            }
#                )
#
##Save json response as a variable
#strava_tokens = response.json()
#
##Save tokens to file
#with open('strava_tokens.json', 'w') as outfile:
#    json.dump(strava_tokens, outfile)
#
##Open JSON file and print the file contents to check it's worked properly
#with open('strava_tokens.json') as check:
#  data = json.load(check)
#print(data)

# Step 4: Use your refresh token to retrieve a new access token (if expired) --- note depends on Step 1-3
# Get the tokens from file to connect to Strava
with open('strava_tokens.json') as json_file:
    strava_tokens = json.load(json_file)

# If access_token has expired then use the refresh_token to get the new access_token
if strava_tokens['expires_at'] < time.time():

# Make Strava auth API call with current refresh token
    response = requests.post(
                        url = 'https://www.strava.com/oauth/token',
                        data = {
                                'client_id': creds.CLIENT_ID,
                                'client_secret': creds.CLIENT_SECRET,
                                'grant_type': 'refresh_token',
                                'refresh_token': strava_tokens['refresh_token']
                                }
                    )
# Save response as json in new variable
    new_strava_tokens = response.json()

# Save new tokens to file
    with open('strava_tokens.json', 'w') as outfile:
        json.dump(new_strava_tokens, outfile)

# Use new Strava tokens from now
    strava_tokens = new_strava_tokens

# Open the new JSON file and print the file contents 
# to check it's worked properly
with open('strava_tokens.json') as check:
  data = json.load(check)
#print(data)

# Helper Functions to convert and format data
def convert_distance (data):
  # m to km
  return round(data/1000, 2)

def convert_duration (data):
  # sec to min
  return round(data/60, 2)

def convert_speed (data):
  # m/s to km/h
  return round(data*3.6, 2)

# Loop through all activities
page = 1
url = "https://www.strava.com/api/v3/activities"
access_token = strava_tokens['access_token']

# Create the dataframe ready for the API call to store your activity data
activities = pd.DataFrame(
    columns = [
            "id",
            "name",
            "start_date_local",
            "location_country",
            "end_latlng",
            "type",
            "distance",
            "moving_time",
            "elapsed_time",
            "total_elevation_gain",
            "average_speed",
            "max_speed",
            "average_cadence",
            "average_watts",
            "max_watts",
            "weighted_average_watts",
            "average_heartrate",
            "max_heartrate",
            "kilojoules",
            "suffer_score",
            "pr_count",
            "achievement_count",
            "external_id"
    ]
)

while True:
    
    # get page of activities from Strava
    r = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
    r = r.json()
    
    # if no results then exit loop
    if (not r):
        break

    # otherwise add new data to dataframe
    for x in range(len(r)):

        activities.loc[x + (page-1)*200,'id'] = r[x]['id']
        activities.loc[x + (page-1)*200,'name'] = r[x]['name']
        activities.loc[x + (page-1)*200,'start_date_local'] = r[x]['start_date_local']
        activities.loc[x + (page-1)*200,'location_country'] = r[x]['location_country']
        activities.loc[x + (page-1)*200,'end_latlng'] = r[x]['end_latlng']
        activities.loc[x + (page-1)*200,'type'] = r[x]['type']
        activities.loc[x + (page-1)*200,'distance'] = convert_distance(r[x]['distance'])
        activities.loc[x + (page-1)*200,'moving_time'] = convert_duration(r[x]['moving_time'])
        activities.loc[x + (page-1)*200,'elapsed_time'] = convert_duration(r[x]['elapsed_time'])
        activities.loc[x + (page-1)*200,'total_elevation_gain'] = r[x]['total_elevation_gain']
        activities.loc[x + (page-1)*200,'average_speed'] = convert_speed(r[x].get('average_speed', '-')) 
        activities.loc[x + (page-1)*200,'max_speed'] = convert_speed(r[x].get('max_speed', '-'))
        activities.loc[x + (page-1)*200,'average_cadence'] = r[x].get('average_cadence', '-')
        activities.loc[x + (page-1)*200,'average_watts'] = r[x].get('average_watts', '-') 
        activities.loc[x + (page-1)*200,'max_watts'] = r[x].get('max_watts', '-')
        activities.loc[x + (page-1)*200,'weighted_average_watts'] = r[x].get('weighted_average_watts', '-')
        activities.loc[x + (page-1)*200,'average_heartrate'] = r[x].get('average_heartrate', '-') 
        activities.loc[x + (page-1)*200,'max_heartrate'] = r[x].get('max_heartrate', '-') 
        activities.loc[x + (page-1)*200,'kilojoules'] = r[x].get('kilojoules', '-') 
        activities.loc[x + (page-1)*200,'suffer_score'] = r[x].get('suffer_score', '-')
        activities.loc[x + (page-1)*200,'pr_count'] = r[x]['pr_count']
        activities.loc[x + (page-1)*200,'achievement_count'] = r[x]['achievement_count']
        activities.loc[x + (page-1)*200,'external_id'] = r[x]['external_id']
        
    print("Processing:", page, "page")
    # increment page
    page += 1

print("Total:", len(activities), "activities")

# Export your activities file as a csv 
# to the folder you're running this script in
activities.to_csv('strava_activities.csv')
