import discord
from discord.ext import commands
import asyncio
import json
import requests
import urllib.parse
import random



class Drinks():
	
	adverbs = ["happily","gladly","sadly","happily","thankfully","perfectly","highly","lowly","quickly","slowly","suddenly","promptly","angrily","quietly","loudly","softly","beautifully","motionlessly","gracefully","generously","generally","adamantly","certainly","hungrily","massively","necessarily","lovely","sharply","accusingly","heartily","roughly","smoothly","separately","badly","dangerously","mournfully","spitefully","boldly","suddenly","automatically","normally","pragmatically","argumentatively","shortly","wrongly","effortlessly","painstakingly","breathlessly","proudly","greatly","horrifyingly","correctly","carefully","ironically","practically","partially"]
	
	def format_drink(self, ctx, drink):
		o = ""
		print(drink)
		print(drink['strDrink'])
		print(drink['strDrinkThumb'])
		o += "**The drink bot {} mixes a {} for <@{}>**".format(random.choice(self.adverbs), drink['strDrink'], ctx.message.author.id)
		o += "\n\n{}".format(drink['strDrinkThumb'])
		o += "\nWant to know how to make this?  Go to: https://thecocktaildb.com/drink.php?c={}".format(drink['idDrink'])
		return o
	
	def search_for_drink(self, ctx, search_string):
		o = ""
		raw = " ".join(search_string)
		url_safe = urllib.parse.quote_plus(raw)
		response = requests.get("http://www.thecocktaildb.com/api/json/v1/1/search.php?s=" + url_safe)
		if response.headers['Content-Type'] == 'application/json':
			drinks = response.json()
			if drinks['drinks'] == None:
				o += "Nothing found for {}.".format(raw)
				o += "If your favorite drink isn't found here, head over to http://thecocktaildb.com"
				o += "and please don't blame Erynne! :stuck_out_tongue_winking_eye:" 
			else:
				print(drinks)
				num_drinks = len(drinks['drinks'])
				if num_drinks > 1:
					found_flag = False
					found_drink = []
					for drink in drinks['drinks']:
						d1 = raw.lower()
						d2 = drink['strDrink'].lower()
						
						if d1 == d2: 
							print(raw.lower())
							print(drink['strDrink'].lower())
							found_flag = True
							found_drink = drink
					if found_flag:
						o += self.format_drink(ctx, found_drink)
					else:
						o += "**Found {} drink(s) for the search string {}:**".format(num_drinks, raw)
						for drink in drinks['drinks']:
							o += "\n-->{}".format(drink['strDrink'])
						o += "\n\n**Which one did you mean?**"
				else:
					drink = drinks['drinks'][0]
					o += self.format_drink(ctx, drink)
					
		return o
	
	@commands.command()
	async def drink(self, ctx, *args):
		"""Get the user a cocktail. Sorry, straight drinks/shots probably won't work. 
		   The drink database is located at http://thecocktaildb.com
		   If your favorite drink isn't in there, please don't blame Erynne!"""
		await ctx.send(self.search_for_drink(ctx, args))
	
	
	def __init__(self, bot):
		self.bot = bot




def setup(bot):
	bot.add_cog(Drinks(bot))
