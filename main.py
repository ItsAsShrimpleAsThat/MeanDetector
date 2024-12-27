from openai import OpenAI
from discord.ext import commands
from discord import app_commands
import discord

# ---------- Global variables ----------
enabled = False
whitelistEnabled = False;
whitelistedChannels = []

# ---------- Intialize ChatGPT ----------
gptKeyFile = open("gpt.key", "r") # open API key file.
gptAPIKey = gptKeyFile.read()
gptKeyFile.close()

client = OpenAI(
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

# ---------- Bot Commands ----------
@client.tree.command(name="enable", description="Enables the bot")
async def enable(interaction: discord.Interaction):
    await interaction.response.send_message("please fucking work i beg you")

@client.listen("on_message")
async def on_message(message):
    if message.author.id != client.user.id:
        await message.reply("test")

client.run(discordAPIkey)

"""
completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "test test test test"}
  ]
)

print(completion.choices[0].message.content);
"""