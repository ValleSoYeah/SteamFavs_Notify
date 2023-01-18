from functions import *
from credentials import my_SteamID, my_APIkey
import pandas as pd

# use credentials to get steamID of entire friendlist
my_friend_IDs = get_friend_IDs(my_SteamID, my_APIkey)

#check timestamp in csv, only get friend names if longer ago than x hours or if friend list got longer

# look up the steam names for all IDs in friendlist
my_friend_names = get_friend_names(my_friend_IDs, my_APIkey)

#load table of favorites
#include wildcard characters for file name
my_favs = pd.read_csv("my_favorites.csv", delimiter=";")

# fill empty IDs in favorites
my_favs = fill_empty_ids(my_favs, my_friend_names)

# initialize empty dict for notifications
my_notify = {}
for i in range(my_favs.shape[0]):
    my_notify[my_favs.iloc[i]["steamname"]]=""

#check repeatedly for changes
check_loop(my_notify, my_favs, my_APIkey, sleep=60, iter=100)