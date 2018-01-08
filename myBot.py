import discord
import asyncio
from discord.ext import commands
import random
import pprint
import time
import sqlite3
from bimbotconfig import *

import game
import betyourbimbo as bimbo

description = '''Welcome to the Bimbonator 3001x!  \nYou may use the following commands:'''

TEST = True

CMD_PREFIX = '!'

bot = commands.Bot(command_prefix=CMD_PREFIX, description=description)
bimbo = bimbo.BetYourBimbo(bot)

game = game.Game(bot)
idleSince = int(time.time())

def removeUserFormatting(userid):
	if userid[0:2] == "<@":
		userid = userid[2:]
	if userid[-1] == ">":
		userid = userid[:-1]
	return userid



def playerStatus(player):
	return "<@{}> is up...\nYour hand is {} for {}".format(player.name, player.getHand(), player.getBJCount())



def whosplaying(game):
	o = "__**The following users are set to play in the next game:**__"
	for player in game.players:
		o += "\n<@{}>".format(player.name)
	if len(game.players) == 0:
		o += "\nNobody!"
	return o
	

	
def parse_args(args, ctx):
	
	num = 1
	recipient = ctx.message.author.id
	# print ("parse: {}".format(args))
	
	
	for arg in args:
		#print(arg)
		if arg.isdigit():
			num = int(arg)
		elif isinstance(arg,str):
			if arg[:2] == "<@":
				#This is a user id!
				recipient = arg[2:-1]
	# print(" R: {}  N: {}".format(recipient, num))
	return {"recipient":recipient, "num":num}
	
	

@bot.event
async def on_ready():
	print('Logged in as')
	print("Bot Name: {}".format(bot.user.name))
	print("Bot ID:   {}".format(bot.user.id))
	print("Auth URL: {}".format(discord.utils.oauth_url(bot.user.id, permissions=None,)))
	print('------')
	bot.load_extension("betyourbimbo")



@bot.command()
async def startBJ(ctx):
	"""Start a game of blackjack (Note: will reset an ongoing game!)"""
	global game
	
	game.reset(2)
	await ctx.send("Starting Blackjack!  Who'd like to play?\nRespond with the __!playing__ command to join.\n__!out__ will get you out of the game.")
	
	
	
@bot.command()
async def stopBJ(ctx):
	"""Stop an active game of blackjack & reset everything."""
	global game
	
	game.reset()
	game.set_game_state("STOPPED")
	await ctx.send("Awwww....how sad.  If you'd like to start a game, use __!startBJ__")
	
	
	
@bot.command()
async def playing(ctx):
	"""Tell the Dealer that you're playing in the next game"""
	global game	
	m = game.addPlayer(ctx.message.author.id)
	await ctx.send(m)
	if bimbo.getUserGender(ctx.message.author.id) is None:
		await ctx.send("**Please set your gender!** You can do that by typing __!gender M__ or __!gender F__")
	await ctx.send(whosplaying(game))
	await ctx.send("If players are ready, you can start the game by typing __!dealBJ__")



@bot.command()
async def out(ctx):
	"""Tell the dealer that you're removing yourself from the next game"""
	m = game.delPlayer(ctx.message.author.id)
	await ctx.send(m)
	await ctx.send(whosplaying(game))
	
	

@bot.command()
async def dealBJ(ctx):
	"""Deal cards to all players & dealer. (Note: 1 player must be playing)"""
	global game

	o = game.startHand()
	await ctx.send(o)
	
	print("Game State -----> {}".format(game.state))
	if game.state == "PLAYING":
		o = game.playersTurn()
		for item in o:
			await ctx.send(item)
			await asyncio.sleep(1)



@bot.command()
async def split(ctx):
	global game
	await ctx.send(game.split())
	
		
	o = game.playersTurn()

	for item in o:
		await ctx.send(item)
		await asyncio.sleep(1)


		
@bot.command()
async def hit(ctx):
	"""Blackjack: Take an additional card into your hand."""
	global game
	
	o = game.hit(ctx)
	await ctx.send(o)
	
	o = game.playersTurn()

	for item in o:
		await ctx.send(item)
		await asyncio.sleep(1)
	
	

	
@bot.command()
async def stay(ctx, force="no"):
	"""Blackjack: End your turn without taking an additional card."""
	global game
	
	print(force)
	print(game.players[game.turn].name != ctx.message.author.id)
	print(force == "force")
	print(game.players[game.turn].name)
	print(ctx.message.author.id)
	print(bimbo.isOwlCoEmployee(ctx.message.author.id))
	
	if game.players[game.turn].name != ctx.message.author.id:
		print("Attempt to stay someone else's hand!")
		
		print (force == "force" or force == "FORCE") 
		print (bimbo.isOwlCoEmployee(ctx.message.author.id))
		print (force != "force" and force != "FORCE") 
		print (not bimbo.isOwlCoEmployee(ctx.message.author.id))
		
		if (force == "force" or force == "FORCE") and not bimbo.isOwlCoEmployee(ctx.message.author.id):
			print("FORCED attempt failed!")
			await ctx.send("**Silly bimbo!** Only OwlCo employees can force someone else's hand to continue")
			return
		
		if (force != "force" and force != "FORCE") or not bimbo.isOwlCoEmployee(ctx.message.author.id):
			print("FORCED attempt failed!")
			await ctx.send("Sorry, <@{}>! Please wait your turn!".format(ctx.message.author.id))
			return
			
		await ctx.send("Forcing idle player to stay...")
				
		o = game.playersTurn()
		for item in o:
			await ctx.send(item)
			await asyncio.sleep(1)
	
	o = game.stay(ctx, force)
	await ctx.send(o)
	
	o = game.playersTurn()
	for item in o:
		await ctx.send(item)
		await asyncio.sleep(1)


@bot.event
async def on_message(message):
	global CMD_PREFIX, idlesince

	accept_channels = ["bot_test", "betyourbimbo"]
	chn = str(message.channel)
	#srv = str(message.guild)
	if chn not in accept_channels and chn[0:14] != "Direct Message":
		#print("Ignoring from {}".format(message.channel))
		return
	
	if message.content[0] == CMD_PREFIX:
		bimbo.logCommand(message.author.id, message.content)
		
	if chn in accept_channels:
		idleSince = int(time.time())

	await bot.process_commands(message)


if TEST:
	bot.run(test_key)
else:
	bot.run(release_key)

