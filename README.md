# UPML Killer bot
This bot was created for the game "Killer" in the Ugra Physics and Mathematics Lyceum.

## Deploy
1. Set env variables (`.env.example`):
    * TOKEN - Telegram bot token
    * DB_FILE - DB file name
    * LOG_FILE - Log file name
    * BETTER_CALL_SAUL - How to contact with admin
    * ADMIN_ID - Admin Telegram ID 

2.  Launch
    * Local
      ```
      pip install -r ./requirements.txt
      python -m src
      ```
    * Docker
      ```
      docker-compose up -d --build
      ```

## Admin commands
*[ids] - DB IDs separated by a space*\
*[text] - any message*
- /check_users
- /list_alive
- /delete_users *[ids]*
- /kill *[ids]*
- /start_game
- /shuffle
- /message *[text]*

## TODO
- [ ] - Refactor all this shit
- [ ] - Make transactions in the database
