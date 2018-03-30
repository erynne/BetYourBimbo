import sqlite3
import random
import time
import discord
from discord.ext import commands
import asyncio

class BetYourBimbo():
	
	#TEST_TOKEN_LIMIT = 20
	#PROD_TOKEN_LIMIT = 13
	TOKEN_LIMIT = 20

	def parse_args(self, args, ctx):
		
		num = 1
		recipient = ctx.message.author.id
		gender = "B"
		print ("{} --> parse: {}".format(time.strftime("%m/%d/%y %H:%M %Z"), args))
		
		
		for arg in args:
			if arg.isdigit():
				num = int(arg)
			elif isinstance(arg,str):
				if arg[:2] == "<@":
					#This is a user id!
					arg = arg[2:-1]
					if arg[0] == "!":
						arg = arg[1:]
					recipient = int(arg)
				elif arg in "MFBmfb":
					#this is a gender!
					gender = arg
		return {"recipient":recipient, "num":num, "gender": gender}
	

	def tallyReward(self, userid, rewardType = 'W'):
		colNames = {'W': 'wins', 'L': 'losses', 'P': 'pushes', 'BJ': 'bjs'}
		now_time = int(time.time())
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		
		if rewardType in ['W', 'L', 'BJ']:
			cursor.execute("INSERT into rewards (UserID, Type, DateTime) values (?, ?, ?)",(userid, rewardType, now_time) )	
			db.commit()
			print("{} --> Added tally for {}'s {}".format(time.strftime("%m/%d/%y %H:%M %Z"), userid, rewardType))
		
		adduserstatsSQL = "UPDATE userinfo set {0} = {0} + 1 where userid = {1};".format(colNames[rewardType],userid)
		print("adduserstatsSQL = {}".format(adduserstatsSQL))
		cursor.execute(adduserstatsSQL);
		db.commit()

	
	def removeUserFormatting(self, userid):
		if not isinstance(userid, int):
			if userid[0:2] == "<@":
				userid = userid[2:]
			if userid[-1] == ">":
				userid = userid[:-1]
			if userid[0] == "!":
				userid = userid[1:]

		return userid
	
	def removeReward(self, userid, rewardType):
		now_time = int(time.time())
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		
		cursor.execute("select * from rewards where UserID = ? and Type = ? ORDER BY DateTime ASC LIMIT 1", (userid, rewardType))
		reward = cursor.fetchone()
		
		if reward == None:
			return False
		else:
			cursor.execute("delete from rewards where UserID = ? and Type = ? and DateTime = ?", (userid, rewardType, reward[2]))
			db.commit()
			return True
			
	
	def getUserRewards(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("select userid, type, count(*) from rewards where userID = ? group by Type order by Type DESC;",(userid,))
		rval = cursor.fetchall()
		return rval
	
	def processTimeouts(self):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		effectExpireTime = int(time.time()) - 86400
		rewardExpireTime = int(time.time()) - 3600

		sql = "UPDATE current set RemovedFlag = 'T' where Timestamp < '{}'".format(effectExpireTime)
		cursor.execute("UPDATE current set RemovedFlag = 'T' where Timestamp < ?", (effectExpireTime,))
		db.commit()
		
		cursor.execute("DELETE from rewards where DateTime < ?", (rewardExpireTime,))
		db.commit()
		db.close()
	
	
	def logCommand(self, user, command):
		db = sqlite3.connect('Bimbot.sqlite')
		now_time = int(time.time())
		cursor = db.cursor()
		cursor.execute("INSERT into commands (datetime, userid, command) values (?, ?, ?)",(now_time, user, command) )
		db.commit()
	
	
	
	def getOwlcoEmployees(self):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("select userid from owlco_employees")
		o = []
		r = cursor.fetchall()
		for e in r:
			o += e
		return  o


	def getUserGender(self, userid):
		userid = self.removeUserFormatting(userid)
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("select gender from userinfo where userid = ?",(userid, ) )
		val = cursor.fetchone()
		if val != None:
			val = val[0]
		return val

	def setUserGender(self, userid, gender):
		userid = self.removeUserFormatting(userid)
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("INSERT OR REPLACE into userinfo (userid, gender, lastSeen) values (?, ?, ?) ",(userid, gender.upper(), int(time.time())) )
		db.commit()
		return gender

	def addOwlCoEmployee(self, userid):
		userid = self.removeUserFormatting(userid)
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("INSERT into owlco_employees (userid, can_delete) select ?, 'Y' where not exists (select 1 from owlco_employees where userid = ?)",(userid, userid) )
		db.commit()
		return cursor.lastrowid



	def can_remove_employee(self, userid):
		userid = self.removeUserFormatting(userid)
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("select * from owlco_employees where userid = ? and can_delete = 'Y'",(userid, ) )
		val = cursor.fetchone()
		if val is None:
			return False
		else:
			return True



	def removeOwlCoEmployee(self, userid):
		userid = self.removeUserFormatting(userid)
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("DELETE FROM owlco_employees where userid = ?",(userid, ) )
		db.commit()
		return cursor.lastrowid



	def isOwlCoEmployee(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("SELECT * from owlco_employees where userid = ? ", (userid,))
		val = cursor.fetchall()
		if len(val) > 0:
			return True
		else:
			return False


	def choose_random_effect(self, gender="B"):
		print("{} --> Choosing effect: gender is {}".format(time.strftime("%m/%d/%y %H:%M %Z"), gender))
		db = sqlite3.connect('Bimbot.sqlite')
		query = "SELECT * FROM neweffects "

		if not gender in "Bb":
			query += "WHERE gender = '{}' ".format(gender)
			
		query += "ORDER BY RANDOM() LIMIT 1;"
		cursor = db.cursor()
		cursor.execute(query)
		rval = cursor.fetchone()
		db.close()
		return rval




	def user_has_effect(self,userID, tokenID, effectType):
		self.processTimeouts()
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("SELECT * FROM current where userid = ? and id = ? and type = ?;", (userID, tokenID, effectType))
		val = cursor.fetchall()
		if len(val) > 0:
			return True
		else:
			return False


			
	def has_token(self, userID, tokenID):
		return self.user_has_effect(userID, tokenID, 'T')
		
		
		
	def has_effect(self, userID, effectID):
		return self.user_has_effect(userID, effectID, 'E')


	def remove_category_effects(self, userid, category):
		print("Removing {} effects for <@{}>".format(category, userid))
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET RemovedFlag = 'C', RemovedTimeStamp = ? WHERE Type = 'E' AND UserID = ? AND category = ?", (nowtime, userid, category))
		db.commit()
		db.close()		

	def store_effect(self, etype, userid, effect, category="None", removeCategory="N"):
		self.processTimeouts()
		if removeCategory == "Y" and (etype == 'E' or etype == 'P'):
			self.remove_category_effects(userid, category)
		
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		now_time = int(time.time())
		cursor.execute("INSERT INTO current(Type, UserID, Effect, Timestamp, Category, RemovesCategory) VALUES(?, ?, ?, ?, ?, ?)", (etype, userid, effect, now_time, category, removeCategory))
		db.commit()
		db.close()

		return cursor.lastrowid
		
	def get_user_effects(self, userid):
		self.processTimeouts()
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("SELECT * FROM current WHERE (Type = 'E' OR Type = 'P') AND RemovedFlag is null AND UserID = ? AND Timestamp > ? ORDER BY Type ASC, Timestamp ASC", (userid, nowtime-86400))
		effects = cursor.fetchall()
		db.close()
		
		return effects


	def get_last_seen(self, timeInSecs):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("SELECT userid FROM userinfo WHERE lastseen > ?", (nowtime - timeInSecs, ))
		retVal = cursor.fetchall()
		retVal = [int(i[0]) for i in retVal] # remove the tuples from the list
		print("{} --> Eligible: {}".format(time.strftime("%m/%d/%y %H:%M %Z"), retVal)) 
		db.close()
		return retVal


	def give_token(self, fromuserid, tokenid, touserid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("SELECT * from current where Type = 'T' and ID = ? and userid = ?", (tokenid, fromuserid))
		dbEffect = cursor.fetchall()
		if len(dbEffect) == 0:
			return "**Sorry! -** <@{}> doesn't have any such token!".format(fromuserid)
		dbEffect = dbEffect[0]
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET UserID = ? WHERE (Type = 'T' AND UserID = ? AND ID = ?)" , (touserid, fromuserid, tokenid))
		db.commit()
		print( "{} --> <@{}> gave the __**{}**__ token to <@{}>".format(time.strftime("%m/%d/%y %H:%M %Z"), fromuserid, dbEffect[3], touserid))
		return "<@{}> gave the __**{}**__ token to <@{}>".format(fromuserid, dbEffect[3], touserid)



	def remove_one_effect(self, ctx, userid, effectid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		charge = True
		
		print("{} --> UserID: {}\nAuthor: {}\nIsEmployee: {}".format(time.strftime("%m/%d/%y %H:%M %Z"), userid, ctx.message.author.id, self.isOwlCoEmployee(ctx.message.author.id)))
		
		if userid != ctx.message.author.id and self.isOwlCoEmployee(ctx.message.author.id):
			charge = False
			print("{} --> Charge = {}".format(time.strftime("%m/%d/%y %H:%M %Z"), charge))
		
		cursor.execute("SELECT * from current where (Type = 'E' or Type = 'P') and ID = ? and userid = ?", (effectid, userid))
		dbEffect = cursor.fetchall()
		
		if len(dbEffect) == 0:
			return "That effect does not exist for <@{}>.".format(userid)
		
		dbEffect = dbEffect[0]
		
		if dbEffect[1] == "P":
			return "**Sorry, <@{}>! That effect is a penalty and can not be removed. It must expire on its own.**".format(userid)
		
		if charge:
			if not self.removeReward(userid, 'W'):
				if not self.isOwlCoEmployee(ctx.message.author.id):
					return "**Sorry, <@{}> doesn't have a WIN ticket to use for this action!  Play more!".format(userid)
		
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET RemovedFlag = 'Y', RemovedByUserID = ?, RemovedTimeStamp = ? WHERE (Type = 'E' AND UserID = ? AND ID = ?)" , (ctx.message.author.id, nowtime, userid, effectid))
		db.commit()
		db.close()
		
		print( "{} --> Removed __**{}**__ from <@{}>".format(time.strftime("%m/%d/%y %H:%M %Z"), dbEffect[3], userid))
		return "Removed __**{}**__ from <@{}>".format(dbEffect[3], userid)
		
		

	def remove_user_effects(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET RemovedFlag = 'Y', RemovedByUserID = ?, RemovedTimeStamp = ? WHERE Type = 'E' AND UserID = ?", (userid, nowtime, userid))
		db.commit()
		db.close()
		
	
	def remove_user_tokens(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET RemovedFlag = 'Y', RemovedByUserID = ?, RemovedTimeStamp = ? WHERE Type = 'T' AND UserID = ?", (userid, nowtime, userid))
		db.commit()
		db.close()


		
	def get_user_tokens(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("SELECT * FROM current WHERE (Type = 'T') AND RemovedFlag is null AND UserID = ? and Timestamp > ? ORDER BY Type ASC, Timestamp ASC", (userid, nowtime-86400))
		rval = cursor.fetchall()
		db.close()
		return rval
		
	def get_num_user_tokens(self, userid):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("SELECT count(*) FROM current WHERE (Type = 'T') AND RemovedFlag is null AND UserID = ? and Timestamp > ? ORDER BY Type ASC, Timestamp ASC", (userid, nowtime-86400))
		rval = cursor.fetchone()[0]
		db.close()
		return rval
		
	def summarize_user_tokens(self):
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("select UserID, count(UserID) as numTokens from current where type = 'T' and RemovedFlag is null and Timestamp > ? group by UserID order by numTokens DESC", (nowtime-86400,))
		rval = cursor.fetchall()
		db.close()
		return rval



	def throw_token(self, userid, tokenid, thrownAt):
		self.processTimeouts()
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		nowtime = int(time.time())
		cursor.execute("SELECT * FROM current WHERE ID = ? AND Type = 'T' and RemovedFlag is null AND UserID = ? and Timestamp > ? ORDER BY Type ASC, Timestamp ASC", (tokenid, userid, nowtime-86400))
		token = cursor.fetchall()
		print(token)
		if len(token) == 0:
			return "<@{}> does not have any such token!".format(userid)		
		token = token[0]
		
		if token[10] == 'Y':
			self.remove_category_effects(thrownAt, token[9])
		db.commit()
		cursor.execute("INSERT into current (Type, UserID, Effect, TimeStamp, ThrownBy, Category, RemovesCategory) values (?, ?, ?, ?, ?, ?, ?)", ("E", thrownAt, token[3], nowtime, userid, token[9], token[10]))
		db.commit()
		cursor.execute("UPDATE current SET RemovedFlag = 'Y', RemovedByUserID = ?, RemovedTimeStamp = ? WHERE (Type = 'T' AND UserID = ? AND ID = ?)" , (userid, nowtime, userid, token[0]))
		db.commit()
		db.close()
		
		if str(userid) == str(thrownAt):
			return "<@{0}> decides to keep the __**{1}**__ effect for themself! <@{0}> snaps the token & is covered in a shower of magical sparkles!".format(userid, token[3])
		else:
			return "<@{0}> throws a __**{1}**__ token at <@{2}>!  It hits, and <@{2}> glows slightly!".format(userid, token[3], thrownAt)
		
		
	
	def tokens(self, ctx, userid, numTokens=1):
		self.processTimeouts()
		output = ""
		charge = True
		
		if userid != ctx.message.author.id and self.isOwlCoEmployee(ctx.message.author.id):
			charge = False
		
		if numTokens > 10:
			output = "**Sorry!** A maximum of 10 tokens can be given out at any one time!"
			return output

		if numTokens > 1:
			output += "__**Oooh! Mega-win! {0} tokens for <@{1}>, coming right up!**__\n\n".format(numTokens, userid)
			
		if numTokens == 3:
			if charge:
				if not self.removeReward(userid, 'BJ'):
					if not self.isOwlCoEmployee(userid):
						output += "\n\n**Sorry!**  <@{}> doesn't have any more BJ tokens to use for this request.  Play more!".format(userid)
						return output
				else:
					charge = False
			
		for x in range(numTokens):	
			if charge:
				if not self.removeReward(userid, 'W'):
					if not self.isOwlCoEmployee(userid):
						output += "\n\n**Sorry!**  <@{}> doesn't have any more WIN tokens to use for this request.  Play more!".format(userid)
						return output
					
			effect = self.choose_random_effect()
			print(effect)
			token_id = self.store_effect("T", userid, "{} - {}".format(effect[1], effect[2]), effect[1], effect[4])
			if x >= 1:
				output += "\n"
			output += "**<@{0}> rolls a {1} and receives a __{2} - {3}__ token!! (ID # {4})**".format(userid, effect[0], effect[1], effect[2], token_id)	
				
		return output


	def effects(self, ctx, userid, numEffects, gender):
		self.processTimeouts()
		output = ""
		
		if numEffects > 10:
			output += "Sorry, a maximum of 10 effects can be given out at any one time!"
			return output
			
		if numEffects > 1:
			output += "__**Muhahaha! {0} effects for <@{1}>, coming right up!**__\n\n".format(numEffects, userid)
					
		charge = True
		
		if userid != ctx.message.author.id and self.isOwlCoEmployee(ctx.message.author.id):
			charge = False
			
		for x in range(numEffects):	
			if self.removeReward(userid, 'L') or not charge or self.isOwlCoEmployee(ctx.message.author.id):
				effect = self.choose_random_effect(gender)
				effect_id = self.store_effect("E", userid, "{} - {}".format(effect[1], effect[2]), effect[1], effect[4])
				if x >= 1:
					output += "\n"
				output += "**<@{0}> rolls a {1}, begins to glow slightly and gains: __{2} - {3}__ (ID #{4})**".format(userid, effect[0], effect[1], effect[2], effect_id)
			else:
				output += "\n\n**Sorry, but <@{}> doesn't have any more loss tickets to use for this request!**".format(userid)
				return output
				
		return output
		
	def customEffect(self, userid, effectText):
		self.processTimeouts()
		
		output = ""
		effect_id = self.store_effect("E", userid, effectText, "Custom")
		output = "**<@{}> beings to glow slightly and gains: __{}__ (ID #{})**".format(userid, effectText, effect_id)
		return output
		
	def customToken(self, userid, effectText):
		self.processTimeouts()
		
		output = ""
		token_id = self.store_effect("T", userid, effectText, "Custom")
		output = "**<@{0}> receives a __{1}__ token!! (ID # {2})**".format(userid, effectText, token_id)
		return output


	def penalties(self, userid, numPenalties=1):
		self.processTimeouts()
		output = ""
		#"__**Uh oh! Someone's in trouble! {0} effects for <@{1}>, coming right up!**__\n\n".format(numPenalties, userid)

		for x in range(numPenalties):	
			gender = self.getUserGender(userid)
			effect = self.choose_random_effect(gender)
			penalty_id = self.store_effect("P", userid, "{} - {}".format(effect[1], effect[2]), effect[1], effect[4])
			if x > 1:
				output += "\n"
			output += "**<@{0}> rolls a {1} and receives a __{2}__ penalty!! This penalty will remain for 24 hours!**".format(userid, effect[0], effect[1], penalty_id)
		
		return output

	@commands.command(hidden=True)
	async def getSummary(self, ctx):
		"""OwlCo Employee Use ONLY!"""
		
		if self.isOwlCoEmployee(ctx.message.author.id):
			summary = self.summarize_user_tokens()
			if len(summary) > 0:
				await ctx.send("The following users have tokens:")
				for user in summary:
					await ctx.send("<@{}> : {} token(s)".format(user[0], user[1]))
			else:
				await ctx.send("No users currently have tokens.")
				
			#do other summaries here
		else:
			await ctx.send("Sorry, but you don't have that kind of pull around here, <@{}>!".format(ctx.message.author.id))


	@commands.command(hidden=True, aliases=['hire'])
	async def addEmployee(self, ctx, userID):
		"""OwlCo Employee Use ONLY!"""
		userID = self.removeUserFormatting(userID)
		if self.isOwlCoEmployee(ctx.message.author.id):
			ocid = self.addOwlCoEmployee(userID)
			if ocid != 0:
				await ctx.send("<@{}> added as OwlCo employee #{}!".format(userID, ocid))
			else:
				await ctx.send("Hey! <@{}> is already an OwlCo employee!  I'm not giving more than one paycheck to 'em!".format(userID))
		else:
			await ctx.send("Sorry, but you don't have that kind of pull around here, <@{}>!".format(ctx.message.author.id))

	@commands.command()
	async def showRewards(self, ctx, *args):
		"""List the reward 'tickets' a user has."""
		self.processTimeouts()
		pargs = self.parse_args(args, ctx)
		num = pargs['num']
		userID = pargs['recipient']

		if self.isOwlCoEmployee(ctx.message.author.id) or userID == ctx.message.author.id:
			
			userRewards = self.getUserRewards(userID)
			if len(userRewards) > 0:
				o = "<@{}> has:".format(userID)
				for reward in userRewards:
					o += "\n{} {}s".format(reward[2], reward[1])
					
				o += "\n\nNOTE: Rewards expire one hour after being issued!  Use them or lose them!"
				await ctx.send(o)
			else:
				await ctx.send("<@{}> doesn't have any current rewards.".format(userID))
		else:
			await ctx.send("Sorry, only Employees can do that!")


	@commands.command(hidden=True)
	async def addWin(self, ctx, *args):
		"""OwlCo Employee Use ONLY!"""
		self.processTimeouts()
		if self.isOwlCoEmployee(ctx.message.author.id):
			pargs = self.parse_args(args, ctx)
			num = pargs['num']
			recipient = pargs['recipient']
			self.tallyReward(recipient, 'W')
			await ctx.send("Tallying a win for <@{}>".format(recipient))
		else:
			await ctx.send("Sorry, only Employees can do that!")

	@commands.command(hidden=True)
	async def addLoss(self, ctx, *args):
		"""OwlCo Employee Use ONLY!"""
		self.processTimeouts()
		if self.isOwlCoEmployee(ctx.message.author.id):
			pargs = self.parse_args(args, ctx)
			num = pargs['num']
			recipient = pargs['recipient']
			self.tallyReward(recipient, 'L')
			await ctx.send("Tallying a loss for <@{}>".format(recipient))
		else:
			await ctx.send("Sorry, only Employees can do that!")
			

	@commands.command(hidden=True)
	async def addBJ(self, ctx, *args):
		"""OwlCo Employee Use ONLY!"""
		self.processTimeouts()
		if self.isOwlCoEmployee(ctx.message.author.id):
			pargs = self.parse_args(args, ctx)
			num = pargs['num']
			recipient = pargs['recipient']
			self.tallyReward(recipient, 'BJ')
			await ctx.send("Tallying a blackjack for <@{}>".format(recipient))
		else:
			await ctx.send("Sorry, only Employees can do that!")
	
	#@commands.command()
	#async def useReward(self, ctx, rewardType='W'):
	#	userID = ctx.message.author.id
	#	if self.removeReward(ctx.message.author.id, rewardType):
	#		await ctx.send("Ok!  Removed {} ticket from <@{}>".format(rewardType, userID))
	#	else:
	#		await ctx.send("Sorry....<@{}> doesn't have a reward of {} type".format(userID, rewardType))

	@commands.command(aliases=['gender'])
	async def setGender(self, ctx, gender):
		userid = ctx.message.author.id
		if gender in "MFBmfb":
			output = "<@{}>, I set your gender to {}.".format(userid, self.setUserGender(userid, gender))
		else:
			output = "Hey, <@{}>....what gender was that again? (M = Male, F = Female, B = Both)".format(userid)
		await ctx.send( output)
		


	@commands.command(hidden=True, aliases=['sack'])
	async def sackEmployee(self, ctx, userID):
		"""OwlCo Employee Use ONLY!"""
		userID = self.removeUserFormatting(userID)
		if self.isOwlCoEmployee(ctx.message.author.id) and self.can_remove_employee(userID):
			ocid = self.removeOwlCoEmployee(userID)
			await ctx.send("<@{}> has been sacked. Security is on the way to escort them out of the building.".format(userID, ocid))
		else:
			await ctx.send("Sorry, but you don't have that kind of pull around here, <@{}>!".format(ctx.message.author.id))

	@commands.command()
	async def showEmployees(self, ctx):
		"""List OwlCo employees"""
		o = "__**The following are currently OwlCo employees:**__"
		oce = self.getOwlcoEmployees()
		for e in oce:
			o += "\n<@{}>".format(e)
		await ctx.send(o)

	@commands.command(aliases=['addce', 'addCE', 'ace'])
	async def addCustomEffect(self, ctx, *, effectText : str):
		"""OwlCo Employee Use ONLY!"""
		if self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send(self.customEffect(ctx.message.author.id, effectText))
		else:
			await ctx.send("Sorry, only an OwlCo employee can do that!")
		return
		
	@commands.command(aliases=['addct', 'addCT', 'act'])
	async def addCustomToken(self, ctx, *, effectText : str):
		"""OwlCo Employee Use ONLY!"""
		if self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send(self.customToken(ctx.message.author.id, effectText))
		else:
			await ctx.send("Sorry, only an OwlCo employee can do that!")
		return

	@commands.command(pass_context=True, aliases=['drop'])
	async def dropToken(self, ctx, tokenid):
		"""Drop a token."""
		userid = ctx.message.author.id
		self.processTimeouts()
		db = sqlite3.connect('Bimbot.sqlite')
		cursor = db.cursor()
		cursor.execute("SELECT * from current where Type = 'T' and ID = ? and userid = ?", (tokenid, userid))
		dbEffect = cursor.fetchall()
		
		if len(dbEffect) == 0:
			await ctx.send( "**Sorry! -** <@{}> doesn't have any such token!".format(userid))
			return
		
		dbEffect = dbEffect[0]
		nowtime = int(time.time())
		cursor.execute("UPDATE current SET RemovedFlag = 'Y', RemovedByUserID = ?, RemovedTimeStamp = ? WHERE (Type = 'T' AND UserID = ? AND ID = ?)" , (userid, nowtime, userid, tokenid))
		db.commit()
		db.close()		
		await ctx.send("<@{}> dropped a __**{}**__ token. It fades away into the ether.".format(userid, dbEffect[3]))


	@commands.command(pass_context=True, aliases=['dropAll', 'dropall'])
	async def dropAllTokens(self, ctx, *args):
		"""Drop all tokens."""
		pargs = self.parse_args(args, ctx)
		userID = pargs['recipient']
		
		if userID != ctx.message.author.id and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("Sorry, only an OwlCo employee can force a user to drop their tokens!")
			return
		
		self.remove_user_tokens(userID)
		await ctx.send("<@{}> drops all their tokens.  The tokens clatter on the ground, sparkle briefly, and fade into the ether.".format(userID))


	@commands.command(aliases=['remove'])
	async def removeEffect(self, ctx, *args):
		"""Removes an effect
		\nID is found by using !examine
		Examples:\n---------
		!removeEffect 2 -> removes effectID 2, as listed in your effects list"""
		pargs = self.parse_args(args, ctx)
		userID = pargs['recipient']
		effectID = pargs['num']
		
		if userID != ctx.message.author.id and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("Sorry, only an OwlCo employee can remove effects from a user other than themselves!")
			return
		
		await ctx.send(self.remove_one_effect(ctx, userID, effectID))


	@commands.command(aliases=['removeall', 'removeAll', 'removealleffects'])
	async def removeAllEffects(self, ctx, *args):
		"""Removes all effects"""
		pargs = self.parse_args(args, ctx)
		userID = pargs['recipient']
		charge = True
		
		if userID != ctx.message.author.id and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("Sorry, only an OwlCo employee can remove effects from a user other than themselves!")
			return
			
		if userID != ctx.message.author.id and self.isOwlCoEmployee(ctx.message.author.id):
			charge = False
			
		if charge:
			if not self.removeReward(userID, 'BJ'):
				if not self.isOwlCoEmployee(userID):
					await ctx.send( "**Sorry!** <@{}> doesn't have a BJ ticket to use for this action!  Play more!".format(userID))
					return
		
		self.remove_user_effects(userID)
		await ctx.send("All effects for <@{}> have been removed".format(userID))



	@commands.command()
	async def give(self, ctx, tokenID, giveTo):
		"""Gives a token to a user, so they can use it later
		\nUser must be specified in @user format
		\nID is found by using !mytokens
		\nExamples:\n---------
		\n!throw 12 @user -> gives a token to @user"""

		giveTo = self.removeUserFormatting(giveTo)
		await ctx.send(self.give_token(ctx.message.author.id, tokenID, giveTo))
		


	@commands.command(aliases=['lookAt', 'lookat', 'view', 'look'])
	async def examine(self, ctx, *args):
		"""Shows the effects active for a user.
		\nUser is optional & must be specified in @user format.
		"""
		
		pargs = self.parse_args(args, ctx)
		userid = pargs['recipient']
		effects = self.get_user_effects(userid)
		o = ""
		userGender = self.getUserGender(userid)
		if userGender == "M":
			o += "<@{}> is currently Male.\n\n".format(userid)
		elif userGender == "F":
			o += "<@{}> is currently Female.\n\n".format(userid)
		elif userGender == "B":
			o += "<@{}> currently is both Male AND Female.\n\n".format(userid)
		else:
			o += "<@{}> hasn't set their gender yet.\n\n".format(userid)
		if len(effects) > 0:
			count = 0
			o += "Here are the current effects for <@{}>:".format(userid)
			for e in effects:
				if count > 0 and count % 10 == 0:
					await ctx.send(o)
					o = "Continuing <@{}>'s effect list:".format(userid)
				count += 1
				idstring = ""
				if e[1] == "E":
					etype = "Effect:"
					idstring = "ID: {} = ".format(e[0])
				if e[1] == "P":
					etype = "__**Penalty:**__"
				seconds = 86400 - (int(time.time()) - int(e[4]))
				m, s = divmod(seconds, 60) # get seconds
				h, m = divmod(m, 60) # get hour & minute
				expires = "{}h {}m {}s".format(h, m, s)
				o += "\n{}{} __**{}**__ expires in {}".format(idstring, etype, e[3], expires)
				
				#If the effect was thrown by someone, note that in the output string
				if e[8] != None:
					o += " (Thrown by <@{}>)".format(e[8])
					
			if o != "":
				await ctx.send(o)
		else:
			o += "<@{}> has no current effects".format(userid)
			await ctx.send( o )
	
	
	@commands.command(name='mytokens', aliases=['showtokens', 'myTokens', 'inventory', 'inv'], pass_context=True)
	async def mytokens(self, ctx):
		"""Gets your current token inventory."""
		userID = ctx.message.author.id
		user = ctx.message.author
		await ctx.send("OK, <@{}>, I'll DM you your tokens list".format(userID))
		tokens = self.get_user_tokens(userID)
		if len(tokens) > 0:
			count = 0
			o = "Here are your current tokens:"
			for t in tokens:
				if count > 0 and count % 10 == 0:
					await user.send(o)
					o = "Continuing your token list:"
				count += 1
				seconds = 86400 - (int(time.time()) - int(t[4]))
				m, s = divmod(seconds, 60)
				h, m = divmod(m, 60)
				expires = "{}h {}m {}s".format(h, m, s)
				o += "\nID: {} = __**{}**__ expires in {}".format(t[0],t[3], expires)
				
			o += "\n\nYou may throw these tokens at another user by typing __**!throw tokenID @User**__"
			o += "\nYou may also give a token to another user by typing __**!give tokenID @User**__"
		
		else:
			o = "You currently have no tokens"
		await user.send(o)
	
	
	@commands.command(aliases=['snap', 'fumble'])
	async def throw(self, ctx, tokenID, thrownAt="SELF"):
		"""Throws a token at a user 
		\nUser must be specified in @user format
		\nID is found by using !mytokens
		\nExamples:\n---------
		\n!throw 12 @user -> throws a token at @user
		\n\n**NOTE:** OwlCo has asked me to inform you that tokens expire 24 hours after their creation, and are valid in the casino and wherever fine OwlCo tokens are accepted."""
		userID = ctx.message.author.id

		if thrownAt == "SELF":
			thrownAt = userID
		else:
			thrownAt = self.removeUserFormatting(thrownAt)
		
			
		if self.has_token(userID, tokenID):
			if thrownAt == self.bot.user.id:
				await ctx.send("**Costly mistake!  The token bounces off the Dealer and drops to the floor.\n{}".format(self.drop_token(userID, tokenID)))
				await ctx.send("**Silly bimbo!**  The OwlCo dealer is immune from your treachery! Assume the position for your ~~spanking~~ penalty...\n\n{}".format(self.penalties(userID,1)))
				return
			else:
				await ctx.send(self.throw_token(userID, tokenID, thrownAt))

		else:
			await ctx.send("Ooops! You don't have that token!")
			return


	@commands.command(aliases=['tokens'])		
	async def token(self, ctx, *args):
		"""Gives randomly-chosen tokens to a user! \nUser is optional & must be specified in @user format.
		\nAlso accepts an optional number for # of tokens given!
		\nExamples:\n---------
		\n!token -> gives a single token to the caller
		\n!token 2 -> gives two tokens to the caller  
		\n!token @user -> gives a single token to the target @user
		\n!token @user 2 -> gives two tokens to the target @user
		\n\n**NOTE:** OwlCo has asked me to inform you that tokens are only effective for 24 hours after their creation, and are valid in the casino and wherever fine OwlCo tokens are accepted."""
		
		if ctx.message.guild is None and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("Issuing of tokens is not allowed in private chat!")
			return
		
		pargs = self.parse_args(args, ctx)
		num = pargs['num']
		recipient = pargs['recipient']
		
		num_tokens = self.get_num_user_tokens(recipient)
		if num_tokens >= self.TOKEN_LIMIT or num_tokens + num > self.TOKEN_LIMIT:
			await ctx.send("**Sorry!** OwlCo has limited the number of tokens that can be held by any one user to {}.\n<@{}> currently has {} tokens.".format(self.TOKEN_LIMIT, recipient, num_tokens))
			await ctx.send("Either ask for fewer tokens, or else __!drop__ or __!throw__ some tokens before asking for more")
			return
		
		if recipient == self.bot.user.id:
			await ctx.send("**Naughty bimbo!**  The OwlCo dealer is immune from your bribery! Assume the position...\n\n{}".format(self.penalties(ctx.message.author.id,1)))
			return
			
		if recipient != ctx.message.author.id and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("**Silly bimbo!**  Only OwlCo Employees can issue tokens to other people!")
			return
			
		await ctx.send(self.tokens(ctx, recipient, num))
	
	
	
		
	@commands.command(aliases=['effects'])
	async def effect(self, ctx, *args):
		"""Conveys randomly-chosen effects onto a user! \nUser is optional & must be specified in @user format.
		\nAlso accepts an optional number for # of effects rendered!
		\nExamples:\n---------
		\n!effect -> renders a single effect onto the caller
		\n!effect 2 -> renders two effects onto the caller  
		\n!effect @user -> renders a single effect onto the target @user
		\n!effect @user 2 -> renders two effects onto the target @user
		\n\n**NOTE:** OwlCo has asked me to inform you that effects last 24 hours from their inception."""
		
		if ctx.message.guild is None:
			await ctx.send("Issuing of effects is not allowed in private chat!")
			return
		
		pargs = self.parse_args(args, ctx)
		num = pargs['num']
		recipient = pargs['recipient']
		
		gender = self.getUserGender(recipient)


		if gender is None:
			await ctx.send("Sorry, but I need to know <@{}>'s gender before issuing an effect.  Please use type __!gender M__, __!gender F__, or __!gender B__ to set your current character gender".format(recipient))
			return

		if recipient == self.bot.user.id:
			await ctx.send("**Silly bimbo!**  The OwlCo dealer is immune from all effects! Assume the position...\n\n{}".format(self.penalties(ctx.message.author.id,1)))
			return
		
		if recipient != ctx.message.author.id and not self.isOwlCoEmployee(ctx.message.author.id):
			await ctx.send("**Silly bimbo!**  Only OwlCo employees can give other users effects! Assume the position...\n\n{}".format(self.penalties(ctx.message.author.id,1)))
			return
		
		o = self.effects(ctx, recipient, num, gender)
		await ctx.send(o)
	


	async def cannon(self, bot, channel):
		eligible = self.get_last_seen(600)  # 600 = 10 minutes seen time
		possible = ['E', 'E', 'E', 'T', 'T', 'N']
		await channel.send("__**BOOM!  The Bimbo Cannon goes off, showering the room in BetYourBimbo tokens!**__")
		if eligible == []:
			await channel.send("__**Oh no!**__  No one's around....All of the tokens & effects fade into the ether.\nBetter luck next time!")
			return
		
		for userID in eligible:
			gender = self.getUserGender(userID)
			if gender is None:
				gender = "B"
			hitwith = random.choice(possible)
			if hitwith == "E":
				effect = self.choose_random_effect(gender)
				effect_id = self.store_effect("E", userID, "{} - {}".format(effect[1], effect[2]), effect[1], effect[4])
				await channel.send("<@{0}> is hit by a **{1} - {2}** token, which pops! (ID#{3}) <@{0}> glows brightly for a moment.... ".format(userID, effect[1], effect[2],  effect_id))
			elif hitwith == "T":
				effect = self.choose_random_effect('B')
				effect_id = self.store_effect("T", userID, "{} - {}".format(effect[1], effect[2]), effect[1], effect[4])
				await channel.send("<@{}> catches a **{} - {}** token and pockets it! (ID#{})".format(userID, effect[1], effect[2], effect_id))
			else:
				await channel.send("<@{}> is missed completely. Better luck next go!".format(userID))
		return
		
	@commands.command(aliases=['boom', 'takeCover', 'takecover'])
	async def fireCannon(self, ctx):
		if self.isOwlCoEmployee(ctx.message.author.id):
			await self.cannon(self.bot, ctx.message.channel)
		else:
			await channel.send("Sorry, only OwlCo Employees are allowed near the cannon!")
	
	def __init__(self, bot):
		self.bot = bot

	
def setup(bot):
	bot.add_cog(BetYourBimbo(bot))




