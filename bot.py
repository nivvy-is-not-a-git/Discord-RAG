import discord
import asyncio
import ingest, buffer, vector_search
import os
from dotenv import load_dotenv

load_dotenv()

buffer.init_db()


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
token=os.getenv('DISCORD_TOKEN')

server = int(os.getenv('DISCORD_SERVER'))   # type: ignore
IGNORE_CHANNELS=['remy-music']

 
@client.event
async def on_ready():
    print("bot ready")
    guild = await client.fetch_guild(server)
    print(f"guild: {guild.name}")
    channels = await guild.fetch_channels()
    text_channels = [c for c in channels if isinstance(c, discord.TextChannel)]
    print(f"channels: {[c.name for c in text_channels]}")
    query_string = input("enter query string: ")
    
    for channel in text_channels:
        print(f"checking channel: {channel.name}")
        if channel.name == 'remy-music':
            print(f"ingesting {channel.name}")
            await ingest.run_ingest(channel)
    print("ingest done, running search")
    results = vector_search.vsearch(query_string)
    print(results)
        
        



client.run(token)