import base64
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from urllib.request import urlopen
import json
import requests
import pytz
from datetime import datetime

#########################################################################################################
# to run in Cloud Functions, all credentials need to be stored as environment variables with these names:
# my_APIkey, my_bot_token, my_telegram_id, my_spreadsheet_id, serv_acc
##########################################################################################################


def activate_fav_notify_sheets(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    try:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        print(f"Triggered by the Pub/Sub message: '{pubsub_message}'")
    except:
        print("Triggered by something other than a Pub/Sub message.")

    print(f"Script version number {os.environ['K_REVISION']}")

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    RANGE = 'A1:D100'

    # Loading environment variables.
    my_SteamID = os.environ["my_SteamID"]
    my_APIkey = os.environ["my_APIkey"]
    my_bot_token = os.environ["my_bot_token"]
    my_telegram_id = os.environ["my_telegram_id"]
    my_spreadsheet_id = os.environ["sheet_id"]
    serv_acc = eval(os.environ["appspot_service_acc"])

    
    #loading favlist from sheet
    #reducing memory-usage by overwriting same var in each step
    var = service_account.Credentials.from_service_account_info(serv_acc, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=var)
    var = service.spreadsheets().values().get(spreadsheetId=my_spreadsheet_id, range="my_favs!"+RANGE).execute()
    var = var.get('values', [])
    if not var:
        print('No data found.')
        return
    else:    
        my_favs= pd.DataFrame(var[1:], columns=var[0])
        print('Favs imported from GSheets!')

    #Loading last state of running games from chached sheet
    var = service.spreadsheets().values().get(spreadsheetId=my_spreadsheet_id,range="cache!"+RANGE).execute()
    var = var.get('values', [])
    my_notify = {}
    # reset chached state at first invocation of the day (after 18:00)
    if not var or datetime.now(pytz.timezone('Europe/Berlin')).strftime('%H:%M')[:4] == "18:0":
        for i in range(my_favs.shape[0]):
            my_notify[my_favs.iloc[i]["steamname"]]="-"
        print("State dictionary was reset")
    else:
        for i in range(len(var)):
            my_notify[var[i][0]] = var[i][1]
        print("Cached state imported from GSheets")
    

    def check_for_matches(favs, APIkey):
        """Returns dictionary of favorite friends with either empty value or game name, if it is a match"""
        matches={}
        for n in range(favs.shape[0]):
            id= favs.iloc[n]["steamid"]
            fav_games= [x.strip() for x in favs.iloc[n]["games"].split(",")]
            URL = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIkey}&steamids={id}"
            file = urlopen(URL)
            content = file.read().decode('utf-8')
            friendstatus = json.loads(content)
            try:
                friendstatus = friendstatus["response"]["players"][0] #fails if profile is not accessible
                friend_name = friendstatus["personaname"]
                try:
                    curr_game = friendstatus["gameextrainfo"] #fails if friend is not currently playing a game
                    if curr_game in fav_games: 
                        matches[friend_name] = curr_game
                except: 
                    matches[friend_name] = "-"
            except:
                continue
        return matches 

    def check_for_change(matches):
        """Checks whether any detected matches are new or reoccuring"""
        has_changed = False
        for entry in matches.keys():
            if my_notify[entry] != matches[entry]:
                my_notify[entry] = matches[entry]
                if my_notify[entry] != "-":
                    has_changed = True
        return my_notify, has_changed

    def send_message(message, bot_token, telegram_id):
        """Sends a message via the specified bot, to the specified telegram ID"""
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={telegram_id}&text={message}"
        requests.get(url).json()
        print(f"{datetime.now(pytz.timezone('Europe/Berlin')).strftime('%H:%M:%S')}: Just sent this message via Telegram: '{message}'")

     
    #Run code
    matches = check_for_matches(my_favs, my_APIkey)
    my_notify, has_changed = check_for_change(matches)
    if has_changed == True:
        for i in my_notify.keys():
            if my_notify[i] != "-":
                message = f"{i} is now playing {my_notify[i]}!"
                send_message(message, my_bot_token, my_telegram_id)
    else:
        print(f"{datetime.now(pytz.timezone('Europe/Berlin')).strftime('%H:%M:%S')} Nothing to report")
    
    #cache current state
    var=[]
    for key in my_notify:
        var.append([key, my_notify[key]])
    data = {'values' : var}
    service.spreadsheets().values().update(spreadsheetId=my_spreadsheet_id, body=data, range="cache!"+RANGE, valueInputOption='USER_ENTERED').execute()
