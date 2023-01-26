# SteamFavs_Notify
Get notified via Telegram when a favorite friend starts a favorite game

Run

````bash
python --version
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
py -3 -m venv .venv
.venv\scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
````

---

## Next steps
### Deploy and Run in Cloud
- test build using a single script with Google Cloud Run
- store credentials in separate file
- manage fav-table as private Google Sheet (access through service-account)

&nbsp;

## The longterm vision:
### All communication and setup though a single Telegram-Bot
- Initialize the bot with your SteamID and SteamAPI-Key
- Send the Bot the steam name of a friend, and nickname and a game you want to be notified for
- More games can be added using the nickname and the name of the game
- games can be removed from the list
- notifications can be turned off for certain friends and/or games
