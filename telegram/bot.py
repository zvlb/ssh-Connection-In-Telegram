# -*- coding: utf-8 -*-
import config
import allMessage
import telebot
import paramiko
import os
import sys
import time

bot = telebot.TeleBot(config.botToken)

class User:
    def __init__(self, userChatId):
        self.userChatId = userChatId

    def userName(self, userName):
        self.userName = userName
    
    def sshUser(self, sshUser):
        self.sshUser = sshUser

    def sshPassword(self, sshPassword):
        self.sshPassword = sshPassword

    def sshHost(self, sshHost):
        self.sshHost = sshHost

    def cdCommand(self, cdCommand):
        self.cdCommand = cdCommand

    def userStep(self, userStep):
        self.userStep = userStep
        #(If user for chatId) = None - user not activate
        #step = 1 - wait everything
        #step = 2 - activ

knownUsers = {}

#
#
#Pass all message(exclude /start, /on, /help), if user not activate:
@bot.message_handler(func=lambda message: \
                    ((knownUsers.get(message.chat.id) == None) or (knownUsers.get(message.chat.id) == 1)) \
                    and (message.text != '/start') and (message.text != '/on') \
                    and (message.text != '/help'), content_types=["text"])
def pass_message(message):
    pass

#
#
#Message /start after and before register user
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id) == None, commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['start_AfterAuthorized'])

@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['start_BeforeAuthorized'])
#
#
#Message /help after and before register user
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id) == None, commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['help_AfterAuthorized'])

@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, allMessage.commands['help_BeforeAuthorized'])

#
#
#Message /aboutBot
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['aboutbot'])
def send_aboutBot(message):
    bot.send_message(message.chat.id, allMessage.commands['aboutbot'])

#
#
#User information:
@bot.message_handler(func=lambda message: True, commands=['information'])
def test_user(message):
    data = 'UserName: ' + knownUsers.get(message.chat.id).userName + '\n' +\
            'Ssh user: ' + knownUsers.get(message.chat.id).sshUser + '\n' +\
            'host(IP) for ssh connection: ' + knownUsers.get(message.chat.id).sshHost + '\n' +\
            'Your location on the server (pwd): ' + knownUsers.get(message.chat.id).cdCommand
    bot.send_message(message.chat.id, data)

#
#
#Activate, and deactivation bot. 
@bot.message_handler(func=lambda message: True, commands=['on'])
def activate_user(message):
    if knownUsers.get(message.chat.id) == None:
        newUser = User(message.chat.id)
        newUser.userName = ''
        newUser.sshUser = config.sshUser
        newUser.sshPassword = config.sshPassword
        newUser.sshHost = config.sshHost
        newUser.cdCommand = config.sshHomeDirectory
        newUser.userStep = 1
        knownUsers[message.chat.id] = newUser

        password = bot.send_message(message.chat.id, "Enter the bot password:")
        bot.register_next_step_handler(password, check_password)
    elif knownUsers.get(message.chat.id).userStep == 2:
        bot.send_message(message.chat.id, "You are already authorized on this bot")

def check_password(message):
    if message.text == config.botPassword:
        knownUsers.get(message.chat.id).userStep = 2
        knownUsers.get(message.chat.id).userName = message.chat.first_name

        bot.send_message(message.chat.id, "Ok password. Welcome.")   
    else:
        password = bot.send_message(message.chat.id, "Wrong password. Try again:")
        bot.register_next_step_handler(password, check_password)


@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['off'])
def deactivate_user(message):
    knownUsers.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Bye")

#
#
#Set ssh user and ssh password
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['setsshuser'])
def request_ssh_user(message):
    knownUsers.get(message.chat.id).userStep = 1
    sshUser = bot.send_message(message.chat.id, "Enter the ssh user:")
    bot.register_next_step_handler(sshUser, add_ssh_user)

def add_ssh_user(message):
    if ((config.rootPermission) or (message.text != 'root')):
        knownUsers.get(message.chat.id).sshUser = message.text
        sshPassword = bot.send_message(message.chat.id, "Enter the ssh password:")
        bot.register_next_step_handler(sshPassword, add_ssh_password)
    else:
        bot.send_message(message.chat.id, "Root not allowed")

def add_ssh_password(message):
    knownUsers.get(message.chat.id).userStep = 2
    knownUsers.get(message.chat.id).sshPassword = message.text


