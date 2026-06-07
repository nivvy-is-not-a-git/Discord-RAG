import asyncio
import buffer, chunker
import discord
from typing import Any


async def scrape_history(channel:discord.TextChannel, after:discord.Object | None =None) -> None:
    async for thread in channel.archived_threads(limit=None): #threaded messages do not appear in channel history and must be iterated independently.
        async for message in thread.history(limit=None, oldest_first=True, after=after):
            if message.author.bot:
                continue
            buffer.store_message(message, thread_id=str(thread.id), thread_name=thread.name)
    #async for archived_threads since results are paginated (async generator) while await for channel.threads() since it fetches list all at once
    for thread in await channel.threads():
        async for message in thread.history(limit=None, oldest_first=True, after=after):
            if message.author.bot:
                continue
            buffer.store_message(message, thread_id=str(thread.id), thread_name=thread.name)

    async for message in channel.history(limit=None, oldest_first=True, after=after):
        if message.author.bot:
            continue
        buffer.store_message(message)
    await asyncio.sleep(1)


async def run_ingest(channel:discord.TextChannel) -> None:
    last_id = buffer.get_last_message_id(channel.name)
    after = discord.Object(id=last_id) if last_id else None

    await scrape_history(channel, after=after)

    message_ids = chunker.semantic_chunk()
    buffer.mark_processed(message_ids)
    



