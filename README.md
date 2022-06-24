# ssh connection in Telegram

How it work (briefly):
- Put folder telegram/ on the server in the local network. (Need internet access)
- Сhange settings in telegram/config.py (look at the comments)
- Run /telegram/bot.py

# Screen:

![Image alt](https://raw.githubusercontent.com/vzemtsov/ssh-Connection-In-Telegram/master/screen.JPG)


# More info:


To use this bot u need:
1. Put folder telegram/ on the server in the local network. (Need internet access)
2. Create bot in telegram. Send "/newbot" to @BotFather.
3. Copy u API tokem. Send "/mybot" to @BotFather, select u bot, and select API token.
(looks something like 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11)
4. Paste u API token in telegram/config.py
5. Change all u want in telegram/config.py
6. Import telebot library
(pip install telebot)
7. Import paramico library
(pip install paramiko)
8. Start telegram.bot.py