#
#
#Set host(IP) for ssh connection:
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, commands=['setsshhost'])
def request_ssh_host(message):
    knownUsers.get(message.chat.id).userStep = 1
    sshDomain = bot.send_message(message.chat.id, "Enter domain(ip) for ssh connection:")
    bot.register_next_step_handler(sshDomain, add_ssh_host)

def add_ssh_host(message):
    knownUsers.get(message.chat.id).userStep = 2
    knownUsers.get(message.chat.id).sshHost = message.text

#
#
#Check exist sshUser:
@bot.message_handler(func=lambda message: \
                    ((knownUsers.get(message.chat.id).userStep == 2) and \
                    (knownUsers.get(message.chat.id).sshUser == '') and \
                    (knownUsers.get(message.chat.id).sshPassword == '')), \
                    content_types=["text"])
def ssh_user_not_exist(message):
    bot.send_message(message.chat.id, "Ssh user not exist. Use /setsshuser or /help")

#
#
#Check exist sshHost:
@bot.message_handler(func=lambda message: \
                    ((knownUsers.get(message.chat.id).userStep == 2) and \
                    (knownUsers.get(message.chat.id).sshHost == '')), \
                    content_types=["text"])
def ssh_user_not_exist(message):
    bot.send_message(message.chat.id, "Ssh host not exist. Use /setsshhost or /help")

#
#
#Do ssh command:
@bot.message_handler(func=lambda message: \
                    knownUsers.get(message.chat.id).userStep == 2, content_types=["text"])
def do_ssh_command(message):
        #check and remember 'cd'-command
        if (message.text[0:3] == 'cd '):
            if knownUsers.get(message.chat.id).cdCommand[-1] != '/':
                knownUsers.get(message.chat.id).cdCommand += '/'
            if message.text[3] == '/':
                knownUsers.get(message.chat.id).cdCommand = message.text.split()[1]
            elif message.text[3:5] == '..':
                flag = knownUsers.get(message.chat.id).cdCommand.split('/')
                knownUsers.get(message.chat.id).cdCommand = '/'
                i = 0
                for element in flag:
                    if ((i == 0) or (i == len(flag)-2) or (i == len(flag)-1)):
                        i += 1
                        continue
                    knownUsers.get(message.chat.id).cdCommand += element + '/'
                    i += 1
            else:
                bot.send_message(message.chat.id, message.text[3:5])
                if knownUsers.get(message.chat.id).cdCommand[-1] =='/':
                    knownUsers.get(message.chat.id).cdCommand += message.text.split()[1]
                else:
                    knownUsers.get(message.chat.id).cdCommand += '/' + message.text.split()[1]
        #ban 'vi', 'less', 'more', 'tail -f':
        elif ((message.text[0:3] == 'vi ') or (message.text[0:5] == 'less ') or \
            (message.text[0:5] == 'more ') or (message.text[0:8] == 'tail -f ')):
                bot.send_message(message.chat.id, "Please don't use dynamic command")
        #Do ssh command:
        else:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(hostname=knownUsers.get(message.chat.id).sshHost, \
                            username=knownUsers.get(message.chat.id).sshUser,
                            password=knownUsers.get(message.chat.id).sshPassword)
                sshCommand = 'cd ' +knownUsers.get(message.chat.id).cdCommand + '; ' + \
                            message.text
                stdin, stdout, stderr = client.exec_command(sshCommand)
                data = stdout.read() + stderr.read()
                if (sys.getsizeof(data) < 34):
                    pass
                elif (sys.getsizeof(data) > 3000):
                    bot.send_message(message.chat.id, \
                                "Answer from server is too large")
                else:
                    bot.send_message(message.chat.id, data)
                client.close()
            except Exception as e:
                bot.send_message(message.chat.id, e)

            #log user actions:
            if config.logging:
                logFile = open(config.logFile, 'a')
                logFile.write("User chat id: '" + str(knownUsers.get(message.chat.id).userChatId) + \
                            "'; User name: '" + str(knownUsers.get(message.chat.id).userName) + \
                            "'; Command: '" + str(sshCommand) + "'\n") 
                logFile.close()

        

while True
    if __name__ == '__main__':
        bot.polling(none_stop=True)
    time.sleep(10)
