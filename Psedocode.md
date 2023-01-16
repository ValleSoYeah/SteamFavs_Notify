### Update List
- load friendlist
- load favorites table
- get missing IDs via Steam-Names
- update and save new favorites table

### Initialize requests
- load target table
- create dict with empty values

### Loop
- for all target entries
- request summary for target id
- if online and game in list
- if not already in dict
- update dict and send key and value to telegram

- if not online or game not in list
- set value to empty

- pause
- resume loop