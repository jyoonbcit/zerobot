"""
0x14d#7621's personal Discord bot.
"""

import discord
import os

intents = discord.Intents(members=True, messages=True, guilds=True)
client = discord.Client(intents=intents)
# Lets the bot listen for specific messages
intents.message_content = True


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('$greetings'):
    await message.channel.send(f'Hello {message.author}')


client.run(os.getenv('TOKEN'))
