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

thanos_quotes = ["But he is inevitable.", "But reality can be whatever he wants.", "But they should've gone for the head."]

help_message = """
```
Normal commands:
$vote - Takes in one argument. Vote for person on the server in the format '$vote [name of person]' (e.g. $vote John S), or 'no-lynch', as '$vote no-lynch' (not case sensitive, but include the hyphen). If you have already voted for someone, it will automatically change your vote.
$unvote - Takes in no arguments. This allows you to vote for no one. You do not have to use it to retract your vote and vote for someone else, as the vote command automatically does that for you.
$help - Takes in no arguments. iT'S sO MetA BrO. Dm's all commands to you, so no clogging the server
$results - Takes in no arguments. Shows all the votes so far through dms, again, for the purpose of not clogging the server.
$joke - Takes in no argments. Recites a comedic phrase that has been told by someone at some point in time.
Admin commands:
$reset - Takes in no arguments. Game Host ONLY. Resets all the votes, pretty simple. Emergency reset system, since ending the day simply doesthat
$end_day - Takes in no arguments. Game Host ONLY. Give the command in #story. Deletes the message, counts up the votes, displays the votes, finds the person with the most votes, informs that they were lynched, and then it "kills" them. Then, the day ends, and no more votes can be sent. The votes are then reset.
$end_night - Takes in no arguments. Game Host ONLY. Give the command in #story. Ends the night (for the voting bot), so that votes can be taken in once again.
```
"""

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
    async for msg in client.get_channel(NIGHT_CHANNEL).history(limit=1):  # check if it's day or night (yes means it is night)
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
          chann = client.get_channel(DATABASE_CHANNEL)  # the "database" *wink* *wink*
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
    async for msg in client.get_channel(NIGHT_CHANNGEL).history(limit=1):
      if msg.content == "Yes":
        return
    allowed = False
    for role in context.message.author.roles:
      if role.name == "Alive":
        allowed = True
    if not allowed:
      await context.message.delete()
      return
    chann = client.get_channel(DATABASE_CHANNEL)
    votes, voters = await chann.history(limit=2).flatten()  # Again, limit should be 1
    votes, voters = GetDetails(votes, voters)  # Gets votes and voters after passing raw data in
    
    if context.message.author.nick not in voters:
        output = "You have not voted. This command is only useable if you have voted"
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
      chann = client.get_channel(DATABASE_CHANNEL)
      await chann.send("*")
      await chann.send("*")  # Message as one thing
      output = "It has been done"
    else:
      await context.message.delete()
      return
    await context.channel.send(output)

#@client.command(pass_context=True)

async def results(context):
  async for msg in client.get_channel(NIGHT_CHANNEL).history(limit=1):
      if msg.content == "Yes":  # Check if it's night or day, "Yes" means it's night
        return
  await context.message.delete()  # Delete message to reduce spam
  channel = client.get_channel(DATABASE_CHANNEL)  # The "database" channel
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

  message_channel = client.get_channel(DATABASE_CHANNEL)
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
    await dead.remove_roles(get(context.guild.roles,id=MAFIA_SERVER))
    #real_alive = 570830233079513088
    #fake_alive = 603472901970329620
    await dead.add_roles(get(context.guild.roles, id=MAFIA_SERVER))
    #real_dead = 574533043084066816
    #fake_dead = 603472880004759568
    await dead.send("You have been lynched in the day. soz bud.")
  await client.get_channel(NIGHT_CHANNEL).send("Yes")
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
  await client.get_channel(NIGHT_CHANNEL).send("No")
  await context.channel.send("The day has been activated. You may now send your votes.")

keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)
