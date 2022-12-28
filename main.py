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
  author = str(message.author)
  print(message.content)
  await prune_messages(message)

  if message.author == client.user:
    return None

  if message.content.startswith('$greetings'):
    await message.channel.send(f'Hello {message.author}')
    
  if message.content == '$daily':
    await points_daily(message)

  if message.content == '$balance' or message.content == '$bal':
    with open('users.json', 'r') as lb:
      data = json.load(lb)
    await message.channel.send(f'{author} has {data[author]["points"]} points.')

  if message.content == '$leaderboard' or message.content == '$lb':
    lb_str = ""
    with open('users.json', 'r') as lb:
      data = json.load(lb)
      lb.seek(0)
    # TODO: Make data displayed limited to 10; maybe add separate pages to display more
    for user in data:
      lb_str += "**"
      lb_str += user
      lb_str += "**\n"
      lb_str += str(data[user]['points'])
      lb_str += " points\n"
    await message.channel.send(lb_str)

  if message.content == '$help':
    help_str = ""
    with open('README.md', 'r') as helpfile:
      lines = helpfile.readlines()
      for line in lines:
        help_str += line

    await message.channel.send(help_str)

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
    if datetime.now() - datetime.strptime(data[author]['last_daily'], '%m/%d/%y %H:%M:%S') < timedelta(days = 1):
      # -8 hours to compensate for PST
      print(datetime.strptime(data[author]['last_daily'], '%m/%d/%y %H:%M:%S') - datetime.now())
      await message.channel.send(
        'Your daily bonus is not ready yet. Check back at '
        f'{datetime.strptime(data[author]["last_daily"], "%m/%d/%y %H:%M:%S") + timedelta(days = 1, hours = -8)}'
      )
      return None
    # If user exists, continue

  # Read current amount of points belonging to user, add 100
  current_points = data[author]['points']
  data[author]['points'] = 100 + current_points
  data[author]['last_daily'] = datetime.now().strftime('%m/%d/%y %H:%M:%S')
  
  with open('users.json', "w") as lb:
    json.dump(data, lb)

  await message.channel.send(f'Daily bonus claimed! User {message.author} has {data[author]["points"]} points.')


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
