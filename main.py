import discord
from discord.utils import get
import asyncio
import webserver
from webserver import keep_alive
from discord.ext import commands
from random import choice
import os
import datetime

BOT_PREFIX = ("$")  # All commands start with $ 


client = commands.Bot(command_prefix=BOT_PREFIX)
client.remove_command("help")  # To set on help command
message_channel = "BOTTOM_TEXT"


def GetDetails(votes_raw, voters_raw):  # Change so that it takes in votes and voters as the args.
  votes, voters = {}, {}
  votes_raw, voters_raw = votes_raw.content, voters_raw.content
  if votes == "*":
    votes = {}
  else:
    for line in votes.split("\n"):
      line = line.rstrip()
      voted, votees = line.split(": ")
      votees = votees.split(", ")
      votes[voted] = votees
  if voters == "*":
    voters = {}
  else:
    for line in voters.split("\n"):
        line = line.strip()
        voter, voted = line.split(": ")
        voters[voter] = voted
  return votes, voters


def UpdateVotes(votes):  # Combine with UpdateVoters
  if votes == {}:
    return "*"
  message = []
  for vote in votes:
    message.append(vote + ": " + ", ".join(votes[vote]))
  return "\n".join(message)

def UpdateVoters(voters):  # Combine with UpdateVotes
  if voters == {}:
    return "*"
  message = []
  for voter in voters:
    message.append(voter + ": " + voters[voter])
  return "\n".join(message)


# @client.command(pass_context=True)

async def help(context):  # Help message dm'd
  await context.message.delete()
  await context.message.author.send(help_message)

#@client.command(pass_context=True)

async def vote(context):
    async for msg in client.get_channel(603466270746214421).history(limit=1):  # check if it's day or night (yes means it is night)
      if msg.content == "Yes":
        return
    allowed = False
    for role in context.message.author.roles:  # Check if they are alive
      if role.name == "Alive":
        allowed = True
        break
    if not allowed:
      await context.message.delete()
      return
    output = "Error occured when processing request"  # In case the message passes all error handlers
    message = context.message.content
    if message.lower() == "$vote boat":  # Funny stuff
      output = "Boat"
    else:
      if len(message) > len("$vote "):  # correctly formatted with space
          chann = client.get_channel(601943715912744964)  # the "database" *wink* *wink*
          votes, voters = await chann.history(limit=2).flatten()  # Fix so that it only reads one message
          votes, voters = GetDetails(votes, voters)  # Gets votes and voters after passing raw data in
          person = message[6:]
          author = context.message.author.nick
              
          
          if person.lower() == "no-lynch":
              person_exists = True
              person = "No-Lynch"
          else:
              person_exists = False
              for p in context.message.guild.members:
                  if p.nick == person:
                      person_exists = True
                      break
          if person_exists:
              output = "The action has been completed!"
              if author in voters:
                votes[voters[author]].remove(author)
                if votes[voters[author]] == []:
                  del votes[voters[author]]
                del voters[author]
              if person in votes:
                votes[person].append(author)
              else:
                votes[person] = [author]
              voters[author] = person
          else:
              output = "The person you have requested to vote for is not on the server"
          await chann.send(UpdateVotes(votes))
          await chann.send(UpdateVoters(voters))  # Send as UpdateDetails(votes, voters) once fixed
    await context.channel.send(output)

#@client.command(pass_context=True)

async def unvote(context):
    async for msg in client.get_channel(603466270746214421).history(limit=1):
      if msg.content == "Yes":
        return
    allowed = False
    for role in context.message.author.roles:
      if role.name == "Alive":
        allowed = True
    if not allowed:
      await context.message.delete()
      return
    chann = client.get_channel(601943715912744964)
    votes, voters = await chann.history(limit=2).flatten()  # Again, limit should be 1
    votes, voters = GetDetails(votes, voters)  # Gets votes and voters after passing raw data in
    
    if context.message.author.nick not in voters:
        output = "You have not voted. This command is only useable if you have voted"
    else:
        if context.message.author.nick == "Max P":
          output = "I did it s-senpai"
        else:
          output = "All good :ok_hand:"
        person = voters[context.message.author.nick]
        votes[person].remove(context.message.author.nick)
        if votes[person] == []:
          del votes[person]
        del voters[context.message.author.nick]
    await chann.send(UpdateVotes(votes))
    await chann.send(UpdateVoters(voters))  # Merge commands to UpdateDetails(votes, voters)
    await context.channel.send(output)

#@client.command(pass_context=True)

async def reset(context):
    permissible = False
    for role in context.message.author.roles:
      if role.name == 'Game Host' or role.name == "Host":
        permissible = True
        break
    if permissible:
      chann = client.get_channel(601943715912744964)
      await chann.send("*")
      await chann.send("*")  # Message as one thing
      output = "It has been done"
    else:
      await context.message.delete()
      return
    await context.channel.send(output)

