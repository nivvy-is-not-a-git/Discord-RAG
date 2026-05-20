import discord
import asyncio
import ingest
import buffer
import os
from dotenv import load_dotenv

load_dotenv()

buffer.init_db()


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
token=os.getenv('DISCORD_TOKEN')

server = int(os.getenv('SERVER'))
IGNORE_CHANNELS=['remy-music']

 
@client.event
async def on_ready():
    guild = client.get_guild(server)
    for channel in guild.text_channels:
        if channel.name in IGNORE_CHANNELS:
            continue
        await ingest.scrape_history(channel)


client.run(token)