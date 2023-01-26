# SteamFavs_Notify - Get notified via Telegram when a favorite friend starts a favorite game

## How to set up runs in Google Cloud Functions (free tier)
### Steam
1.	[Get your SteamAPI-Key](https://steamcommunity.com/dev/apikey), you can use 127.0.0.1 as your domain.
2.	Get the SteamIDs of your friends from their profile-URLs (17-digit number)
### Telegram
1.	Create a Telegram-Bot
    - contact the botfather (https://telegram.me/botfather)
    -   create the bot and note your bot-token
2.	Get your TelegramID through the bot
    -    message your new bot once via Telegram (this also authorizes him to send you messages)
    -   replace the bot token in [this URL](https://api.telegram.org/bot{your_bot_token}/getupdates) and note the 9-digit number behind “id”

&nbsp;

### Google Cloud Project Setup
1.	Setup a Google Cloud account and create a project with billing enabled
2.	Activate billing reports export to BigQuery and set budget alerts
    -   Billing => Billing Export => Detailed Usage Cost => Create new BigQuery dataset
    -   Billing => Budgets & Alerts => Set a Budget at 10€ and alerts at 1-5% to be alerted if you don’t stay in free tier ()
3.	Get service account credentials
    - go to Cloud Functions => Create function. Enable all necessary APIs, this will create your default service account
    -   APIs & Services => Credentials => **your_project_ID**@appspot.gserviceaccount.com => Create Key (JSON)
4.	Save the key as a secret
    - Security => Secret manager => Create Secret 
    - Paste content of the JSON file in the “value” field
5.	Also save your other credentials (SteamID, APIkey, bot_token, telegram_id) as secrets
6.	Create a new Pub/Sub topic

&nbsp;

### Google Sheets
1.	Write your favs in a google sheets-document
    - organize in four columns: friend, steamname, steamid, games
    - write multiple games for one friend in the same cells and separate with a comma
    - name the sheet “my_favs”
    - create a second sheet in the same document named “cache”
2.	Share the document with your Google-Cloud appspot service account email (editor access)
3.	Get your sheets ID from the URL *https://docs.google.com/spreadsheets/d/{sheets_id}/edit*
    - Save your sheets_id as a secret in Google Cloud Cloud 

&nbsp;

### Cloud Functions Setup
1.	Create the Cloud Function
    - Cloud Functions => create function
    - Region: us-central1
    - Trigger: your Pub/Sub topic
    - Memory: 512 MB, Max instances: 1
    - Reference the secrets as environment variables with these names
        - *my_SteamID, my_APIkey, my_bot_token, my_telegram_id, sheet_id, appspot_service_acc*
2.	Deploy and test your function
    - **main.py:** paste from [*google-cloud-functions/SteamFavs_Notify_cloud.py*](https://github.com/ValleSoYeah/SteamFavs_Notify/blob/main/google-cloud-functions/SteamFavs_Notify_cloud.py)
    - **requirements.txt:** paste from [*google-cloud-functions/requirements.txt*](https://github.com/ValleSoYeah/SteamFavs_Notify/blob/main/google-cloud-functions/requirements.txt)
    - deploy the function, test-run it and check the logs
    - delete the multi-region storage bucket to avoid getting billed (!!!)
3.	Set-up a Cloud Scheduler job 
    - Define the frequency (i.e. every 10 minutes in the hours starting with 18-20 (*/10 18-20 * * *)
    - Define the target (your Pub/Sub topic)

&nbsp;

--- 

&nbsp;

## How to set up local runs with Google Sheets


    ```bash
    python --version
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    py -3 -m venv .venv
    .venv\scripts\activate
    pip install --upgrade pip
    pip install -r local/requirements.txt
    ```
- Instead of saving all credentials as secrets in the cloud, save them as shown in [*local/credentials.py*](https://github.com/ValleSoYeah/SteamFavs_Notify/blob/main/local/credentials.py)
- Run [*local/SteamFavs_Nofity_local_from_sheets.py*](https://github.com/ValleSoYeah/SteamFavs_Notify/blob/main/local/SteamFavs_Nofity_local_from_sheets.py)

&nbsp;

--- 

&nbsp;

## How to set up local runs from favorites stored in a csv-file
- Skip all steps for Google Cloud or Google Sheets
- Enter your favorites in [*local/favorites.csv*](https://github.com/ValleSoYeah/SteamFavs_Notify/blob/main/local/favorites.csv)


    ```bash
    python --version
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
    py -3 -m venv .venv
    .venv\scripts\activate
    pip install --upgrade pip
    pip install -r local/requirements.txt
    ```


