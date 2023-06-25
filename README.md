# UPML Killer bot
This bot was created for the game "Killer" in the Ugra Physics and Mathematics Lyceum.

## Deploy
1. Set env variables (`.env.example`):
    * TOKEN - Telegram bot token
    * DB_FILE - DB file name
    * LOG_FILE - Log file name
    * BETTER_CALL_SAUL - How to contact with admin
    * ADMIN_ID - Telegram id admin

2.  Launch
    * Local
      ```
      pip install -r requirements.txt
      python src/main.py
      ```
    * Docker
      ```
      docker-compose up
      ```

## TODO
- [ ] - Refactor all this shit
- [ ] - Make transactions in the database
