

@bot.command(pass_context=True)
async def stay(ctx, force="no"):
	"""Blackjack: End your turn without taking an additional card."""
	global game
	if game.state == "PLAYING":
		#print("{} <--> {}".format(game.players[game.turn].name, ctx.message.author.id))
		if (force == "force" and bimbo.isOwlCoEmployee(ctx.message.author.id)) or game.players[game.turn].name == ctx.message.author.id:
			if force == "force" and bimbo.isOwlCoEmployee(ctx.message.author.id):
				await bot.say("<@{}> has FORCED the current player to stay.\nPlease be careful when using this function!".format(ctx.message.author.id))
			
			player = game.players[game.turn]
			await bot.say("<@{}> is staying with {}...".format(player.name, player.getBJCount()))
			game.turn += 1
			if game.turn < len(game.players):
				await bot.say(playerStatus(game.players[game.turn]) + " - Dealer has {}".format(game.dealer.getDealerHand()))
			else:
				await bot.say("We've reached the end of the player round...now for the dealer!")
				o=game.resolveGame()
				await bot.say(o)
				game.set_game_state("WAITING_ON_PLAYERS")
				o = "\n" + whosplaying(game)
				o += "\n\nYou can deal a new game with the same players by typing __!dealBJ__"
				o += "\nNew players may join by typing __!playing__"
				o += "\nPlayers may leave the game at this point by typing __!out__"
				await bot.say(o)
		else:
			await bot.say("Not your turn yet...")
	else:
		await bot.say("I can't do that yet...")
		
		
		
@bot.command(pass_context=True)
async def hit(ctx):
	"""Blackjack: Take an additional card into your hand."""
	global game
	if game.state == "PLAYING":
		#print("{} <--> {}".format(game.players[game.turn].name, ctx.message.author.id))
		if game.players[game.turn].name == ctx.message.author.id:
			player = game.players[game.turn]
			card = game.deck.deal()
			player.addCard(card)
			await bot.say("<@{}> hits and receives a {}.\nYour hand is now {} for {}".format(player.name, card,player.getHand(), player.getBJCount()))	
			if player.status == "BUST":
				await bot.say("Oh, no!  <@{}> has busted!".format(player.name))
			else:
				await bot.say("Dealer has {}".format(game.dealer.getDealerHand()))
			if game.players[game.turn].status != "OK":
				game.turn +=  1
				if game.turn < len(game.players):
					await bot.say(playerStatus(game.players[game.turn]) + " - Dealer has {}".format(game.dealer.getDealerHand()))
					
				else:
					await bot.say("We've reached the end of the player round...now for the dealer!\n\n\n")
					o=game.resolveGame()
					await bot.say(o)
					game.set_game_state("WAITING_ON_PLAYERS")
					o = "\n" + whosplaying(game)
					o += "\n\nYou can deal a new game with the same players by typing __!dealBJ__"
					o += "\nNew players may join by typing __!playing__"
					o += "\nPlayers may leave the game at this point by typing __!out__"
					await bot.say(o)
		else:
			await bot.say("Not your turn yet...")
			await bot.say("It's <@{}>'s turn...".format(player.name))
	else:
		await bot.say("I can't do that yet...")
