import random
import itertools

class Player:
	
	def reset(self):
		self.hands = [[]]
		self.handNumber = 0
		self.status = "OK"   #poss values; OK, BUST, BJ

	def __init__(self, name):
		self.name = name
		self.reset()

	def numHands(self):
		return len(self.hands)

	def addHand(self,newHand = []):
		self.hands.append(newHand)
		self.handNumber += 1
		return len(self.hands) - 1

	def addCard(self,card):
		self.hands[self.handNumber].append(card)
		return self.hands[self.handNumber]

	def getHand(self, handNumber=0):
		hand = self.hands[handNumber]
		o = ""
		for card in hand:
			o += "[{}]   ".format(card)
		return o
	
	def getCurrentHand(self):
		return self.getHand(self.handNumber)

	def getDealerHand(self):
		print (self.hands[0])
		return [self.hands[0][0], '??']

	def getBJCount(self, handNumber=0):
		count = 0
		numCards = 0
		numAces = 0
		for card in self.hands[handNumber]:
			numCards += 1
			if card[0] in "0123456789":
				count += int(card[0])
			elif card[0] == "A":
				numAces += 1
				count += 11
			else:
				count += 10
				
		#cycle through for aces:
		while numAces > 0 and count > 21:
			count -= 10
			numAces -= 1

		if numCards == 2 and count == 21:
			self.status = "BJ"
			return 21
		
		if count > 21:
			self.status="BUST"
		return count	
	
	def showPlayerHands(self):
		o = "<@{}> has: ".format(self.name)
		for hand in hands:
			if self.numHands > 1:
				o += "\n"
			o = "<@{}> has {} for {}".format(player.name, player.getHand(), player.getBJCount())
				

		
