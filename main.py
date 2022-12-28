"""
0x14d#7621's personal Discord bot.
"""

import discord
import os
import json
from datetime import datetime, timedelta


intents = discord.Intents(members=True, messages=True, guilds=True)
client = discord.Client(intents=intents)
# Lets the bot listen for specific messages
intents.message_content = True


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  print(message.content)
  await prune_messages(message)

  if message.author == client.user:
    return

  if message.content.startswith('$greetings'):
    await message.channel.send(f'Hello {message.author}')
    
  if message.content == '$daily':
    await points_daily(message)


@client.event
async def points_new_user(message):
  author = str(message.author)
  with open('users.json', 'r') as lb:
    data = json.load(lb)

  data[author] = dict()
  data[author]['points'] = 100
  data[author]['last_daily'] = datetime.now().strftime('%m/%d/%y %H:%M:%S')

  with open('users.json', 'w') as lb:
    json.dump(data, lb)

  await message.channel.send('New user created with 100 points.')


@client.event
async def points_daily(message):
  author = str(message.author)
  with open('users.json', 'r') as lb:
    data = json.load(lb)
    # Return to first line, prevents JSONDecodeError
    lb.seek(0)
    # Check if user exists in save file
    if author not in lb.read():
      await points_new_user(message)
      return None
    if datetime.strptime(data[author]['last_daily'], '%m/%d/%y %H:%M:%S') - datetime.now() < timedelta(days = 1):
      await message.channel.send(
        'Your daily bonus is not ready yet. Check back at '
        f'{datetime.strptime(data[author]["last_daily"], "%m/%d/%y %H:%M:%S") + timedelta(days = 1, hours = -8)}'
      )
      return None
    # If user exists, continue

  # Read current amount of points belonging to user, add 100
  current_points = data[author]['points']
  data[author]['points'] = 100 + current_points
  
  with open('users.json', "w") as lb:
    json.dump(data, lb)

  await message.channel.send(f'User {message.author} has {data[author]["points"]} points.')


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
