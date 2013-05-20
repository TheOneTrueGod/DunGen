import math, os
from Globals import *
enemyStats = {}
										 
def loadAllEnemies(floor):
	from Abilities import enemyAbilList
	if floor not in enemyStats:
		print "Loading Enemies"
		baseStats["ability"] = [[enemyAbilList["PROJECTILE"], []]]
		enemyStats[floor] = {}
		fileIn = open(os.path.join("Data", "Enemies", str(floor), "EnemyStats.csv"))
		line = fileIn.readline()
		cols = line.strip().split(",")
		for line in fileIn:
			line = line.strip().split(",")
			enemyType = line[0].strip("\"")
			if enemyType != "DEFAULT":
				if enemyType not in enemyStats[floor]:
					enemyStats[floor][enemyType] = {}
				for on in range(len(line)):
					if loadEnemyStat(floor, enemyType, cols[on].strip("\""), line[on].strip("\"")):
						pass
						
def loadEnemyStat(floor, enemyType, stat, inputValue):
	from Abilities import enemyAbilList
	if stat in baseEnemyStats:
		if stat == "ability":
			enemyStats[floor][enemyType]["ability"] = []
			for abil in inputValue.split("_"):
				abilInfo = abil.split(" ")
				if abilInfo[0].upper() not in enemyAbilList:
					print "ERROR IN LOADENEMYSTATS:", abilInfo[0].upper(), "NOT IN ENEMYABILLIST"
				else:
					params = []
					if len(abilInfo) > 1:
						params = abilInfo[1:]
					enemyStats[floor][enemyType]["ability"] += [[enemyAbilList[abilInfo[0].upper()], params]]
		elif stat == "resistances":
			if "resistances" not in enemyStats[floor][enemyType]:
				enemyStats[floor][enemyType]["resistances"] = [k for k in baseEnemyStats["resistances"]]
			list = inputValue.split("_")
			on = 0
			for i in list:
				enemyStats[floor][enemyType]["resistances"][on] = float(i)
				on += 1
		elif stat == "keywords":
			if "keywords" not in enemyStats[floor][enemyType]:
				enemyStats[floor][enemyType]["keywords"] = {}
			for kwPair in inputValue.split("_"):
				if kwPair:
					keyword, value = inputValue.split(":")
					enemyStats[floor][enemyType]["keywords"][keyword] = float(value)
		elif isInt(inputValue):
			enemyStats[floor][enemyType][stat] = int(inputValue)
		elif isFloat(inputValue):
			enemyStats[floor][enemyType][stat] = float(inputValue)
		else:
			enemyStats[floor][enemyType][stat] = inputValue
		return True
	return False
											 
baseStats = {"defense":100, 
						 "attack" :100,
						 "health" :10,
						 "knockbackResistance":0.0,
						 "moveSpeed":2}
						 
baseEnemyStats = { "defense":100, 
									 "attack" :100,
									 "health":29,
									 "listenRad":90,
									 "alertedListenRad":200,
									 "preferredRange":190,
									 "activateRange":230,
									 "walkSpeed":2,
									 "chargeDist":80,
									 "picture":"noPic",
									 "ability":[],
									 "resistances":[0] * numDamageTypes,
									 "experience":100,
									 "treasureChance":0.0,
									 "treasurePackage":"None",
									 "stunResistance":0.0,
									 "knockbackResistance":0.0,
									 "unitType":0,
									 "keywords":{}}
									 
MagicDamageExpressions = {"Low":{"Single":16, "Area":10}, 
													"Medium":{"Single":25, "Area":15}, 
													"High":{"Single":50, "Area":30}, 
													"Extreme":{"Single":90, "Area":50}}
									 
def calcDamage(attack, defense, baseDamage=0):
	toRet = max(attack / 5.0 - defense / 10.0, 0.5) / 2.0
	return toRet * random.uniform(0.8, 1.2)
	
def calcSpellDamage(baseDamage, spellLevel):
	toRet = baseDamage + baseDamage * (spellLevel / 10.0) * 0.9
	return toRet * random.uniform(0.8, 1.2)
					
def calcKnockback(angle, target, amount = 1):
	val = amount
	return [math.cos(angle) * val, math.sin(angle) * val]