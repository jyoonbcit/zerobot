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
  await prune_messages(message)

  if message.author == client.user:
    return

  if message.content.startswith('$greetings'):
    await message.channel.send(f'Hello {message.author}')

  if "who asked" in message.content:
    await message.guild.kick(user = message.author, reason = 'I asked. :society:')
    await message.message.author.send('Say something if this message is sent.')


async def prune_messages(message):
  if message.content.startswith('$prune') and len(
      message.content) > len('$prune ') and await admin_role_check(message.author, message):
    to_delete = int(message.content[7:]) + 1
    msgs = []
    channel = message.channel
    async for msg in channel.history():
      msgs.append(msg)
    await discord.TextChannel.delete_messages(message.channel,
                                        messages=msgs[1:to_delete])
    await message.channel.send(f'Deleted {int(message.content[7:])} messages.')


async def admin_role_check(member, message):
  if 1044772565740179456 not in list(role.id for role in member.roles):
    await message.channel.send('Not enough permissions bozo...')
    return False
  return True


client.run(os.getenv('TOKEN'))