#@client.command(pass_context=True)

async def results(context):
  async for msg in client.get_channel(603466270746214421).history(limit=1):
      if msg.content == "Yes":  # Check if it's night or day, "Yes" means it's night
        return
  await context.message.delete()  # Delete message to reduce spam
  channel = client.get_channel(601943715912744964)  # The "database" channel
  v = False
  output = []
  async for foo in channel.history(limit=2):  # Ughhh heck, wonder if we can use the GetVotes command...?
    if v == False:
      v = True
      continue
    if foo.content == "*":
      await context.message.author.send("No votes yet!")
      return
    for line in foo.content.split("\n"):
      line = line.strip()
      voted, votees = line.split(": ")
      votees = votees.split(", ")
      line = voted + ": " + str(len(votees)) + "     (" + ", ".join(votees) + ")"
      output.append(line)
  await context.message.author.send("\n".join(output))


#@client.command(pass_context=True)

async def end_day(context):
  await context.message.delete()
  permissible = False
  for role in context.message.author.roles:
    if role.name == 'Game Host' or role.name == "Host":
      permissible = True
      break

  if not permissible:
    return

  message_channel = client.get_channel(601943715912744964)
  v = False
  message = []
  async for line in message_channel.history(limit=2):  # Oh god oh fuck
    if not v:
      v = True
      continue
    line = line.content.strip()
    lynched, lynchCount = ["No-Lynch"], 0
    if line == "*":
      continue
    for foo in line.split("\n"):
      voted, votees = foo.split(": ")
      votees = votees.split(", ")
      message.append(voted + ": " + str(len(votees)) + "     (" + ", ".join(votees) + ")")
      if len(votees) == lynchCount:
        lynched.append(voted)
      elif len(votees) > lynchCount:
        lynched, lynchCount = [voted], len(votees)
  print(lynched)
  e = False
  if len(lynched) == 1:
    lynched = lynched[0]
    e = True
  else:
    for dead in lynched:
      print(dead)
      print(dead == "No-Lynch")
      if dead == "No-Lynch":
        print('here')
        continue
      for member in context.channel.members:
        if member.nick == dead:
          p = member
          break
      for role in p.roles:
        if (role.name == "Game Host" or role.name == "Host") and dead in lynched:
          lynched[lynched.index(dead)] = "No-Lynch"
        if role.name == "Dead" and dead in lynched:
          lynched[lynched.index(dead)] = "No-Lynch"
        if role.name == "Spectator" and dead in lynched:
          lynched[lynched.index(dead)] = "No-Lynch"
        if role.name == "Alive" and dead in lynched:
          person = dead
  
  if e:
    pass
  elif lynched.count("No-Lynch") == len(lynched) - 1:
    lynched = person
  else:
    lynched = "No-Lynch"
  for member in context.channel.members:
      if member.nick == lynched:
        dead = member
        break
  if message == []:
    await context.channel.send("No one has voted, which means...")
  else:
    await context.channel.send("\n".join(message))
  if lynched == "No-Lynch":
    await context.channel.send("No one was lynched.")
  else:
    await context.channel.send(lynched + " was lynched.")
    await dead.remove_roles(get(context.guild.roles,id=570830233079513088))
    #real_alive = 570830233079513088
    #fake_alive = 603472901970329620
    await dead.add_roles(get(context.guild.roles, id=574533043084066816))
    #real_dead = 574533043084066816
    #fake_dead = 603472880004759568
    await dead.send("You have been lynched in the day. soz bud.")
  await client.get_channel(603466270746214421).send("Yes")
  await context.channel.send("The day has been deactivated. Votes will no longer be counted.")
  await message_channel.send("*")
  await message_channel.send("*")

#@client.command(pass_context=True)
async def end_night(context):
  await context.message.delete()
  permissible = False
  for role in context.message.author.roles:
    if role.name == 'Game Host' or role.name == "Host":
      permissible = True
      break

  if not permissible:
    return
  await client.get_channel(603466270746214421).send("No")
  await context.channel.send("The day has been activated. You may now send your votes.")

#@client.event
async def on_message(message):
  gid = message.guild.id
  if gid == 625933318072041472:
    m = message.content.lower()
    if "y" in m:
      if "e" in m[m.index("y"):]:
        if "s" in m[m.index("e"):]:
          await message.delete()

@client.command(pass_context=True)
async def beach(ctx):
  if ctx.message.content[6:] == " yes":
    pass
  elif ctx.message.content[6:] == " no":
    pass
  else:
    await ctx.channel.send("Please give a valid response")

keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)
