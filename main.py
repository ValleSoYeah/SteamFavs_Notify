
from credentials import my_SteamID, my_APIkey

getList_URL = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={my_APIkey}&steamid={my_SteamID}&relationship=friend"
print(getList_URL)

import urllib

f = urllib.request.urlopen(getList_URL)
myfile = f.read()
print(myfile)
