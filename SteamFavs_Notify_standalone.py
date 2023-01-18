import pandas as pd
from urllib.request import urlopen
import json
import requests
from time import time, sleep, localtime, strftime

#from credentials import * ############################################################################################TODO

my_SteamID = "76561198048688318"
my_APIkey = "3B90B4B6F5209358DD991B763FF56CE9"
my_bot_token = "5924291011:AAGFvOa2BpPUwWOBLxJmUYvYojENvcjOp0M"
my_telegram_id = "108811623"

my_favs = pd.DataFrame([['Schniin', 'Pail', 76561198059254917, 'Warhammer: Vermintide 2, Test'],
 ['Nils', 'Smallboy_Slin', 76561197981033122, 'Deep Rock Galactic, SCUM'],
 ['Grady', '[WC] Scott Sterling', 76561198026715831, 'Sands of Salzaar'],
 ['Chrisse', 'chrisse286', 76561198068931354, 'Dota 2']], columns=["friend", "steamname", "steamid", "games"])


def get_friend_IDs(steamid, APIkey):
    """Uses a provided SteamID and matching APIkey to return a DataFrame containing the SteamIDs of all friends"""
    URL = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIkey}&steamid={steamid}&relationship=friend"
    file = urlopen(URL)
    content = file.read().decode('utf-8')
    friendlist = json.loads(content)
    friendlist = pd.DataFrame(friendlist["friendslist"]["friends"])
    print(f"Imported friendlist with {friendlist.shape[0]} entries from Steam")
    return friendlist["steamid"]


def get_friend_names(friend_IDs, APIkey):
    """Uses a list of SteamIDs to """
    print("Updating friend's steamnames")
    keys=["steamid", "personaname"]
    out=[]
    for n, id in enumerate(friend_IDs):
        if n == 0 or (n+1)%10 == 0:
            print(f"{n+1} of {friend_IDs.shape[0]}")
        URL = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIkey}&steamids={id}"
        file = urlopen(URL)
        content = file.read().decode('utf-8')
        friendstatus = json.loads(content)
        try:
            friendstatus = friendstatus["response"]["players"][0]
            out.append([friendstatus.get(key) for key in keys])
        except:
            continue
    return pd.DataFrame(out, columns=["steamid", "steamname"]).sort_values("steamname")


def fill_empty_ids(favs, friend_names):
    favs = pd.merge(favs, friend_names, on="steamname", suffixes=("","_2"))
    favs["steamid"]= favs["steamid_2"]
    favs.drop("steamid_2", axis=1, inplace=True)
    favs.to_csv("my_favorites.csv", sep=";", index=False)
    return favs


def check_for_matches(favs, APIkey):
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
                matches[friend_name] = ""
        except:
            continue
    return matches #returns dictionary of favorite friends with either empty value or game name, if it is a match


def check_for_change(matches, notify):
    has_changed = False
    for entry in matches.keys():
        if notify[entry] != matches[entry]:
            notify[entry] = matches[entry]
            if notify[entry] != "":
                has_changed = True
    return notify, has_changed


def send_message(message, bot_token, telegram_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={telegram_id}&text={message}"
    requests.get(url).json()
    print(f"{strftime('%H:%M:%S', localtime())}: Just sent this message via Telegram: '{message}'")

######################################################################################################
'''
# use credentials to get steamID of entire friendlist ########################################TODO
my_friend_IDs = get_friend_IDs(my_SteamID, my_APIkey)

# look up the steam names for all IDs in friendlist
my_friend_names = get_friend_names(my_friend_IDs, my_APIkey)

#load table of favorites
my_favs = pd.read_csv("my_favorites.csv", delimiter=";") 

# fill empty IDs in favorites
my_favs = fill_empty_ids(my_favs, my_friend_names)'''

# initialize empty dict for notifications
my_notify = {}
for i in range(my_favs.shape[0]):
    my_notify[my_favs.iloc[i]["steamname"]]=""

#check repeatedly for changes
check_interval_sec = 10
max_runtime_hours = 0.01
end_time = time() + (max_runtime_hours * 3600)

while time() < end_time:
    start_time = time()
    matches = check_for_matches(my_favs, my_APIkey)
    my_notify, has_changed = check_for_change(matches, my_notify)
    if has_changed == True:
        for i in my_notify.keys():
            if my_notify[i] != "":
                message = f"{i} is now playing {my_notify[i]}!"
                send_message(message, my_bot_token, my_telegram_id)
    else:
        print(f"{strftime('%H:%M:%S', localtime())} - ")
    sleep(start_time + check_interval_sec - time())

