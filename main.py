from openai import OpenAI
from discord.ext import commands
from discord import app_commands
import discord
from time import time
import random

# ---------- Global variables ----------
meanResponses = []
enabled = False
whitelistEnabled = False
whitelistedChannels = []
sensitivity = 5;

lastMessageRecieved = time()
rateLimit = 5

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

def askChatGPT(prompt):
    completion = AIclient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "user", "content": prompt}
        ],
    )
    return completion.choices[0].message.content

def generateQuestion(message):
    return f"Please determine whether the given message is mean or not. If it is mean, respond with \"Mean\". Otherwise, respond with \"Not mean\". Please judge with a sensitivity of {sensitivity}, where 0 sensitivity means letting almost everything slide, 10 means basically catching everything that could possibly be interpreted as mean in any way, and 5 means only catching the things that are *intentionally* mean. The message is: \"{message}\""

# ---------- Bot Commands ----------
@client.tree.command(name="enable", description="Enables the bot")
async def enable(interaction: discord.Interaction):
    await interaction.response.send_message("please fucking work i beg you")

@client.listen("on_message")
async def on_message(message):
    global lastMessageRecieved
    if(time() - lastMessageRecieved < rateLimit):
        return
    lastMessageRecieved = time()
    if message.author.id != client.user.id:
        chatGPTOpinion = askChatGPT(generateQuestion(message.clean_content))
        if(chatGPTOpinion == "Mean"):
            await message.reply(meanResponses[random.randint(0, len(meanResponses) - 1)])
        #await message.reply("Hi! I have not been programmed to say anything but this test message. If you see this, my code is probably working ok. If you are trying to have a conversation, please feel free to time me out for 10 minutes")

client.run(discordAPIkey)