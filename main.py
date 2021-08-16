# SnekBot - A bot for learning how to create a Discord bot
#
# This Discord bot is built utilizing the "Code a Discord Bot with Python"
# tutorial on YouTube by freeCodeCamp, and the discord.py library.
# Several modifications have been made to the program to personalize it 
# and allow for more functionality. Essentially, it is an uwu bot.
#
# @author robot-artificer
# @version 1.7

# Importing necessary libraries
import discord
import os
import requests
import json
import random
from replit import db # replit database functionality
from keepAlive import keepAlive # web server code for replit

# Importing lists from commands.py
from commands import hello, uwuWords, sadWords, happyWords 
from commands import commands, commandFacts, helpCommands
from commands import initialKeys, triggerWords, snekBotPrompt
from commands import defaultMsg, motivateMsg, bezosPrompt

# Creating a client variable set to the discord client method
client = discord.Client()

options = [] # Initializing an empty list

# Startup actions
# Add active to database keys, and set value to "True"
if "active" not in db.keys():
    db["active"] = True

# Create keys in database
for i in initialKeys:
    if str(i) not in db.keys():
        db[str(i)] = []

# getQuote function returns a random quote from the Zen Quotes api
#
def getQuote():
    # Request data from the Zen Quotes api
    response = requests.get("https://zenquotes.io/api/random")
    
    # Convert into json format
    json_data = json.loads(response.text)

    # Parse json quote into string and return
    quote = json_data[0]["q"] + " ~ " + json_data[0]["a"]
    return quote

# updateMsg adds a new phrase as a value to the list from the provided
# db key
# 
# @param key        The database key to access the stored list
# @param message    The message to add to the stored list
def updateMsg(key, message):
    # Check if the provided key exists in the database
    if key in db.keys():
        # Add message to given key value-list
        newMsg = db[str(key)]
        newMsg.append(message)
        db[str(key)] = newMsg
    else:
        # Add message to a new list for the given key
        db[str(key)] = [message]  

# deleteMsg removes a phrase from the provided db key
#
# @param key    The database key to access the stored list
# @param index  The index of the item in the stored list to delete
def deleteMsg(key, index):
    # Get a copy of the list for the given key
    keyList = db[str(key)]

    # Check to make sure the provided index is valid
    if len(keyList) > index:

        # Delete string at given list index then store in database
        del keyList[index]
        db[str(key)] = keyList

# optionsLogic determines the list of options of phrases for SnekBot to
# use in its replies. This method uses multiple conditionals to parse 
# the supplied message to be able to respond in an "appropriate" manner
#
# @param message    The message sent by the user
# @return           The list of options selected
def optionsLogic(message):
    if any(word in message for word in sadWords):
        options = motivateMsg + list(db["sad"]) + list(db["happy"]) 
    elif any(word in message for word in triggerWords) or any(word in message for word in list(db["trigger"])):
        options = defaultMsg + list(db["random"]) + list(db["butts"]) + list(db["sad"]) + list(db["happy"]) + otherKeyOptions()
    elif any(word in message for word in happyWords):
        options = motivateMsg + defaultMsg + list(db["happy"]) + list(db["random"]) + otherKeyOptions()
    elif any(word in message for word in bezosPrompt):
        options = list(db["bezos"])
    
    return options

# otherKeyOptions creates a list of phrases from database keys that
# are not included in the initialKeys list
#
# @return   The list of phrases from all the keys not in initialKeys
def otherKeyOptions():
    otherList = []  # List to hold multiple lists from db
    
    # Traverse keys
    for i in db.keys():
        # Check if key is not in intialKeys or "active"
        if i not in initialKeys and i != "active":
            # Add database contents list to otherList
            otherList = otherList + list(db[str(i)])
    
    return otherList

# Events for Discord Client
# on_ready event
@client.event
async def on_ready():
    # Display message when bot logs on
    print("{0.user} has logged in!".format(client))

