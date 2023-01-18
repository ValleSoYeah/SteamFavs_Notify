from functions import *
from credentials import *
import pandas as pd
from time import time, sleep, localtime, strftime

# use credentials to get steamID of entire friendlist
my_friend_IDs = get_friend_IDs(my_SteamID, my_APIkey)

# look up the steam names for all IDs in friendlist
my_friend_names = get_friend_names(my_friend_IDs, my_APIkey)

#load table of favorites
my_favs = pd.read_csv("my_favorites.csv", delimiter=";")

# fill empty IDs in favorites
my_favs = fill_empty_ids(my_favs, my_friend_names)

# initialize empty dict for notifications
my_notify = {}
for i in range(my_favs.shape[0]):
    my_notify[my_favs.iloc[i]["steamname"]]=""

#check repeatedly for changes
check_interval_sec = 6
max_runtime_hours = 1
run = True

loop_start_time = time()
while run:
    start_time = time()
    hits = check_fav_status(my_favs, my_APIkey)
    my_notify, changed = check_for_change(hits, my_notify)
    if changed == True:
        for i in my_notify.keys():
            if my_notify[i] != "":
                message = f"{i} is now playing {my_notify[i]}!"
                send_message(message, my_bot_token, my_telegram_id)
    else:
        print(f"{strftime('%H:%M:%S', localtime())}")
    sleep(start_time + check_interval_sec - time())
    runtime = time() - loop_start_time
    if  runtime > (36 * max_runtime_hours):
        break
print(f"Total runtime was {int(runtime//3600)} h, {(int(runtime%3600)//60)} min and {int(runtime%60)} sec")
