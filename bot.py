import discord
from discord import app_commands
from discord.ext import tasks
import ingest, buffer, vector_search
import os
from dotenv import load_dotenv

load_dotenv()

buffer.init_db()


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
token = os.getenv('DISCORD_TOKEN')

server = int(os.getenv('DISCORD_SERVER'))   # type: ignore
IGNORE_CHANNELS = ['rules', 'moderator-only']
PROCESS_INTERVAL_SECONDS = 30


@tasks.loop(seconds=PROCESS_INTERVAL_SECONDS)
async def process_pending_loop():
    await ingest.process_pending()


@client.event
async def on_ready():
    print("bot ready")
    guild = await client.fetch_guild(server)
    print(f"guild: {guild.name}")
    channels = await guild.fetch_channels()
    text_channels = [c for c in channels if isinstance(c, discord.TextChannel)]
    print(f"channels: {[c.name for c in text_channels]}")

    for channel in text_channels:
        if channel.name != 'remy-music':
            continue
        print(f"ingesting {channel.name}")
        await ingest.run_ingest(channel)

    tree.copy_global_to(guild=guild)
    synced = await tree.sync(guild=guild)
    print(f"synced {len(synced)} commands: {[c.name for c in synced]}")
    process_pending_loop.start()
    print("ready to answer queries")


@client.event
async def on_message(message: discord.Message):
    if message.guild is None or message.guild.id != server:
        return
    if message.author.bot or message.type == discord.MessageType.chat_input_command:
        return
    channel = message.channel
    if isinstance(channel, discord.Thread):
        parent_name = channel.parent.name if channel.parent else None
        if parent_name in IGNORE_CHANNELS:
            return
        buffer.store_message(message, thread_id=str(channel.id), thread_name=channel.name)
    else:
        if channel.name in IGNORE_CHANNELS:  # type: ignore
            return
        buffer.store_message(message)


@tree.command(name="ask", description="Ask a question about this server's message history")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    results = vector_search.vsearch(question)
    if not results:
        await interaction.followup.send("I couldn't find anything relevant.")
        return
    parts = []
    for chunk_text, message_ids in results:
        link = buffer.get_discord_link(message_ids[0]) if message_ids else None
        entry = chunk_text
        if link:
            entry += f"\n🔗 {link}"
        parts.append(entry)
    response = "\n\n".join(parts)
    await interaction.followup.send(response[:2000])


client.run(token)
