from openai import OpenAI
from discord.ext import commands
from discord import app_commands
import discord
from time import time
import random
import functools
import json

# ---------- Global variables ----------
# bot settings
enabled = True
whitelistEnabled = False
whitelistedChannels = []
threshold = 7

# variables to limit message sending rate
lastMessageRecieved = 0
rateLimit = 5 #seconds

# handle custom discord emojis
emojiFile = open("emojis.lookup", "r")
emojis = emojiFile.readlines()
emojiFile.close()
numEmojis = len(emojis)

# ---------- Load settings ----------
settingsFile = open("bot.settings", "r") # Read from file
settingsJSON = settingsFile.read()
settingsFile.close()

if len(settingsJSON) > 0:
    settings = json.loads(settingsJSON) # convert string read from file to dictionary
    enabled = settings["enabled"] # load those values from dictionary
    whitelistEnabled = settings["whitelistEnabled"]
    whitelistedChannels = settings["whitelistedChannels"]
    threshold = settings["threshold"]

# ---------- Saving ----------
def save():
    settingsDict = { "enabled": enabled, 
                     "whitelistEnabled": whitelistEnabled,  
                     "whitelistedChannels": whitelistedChannels,
                     "threshold": threshold 
                   }
    
    settingsJSON = json.dumps(settingsDict);
    settingsFile = open("bot.settings", "w")
    settingsFile.write(settingsJSON)
    settingsFile.close()
    
# ---------- Intialize ChatGPT ----------
gptKeyFile = open("gpt.key", "r") # open API key file.
gptAPIKey = gptKeyFile.read()
gptKeyFile.close()

AIclient = OpenAI(
  api_key = gptAPIKey
)

# ---------- Initialize Discord bot ----------
discordKeyFile = open("discord.key", "r")
discordAPIkey = discordKeyFile.read()
discordKeyFile.close()

client = commands.Bot(command_prefix = ")", intents=discord.Intents.all())

@client.event
async def on_ready():
    print("The Mean Detector is ready to eliminate meanness")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")
    except:
        print("ur codes fucking broken lmao")

# ---------- ChatGPT Functions ----------
def askChatGPT(prompt):  #gets response from ChatGPT
    completion = AIclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def generateQuestion(message):
    #return f"Please determine whether the given message is mean or not. If it is mean, respond with a message pointing out how mean they were. Guilt trip the sender of the message a little. Add emoticons like :( or :((( and include some discord emojis by saying \"emoji\" and append a number from 1 to {numEmojis} inclusive with no spaces. Say stuff similar to \"THATS MEAN!!! :(((\" and \"wtf thats so mean stop doing that :(\". Please do not say these examples verbatim. Otherwise, if the message is not deemed to be mean, respond with \"Not mean\" with no punctuation or whitespace. Please judge with a sensitivity of {sensitivity}, which is a scale from 0 to 10. A sensitivity of 0 means saying everything except the meanest things, like racial slurs, is not mean. A sensitivity of 10 means catching everything that could possibly be interpreted as mean in any way, and 5 means only catching the things that are *very* mean. Lower sensitivity values are more lenient and higher values are stricter. The message is: \"{message}\""
    return f"Please give me a meanness score of how mean the following message is. The meanness score is a scale from 0 to 10. Messages should be given lower scores if they are not mean or not that mean. For example, \"Stop saying that please\" would be ~4 and \"You\'re amazing!\" would be ~0. Meaner messages are given higher scores. For example: \"I hate you!\" would be given a ~8, and slurs or other mean names would be given 9s or 10s. If the meanness score is above {threshold}, respond with a message pointing out how mean they were. Guilt trip the sender of the message a little. Add emoticons like :( or :((( and include some discord emojis by saying \"emoji\" and append a number from 1 to {numEmojis} inclusive with no spaces. Say stuff similar to \"THATS MEAN!!! :(((\" and \"wtf thats so mean stop doing that :(\". Please do not say these examples verbatim. If possible, try to respond in context directly to what the message says. Otherwise, if the message is not mean, simply respond with \"Not mean\" with no punctuation or whitespace. Do not include the meanness score in your response. The message is: \"{message}\""

async def unblocker(prompt): # gets response from ChatGPT without pausing execution
    nonblock = functools.partial(askChatGPT, prompt)
    return await client.loop.run_in_executor(None, nonblock)

# ---------- Bot Commands ----------
@client.tree.command(name="enable", description="Enables the bot :)")
async def enable(interaction: discord.Interaction):
    global enabled
    enabled = True
    await interaction.response.send_message("Bot Enabled")

@client.tree.command(name="disable", description="Disables the bot :(")
async def disable(interaction: discord.Interaction):
    global enabled
    enabled = False
    await interaction.response.send_message("Bot Disabled")

@client.listen("on_message")
async def on_message(message):
    if enabled:
        global lastMessageRecieved
        if(time() - lastMessageRecieved > rateLimit):
            if message.author.id != client.user.id: #ensure the bot doesnt respond to itself
                chatGPTOpinion = await unblocker(generateQuestion(message.clean_content)) # Get result from ChatGPT in a non-blocking way to prevent it from freezing
                if(chatGPTOpinion.lower().replace(" ", "") != "notmean"):
                    for i in range(numEmojis):
                        chatGPTOpinion = chatGPTOpinion.replace("emoji" + str(i), emojis[i])
                        chatGPTOpinion = chatGPTOpinion.replace("Emoji" + str(i), emojis[i]) #Edge case when ChatGPT decides to capitalize emoji
                    await message.reply(chatGPTOpinion)
        lastMessageRecieved = time()

client.run(discordAPIkey)