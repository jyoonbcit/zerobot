"""
0x14d#7621's personal Discord bot.
"""

import discord
import os

intents = discord.Intents(members=True, messages=True, guilds=True)
client = discord.Client(intents=intents)
# Lets the bot listen for specific messages
intents.message_content = True
# intents.manage_messages = True
# intents.read_message_history = True

# Instantiate
# textChannel = discord.TextChannel(state = , guild = member.guild.name, data = )


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  await prune_messages(message)

  if message.author == client.user:
    return

  if message.content.startswith('$greetings'):
    await message.channel.send(f'Hello {message.author}')

  if "who asked" in message.content:
    discord.guild.kick(user=message.author, reason='I asked.')


async def prune_messages(message):
  print(message.content)
  if message.content.startswith('$prune') and len(
      message.content) > len('$prune '):
    to_delete = int(message.content[7:]) + 1
    msgs = []
    channel = message.channel
    async for msg in channel.history():
      msgs.append(msg)
    print(list(msg.content for msg in msgs))
    await discord.TextChannel.delete_messages(message.channel,
                                        messages=msgs[1:to_delete])
    await message.channel.send(f'Deleted {int(message.content[7:])} messages.')


client.run(os.getenv('TOKEN'))
