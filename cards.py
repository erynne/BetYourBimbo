import random
import itertools

class Cards:
	
	SUITS = [':clubs:', ':diamonds:', ':heart:', ':spades:']
	RANKS = 'A23456789TJQK'
	
	def shuffle(self):
		random.shuffle(self.deck)
		#TEST self.deck = ['8:clubs:', 'Q:heart:', '8:spades:', '2:heart:', 'Q:clubs:', '6:heart:', 'A:clubs:', '4:clubs:', 'A:diamonds:', 'T:clubs:', '8:diamonds:', 'Q:heart:', '3:clubs:', '5:diamonds:', 'T:spades:', '6:spades:', '7:spades:', '9:heart:', 'Q:spades:', 'Q:diamonds:', '3:diamonds:', '4:clubs:', '2:diamonds:', '8:diamonds:', '3:spades:', '6:diamonds:', 'A:spades:', '2:clubs:', 'K:heart:', '5:spades:', '6:heart:', 'T:heart:', '2:heart:', 'J:heart:', '6:diamonds:', '4:spades:', '6:spades:', 'J:clubs:', '8:spades:', 'Q:spades:', 'J:diamonds:', 'Q:diamonds:', '3:clubs:', 'A:spades:', 'T:spades:', 'A:heart:', '3:spades:', '4:heart:', 'K:diamonds:', '5:clubs:', '2:diamonds:', 'J:spades:', 'K:heart:', 'J:diamonds:', '9:spades:', '9:clubs:', '3:heart:', 'K:spades:', '8:heart:', 'J:spades:', '9:clubs:', '7:heart:', '5:heart:', 'T:diamonds:', '4:diamonds:', '8:clubs:', 'Q:clubs:', 'T:diamonds:', '7:diamonds:', '9:diamonds:', '3:diamonds:', 'K:clubs:', '9:diamonds:', '6:clubs:', 'J:clubs:', '4:diamonds:', '5:clubs:', 'A:heart:', '3:heart:', 'A:diamonds:', '4:heart:', '7:clubs:', '7:heart:', '4:spades:', '5:spades:', '7:clubs:', 'J:heart:', '8:heart:', '8:spades:', 'T:heart:', 'T:clubs:', '6:clubs:', 'K:spades:', '9:spades:', 'A:clubs:', '2:spades:', '8:clubs:', 'K:clubs:', '7:diamonds:', 'K:diamonds:', '2:spades:', '5:heart:', '9:heart:', '5:diamonds:']

		print(self.deck)
	
	def resetDeck(self):
		self.deck = list(tuple(''.join(card) for card in itertools.product(self.RANKS,self.SUITS)) * self.numDecks)
		self.shuffle()
		self.insertMarker()
		self.needsShuffle = False
	
	def __init__(self, numDecks):
		self.numDecks = numDecks
		self.resetDeck()
	
	def insertMarker(self):
		pos = (10+random.randint(0,len(self.deck) * 0.25)) * -1
		self.deck.insert(pos, "XX")
		
	def deal(self):
		dealt = self.deck.pop(0)
		print("Dealt {}".format(dealt))
		if dealt != "XX":
			return dealt
		else:
			self.needsShuffle = True
			print ("Pulled the marker - Deck should shuffle before next deal!")
			dealt = self.deck.pop(0)
			return dealt
		
	def setState(self, newStatus):
		self.status = newStatus
		print("Status: {}".format(self.status))


