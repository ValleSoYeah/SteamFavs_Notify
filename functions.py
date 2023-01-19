import numpy as np
import pandas as pd
from urllib.request import urlopen
import json
from time import localtime, strftime
import requests

def get_friend_IDs(steamid, APIkey):
    URL = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={APIkey}&steamid={steamid}&relationship=friend"
    file = urlopen(URL)
    content = file.read().decode('utf-8')
    friendlist = json.loads(content)
    friendlist = pd.DataFrame(friendlist["friendslist"]["friends"])
    print(f"Friendlist with {friendlist.shape[0]} entries imported from SteamAPI")
    return friendlist["steamid"]

def get_friend_names(friend_IDs, APIkey):
    print("Fetching friend names")
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
    #include timestamp and friend list length in name
    favs.to_csv("my_favorites.csv", sep=";", index=False)
    return favs

def check_fav_status(favs, APIkey):
    notify={}
    keys=["personaname", "steamid", "gameextrainfo"]
    for n in range(favs.shape[0]):
        id= favs.iloc[n]["steamid"]
        games= [x.strip() for x in favs.iloc[n]["games"].split(",")]
        URL = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={APIkey}&steamids={id}"
        file = urlopen(URL)
        content = file.read().decode('utf-8')
        friendstatus = json.loads(content)
        try:
            friendstatus = friendstatus["response"]["players"][0]
            name = friendstatus["personaname"]
            try:
                game = friendstatus["gameextrainfo"]
                if game in games:
                    notify[name] = game
            except: 
                notify[name] = ""
        except:
            continue
    return notify


def check_for_change(hits, notify):
    changed = False
    for entry in hits.keys():
        if notify[entry] != hits[entry]:
            notify[entry] = hits[entry]
            if notify[entry] != "":
                changed = True
    return notify, changed


def check_loop(notify, favs, APIkey, sleep=10, iter=10):
    x=0
    while x<iter:
        hits = check_fav_status(favs, APIkey)
        notify, my_send = check_for_change(hits, notify)
        if my_send == True:
            for i in notify.keys():
                if notify[i] != "":
                    return True, i, notify[i]
                    
        else:
            print(".")
            return False, i, notify[i]
        time.sleep(sleep)
        x +=1

def send_message(message, bot_token, telegram_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={telegram_id}&text={message}"
    requests.get(url).json()
    print(f"{strftime('%H:%M:%S', localtime())}: Just sent this message via Telegram: '{message}'")