# on_message events
@client.event
async def on_message(message):
    # Check if message is from the bot itself
    if message.author == client.user:
        return

    msg = message.content  # Set shortcut for message.content

    # Check if message is a greeting and respond
    if msg.lower().startswith(tuple(hello)):
        await message.channel.send("Hi " + str(message.author.display_name) + "!")

    # Check uwu status
    if msg.lower().startswith(tuple(uwuWords)) or any(word in msg.lower() for word in uwuWords):
        await message.channel.send(random.choice(uwuWords))

    # Display random zen quote
    if msg.startswith("!zen"):
        quote = getQuote()
        await message.channel.send(quote)

    # Command to list all commands
    if msg.lower().startswith(tuple(helpCommands)):
        await message.channel.send("It sounds like you need help! \nThese are the commands you can use:")

        # Loop to display all the commands from the specified lists
        for i in range(len(commands)):
            await message.channel.send(commands[i].ljust(10, " ") + commandFacts[i])

    # Clear database command
    if msg.startswith("$clear"):

        # Clear database then reset flags and keys
        db.clear()
        db["active"] = True
        for i in initialKeys:
            if str(i) not in db.keys():
                db[str(i)] = []
        await message.channel.send("Database has been cleared.")

    # Responding to specific words
    # Check if bot is active and if user requests bot response
    if db["active"] and msg.lower().startswith(tuple(snekBotPrompt)):
        # Set the options list to the return value of optionsLogic
        # by passing in the lowercase values of the supplied message
        options = optionsLogic(msg.lower())
        
        # Have the bot reply with a random choice based on the options list
        await message.channel.send(random.choice(options))

    # Add message to the database
    if msg.startswith("$add"):
        # Parse message based on the assumption that the message is 3 parts,
        # then displayed as verification
        newMsg = msg.split("$add ", 1)[1]
        await message.channel.send("Adding..." + str(newMsg))
        newKey = newMsg.split()[0]
        await message.channel.send("Key: " + str(newKey))
        newPhrase = str(newMsg).split(" ", 1)[1]
        await message.channel.send("Phrase: " + str(newPhrase))
        
        # Call updateMsg method by passing in values
        updateMsg(str(newKey), newPhrase)
        await message.channel.send("New message added.")

    # Delete message from the database
    if msg.startswith("$del"):
        # Parse message based on the assumption that the message is 3 parts,
        # with a number at the end
        tempMsg = msg.split("$del ", 1)[1]
        tempKey = tempMsg.split()[0]
        tempIdx = int(str(tempMsg).split(" ", 1)[1])

        # Check if the provided key is in the database
        if str(tempKey) in db.keys():
            # Call deleteMsg method by passing in values
            deleteMsg(tempKey, tempIdx)

        # Display updated database list
        await message.channel.send(list(db[str(tempKey)]))

    # Display the contents of the database
    if msg.startswith("$keys"):
        # Loop through the database keys and display the values
        for i in db.keys():
            await message.channel.send("List for {" + i + "} key: " + str(db[str(i)]))
    
    # Delete specific database keys
    if msg.startswith("$rmKey"):
        # Parse message to find key
        tempKey = msg.split("$rmKey ", 1)[1]
        # Check if key exists in database
        if str(tempKey) in db.keys():
            del db[str(tempKey)]
            await message.channel.send("The database key has been removed.")
        else:
            await message.channel.send("There is no db key " + tempKey)

    # Display the contents of triggerWords
    if msg.startswith("!tw"):
        await message.channel.send("These are the current trigger words: ")
        await message.channel.send(str(triggerWords))
        if "trigger" in db.keys():
            await message.channel.send(list(db["trigger"]))

    # Bot Activation switches to set bot response ability
    if msg.startswith("$active"):
        value = msg.split("$active ", 1)[1]
        # Check if message is flagged true or false
        if value.lower() == "true":
            db["active"] = True
            await message.channel.send("Bot is activated.")
        else:
            db["active"] = False
            await message.channel.send("Bot is deactivated.")

    # Testing function
    if msg.startswith("$test"):
        testList = otherKeyOptions()
        await message.channel.send(list(testList))

# Webserver keepAlive function
keepAlive()

# Client token
client.run(os.getenv('D_TOKEN'))