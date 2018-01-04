import player
import cards
import time
import betyourbimbo as bimbo

class Game:

	COOLDOWN_PERIOD = 90  #seconds

	def set_game_state(self, state):
		print("Changing game state to: {}".format(state))
		self.state = state



	def reset(self, numDecks=1):
		self.set_game_state("START")
		self.players = []
		self.turn = 0
		self.dealer = player.Player("Dealer")
		self.deck = cards.Cards(numDecks)
		self.set_game_state("WAITING_ON_PLAYERS")
		try:
			self.cooldownTime
		except AttributeError:
			self.cooldownTime = 0



	def __init__(self, bot, numDecks=1):
		self.bot = bot
		self.bimbo = bimbo.BetYourBimbo(bot)
		self.reset(numDecks)


	def getRemainingCooldown(self):
		return  (self.cooldownTime + self.COOLDOWN_PERIOD) - int(time.time())


	def checkCooldown(self):
		if self.getRemainingCooldown() < 0:
			return True
		else:
			return False
			
	
	def whosplaying(self):
		o = "__**The following users are set to play in the next game:**__"
		for player in self.players:
			o += "\n<@{}>".format(player.name)
		if len(self.players) == 0:
			o += "\nNobody!"
		return o


	
	def get_player_names(self):
		names = []
		for player in self.players:
			names.append(player.name)
		return names
		
		
		
	def getNumPlayers(self):
		return len(self.players)
		
		
		
	def showPlayersHands(self):
		o = "Here are the hands:"
		for player in self.players:
			o += "\n<@{}> has {} for {}".format(player.name, player.getHand() , player.getBJCount())
		return o
		
		
		
	def showDealerHand(self):
		return "[{}]  [??]".format(self.dealer.hands[0][0])


	def resolveGame(self):
		output = []
		o = ""
		#reveal dealer's card
		o += "Dealer's hand: {} for {}".format(self.dealer.getHand(), self.dealer.getBJCount())
		while (self.dealer.getBJCount() < 17 and self.dealer.status == "OK"):
			o += "\nDealer hits..."
			newCard = self.deck.deal()
			self.dealer.addCard(newCard)
			o += "\nDealer gets [{}] for {}".format(newCard, self.dealer.getBJCount())
			
		if self.dealer.status == "BUST":
			o += "\nDealer Busts!"
		else:
			o += "\nDealer stays with {}".format(self.dealer.getBJCount())
		
		output.append(o)
			
		#cycle through players
		o = "__**Let's see how this all plays out, shall we?**__"
		for player in self.players:
			if player.status == "BJ":
				o += "\n<@{}> has BLACKJACK and can wipe all effects (__!removeAll__) or roll (__!token 3__) for **3 tokens!!**".format(player.name)
				self.bimbo.tallyReward(player.name, 'BJ')
			elif player.status == "BUST":
				o += "\n<@{}> has busted. Roll the dice (__!effect__) for your penalty!".format(player.name)
				self.bimbo.tallyReward(player.name, 'L')
			else: #player.status == "OK" or player.status == "DBL":
				if self.dealer.status == "BUST":
					o+= "\nDealer busts, <@{}> did not, and WINS!.... Roll the dice (__!token__) for your token, or you may remove an effect (__!removeEffect id#__)!".format(player.name)
					self.bimbo.tallyReward(player.name, 'W')
				elif player.getBJCount() < self.dealer.getBJCount():
					o += "\n<@{}> has {} to the dealer's {}, and lost.... Roll the dice (__!effect__) for your penalty!".format(player.name, player.getBJCount(), self.dealer.getBJCount())
					self.bimbo.tallyReward(player.name, 'L')
				elif player.getBJCount() == self.dealer.getBJCount():
					o += "\n<@{}> has tied the dealer for a push. No harm, no foul!".format(player.name)
				else:
					o += "\n<@{}> has {} and wins! Roll the dice (__!token__) for your token, or you may remove an effect (__!removeEffect id#__)!".format(player.name, player.getBJCount())
					self.bimbo.tallyReward(player.name, 'W')
		
		output.append(o)

		self.cooldownTime = int(time.time())

		
		return output		
		
		
	def playersTurn(self):
		output = []
		print("-----> playersTurn <-----")
		if self.state == "PLAYING":
			o = ""
			
			while self.turn < self.getNumPlayers() and self.players[self.turn].status == "BJ":
				currPlayer = self.players[self.turn]
				output.append("<@{}> has BLACKJACK!  Congratulations!".format(currPlayer.name))
				self.turn += 1
				
			
			if not self.turn >= self.getNumPlayers():
				currPlayer = self.players[self.turn]
				o += "**<@{}>** is up... ".format(currPlayer.name)
				if currPlayer.numHands() == 1:
					o += "Your hand is {} for {} - **Dealer** has: {}".format(currPlayer.getCurrentHand(), currPlayer.getBJCount(), self.showDealerHand()) 
				else:
					o += "You have multiple hands:\n"
					h = 0
					for hand in currPlayer.hands:
						if currPlayer.handNumber == h:
							o += "\n PLAYING: "
						o += str(currPlayer.hands[h])
						h += 1
					o += "\n\nDealer has {}".format(self.showDealerHand())
				output.append(o)
				o = ""
					
			else:
				output.append("We've reached the end of the players' round. Let's see what the dealer has!\n\n")
				output.extend(self.resolveGame())
				self.set_game_state("WAITING_ON_PLAYERS")
				o = self.whosplaying()
				o += "\n\nYou can deal a new game with the same players by typing __!dealBJ__"
				o += "\nNew players may join by typing __!playing__"
				o += "\nPlayers may leave the game at this point by typing __!out__"
				o += "\n\nYou may start another game in {} seconds".format(self.COOLDOWN_PERIOD)
		else:
			o += "-"
			
		if o != "": 
			output.append(o)
		return output

		
	def dealBlackjack(self):
		
		if self.state == "READY":
			print("Dealing!")
			for x in range(2):
				for player in self.players:
					player.addCard(self.deck.deal())
					print(player.hands[player.handNumber])
				self.dealer.addCard(self.deck.deal())
				print(self.dealer.hands[0])
		else:
			print("Not READY")

	def split(self):
		o = "Sorry....Erynne is working on splits still!!"
		return o
		
		
		player = self.players[self.turn]
		#check to see if cards are same
		
		if player.numHands() > 1:
			return "Sorry, can only split once per game"
			
		hand = player.hands[0]
		print("Player's Hand: {}".format(hand))
		if hand[0][0] != hand[1][0]:
			return "Sorry, can only split when cards are the same"

		#create new hand
		newHandNumber = player.addHand()
		print("newHandNumber = {}".format(newHandNumber))
		print(self.players[self.turn].hands)
		#move card 1 from old hand to new hand
		cardToMove = player.hands[newHandNumber-1].pop()
		print(cardToMove)
		player.hands[newHandNumber].append(cardToMove)
		print("HANDS: {}".format(player.hands))
		
		#deal one card to each hand
		for hand in player.hands:
			newCard = self.deck.deal()
			print("Card = {}".format(newCard))
			hand.append(self.deck.deal())
		print (player.hands)
		
		return "Work in progress"
				
		

	def stay(self, ctx, force="no"):	
		o = ""
		if self.state == "PLAYING":
				
			if force == "force":
				o += "<@{}> has FORCED the current player to stay.\nPlease be careful when using this function!".format(ctx.message.author.id)
				
			player = self.players[self.turn]
			o += "<@{}> is staying with {}...".format(player.name, player.getBJCount())
			self.turn += 1
		else:
			o = "I can't do that yet..."
			 
		return o
	
	def hit(self, ctx):
		o = ""
		if self.state == "PLAYING":
			if self.players[self.turn].name == ctx.message.author.id:
				player = self.players[self.turn]
				card = self.deck.deal()
				player.addCard(card)
				o += "<@{}> hits and receives a {}.\nYour hand is now {} for {}".format(player.name, card,player.getHand(), player.getBJCount())
				if player.status == "BUST":
					o += " - Oh, no!  <@{}> has busted!".format(player.name)
				#else:
					#o += " - Dealer has {}".format(self.dealer.getDealerHand())
				if self.players[self.turn].status != "OK":
					self.turn +=  1
			else:
				o += "Not your turn yet..."
				o += "It's <@{}>'s turn...".format(player.name)
		else:
			o += "I can't do that yet..."
		
		return o
		
		
	def startHand(self):
		o = ""
		
		if not self.checkCooldown():
			o = "***ERROR:*** Can't start for {} seconds ({} sec cooldown between games)".format(self.getRemainingCooldown(), self.COOLDOWN_PERIOD)
			o += "\nNew players may join by typing __!playing__"
			o += "\nPlayers may leave the game at this point by typing __!out__"
			return o
		
		if self.state == "WAITING_ON_PLAYERS" and self.getNumPlayers() > 0:
			# Check to see if the deck needs to be shuffled
			if self.deck.needsShuffle == True:
				o += "\nThe marker was pulled during the last game. Shuffling now..."
				self.deck.resetDeck()	
			
			# now reset the game, dealer, and set the turn & state
			for player in self.players:
				player.reset()	
			self.dealer.reset()
			self.turn = 0
			self.set_game_state("READY")
			
			#Now we're ready to go
			o += "\nDealing two cards to each player & dealer...\n"
			self.dealBlackjack()
			
			#Display the players' hands
			
			o += "\n{}".format(self.showPlayersHands())
			
			o += "\nThe dealer has: {}".format(self.showDealerHand())
			self.set_game_state("PLAYING")
		else:
			if self.getNumPlayers() > 0:
				o += "Can't deal yet...(wrong game state)"
			else:
				o += "Can't deal yet...(no players)"
		
		
		return o


	
	def addPlayer(self, playerID):
		if self.state == "WAITING_ON_PLAYERS":
			if playerID in self.get_player_names():
				return "Player <@{}> already present".format(playerID)
			else:
				self.players.append(player.Player(playerID))
				print("Player <@{}> added".format(playerID))
				return "Player <@{}> added".format(playerID)
		else:
			return "Not accepting players..."


			
	def delPlayer(self, playerID):
		if self.state == "WAITING_ON_PLAYERS":
			if playerID not in self.get_player_names():
				return "Player <@{}> not playing!".format(playerID)
			else:
				idx = self.get_player_names().index(playerID)
				del self.players[idx]
				print("Player <@{}> removed".format(playerID))
				return "Player <@{}> removed".format(playerID)
		else:
			return "Can't do that yet..."
