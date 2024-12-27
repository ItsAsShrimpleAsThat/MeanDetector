from openai import OpenAI
from discord.ext import commands
from discord import app_commands
import discord
from time import time
import random
import functools
import typing

# ---------- Global variables ----------
meanResponses = []
enabled = True
whitelistEnabled = False
whitelistedChannels = []
sensitivity = 1

lastMessageRecieved = 0
rateLimit = 5

emojiFile = open("emojis.lookup", "r")
emojis = emojiFile.readlines()
emojiFile.close()

numEmojis = len(emojis)

# ---------- Load responses ----------
responsesFile = open("mean.responses", "r")
meanResponses = responsesFile.readlines()
responsesFile.close();

# ---------- Intialize ChatGPT ----------
gptKeyFile = open("gpt.key", "r") # open API key file.
gptAPIKey = gptKeyFile.read()
gptKeyFile.close()

AIclient = OpenAI(
  api_key = gptAPIKey
)

discordKeyFile = open("discord.key", "r")
discordAPIkey = discordKeyFile.read()
discordKeyFile.close()

# ---------- Initialize Discord bot ----------
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

def blockingFunction():
    time.sleep(10)

def askChatGPT(prompt):
    completion = AIclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def generateQuestion(message):
    return f"Please determine whether the given message is mean or not. If it is mean, respond with a message pointing out how mean they were. Guilt trip the sender of the message a little. Add emoticons like :( or :((( and include some discord emojis by saying \"emoji\" and append a number from 1 to {numEmojis} inclusive with no spaces. Say stuff similar to \"THATS MEAN!!! :(((\" and \"wtf thats so mean stop doing that :(\". Please do not say these examples verbatim. Otherwise, if the message is not deemed to be mean, respond with \"Not mean\" with no punctuation or whitespace. Please judge with a sensitivity of {sensitivity}, which is a scale from 0 to 10. A sensitivity of 0 means saying everything except the meanest things, like racial slurs, is not mean. A sensitivity of 10 means catching everything that could possibly be interpreted as mean in any way, and 5 means only catching the things that are *very* mean. Lower sensitivity values are more lenient and higher values are stricter. The message is: \"{message}\""

async def unblocker(prompt):
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
            if message.author.id != client.user.id: 
                chatGPTOpinion = await unblocker(generateQuestion(message.clean_content))
                print(generateQuestion(message.clean_content))
                if(chatGPTOpinion.lower().replace(" ", "") != "notmean"):
                    #await message.reply(meanResponses[random.randint(0, len(meanResponses) - 1)])
                    for i in range(numEmojis):
                        chatGPTOpinion = chatGPTOpinion.replace("emoji" + str(i), emojis[i])
                    await message.reply(chatGPTOpinion)
                     #await message.reply("Hi! I have not been programmed to say anything but this test message. If you see this, my code is probably working ok. If you are trying to have a conversation, please feel free to time me out for 10 minutes")
        lastMessageRecieved = time()

client.run(discordAPIkey)