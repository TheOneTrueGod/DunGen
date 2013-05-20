import sys
from pygame.locals import *
from Globals import *
import Abilities
EquipmentSlots = enum('RightHand', 'LeftHand',   'Head',   'Chest',     'Glove',    'Feet',     'LeftRing', 'RightRing', 'Potion1',  'Potion2',  'Potion3')
EmptyPics =           ["NoWeapon", "NoOffhand", "NoHelm", "ShirtSlot", "NoGloves", "NoBoots",    "NoRing",   "NoRing",   "NoPotion", "NoPotion", "NoPotion"]
EmptyPics =           [["slots",[0, 0]], ["slots",[1, 0]], ["slots",[2, 0]], ["slots",[3, 0]], ["slots",[4, 0]], ["slots",[5, 0]], ["slots",[6, 0]], ["slots",[6, 0]], ["slots",[7, 0]], ["slots",[7, 0]], ["slots",[7, 0]]]
class Equipment:
	def __init__(self, owner):
		self.equipmentIteration = 0
		self.owner = owner
		self.cash = 0
		self.inventory = [Item("WoodSword", owner), Item("WoodDagger", owner), Item("PineBow", owner)]
		self.equipped = [Item("WoodDagger", owner), Item("WoodDagger", owner), None, None, None, None, None, None, None, None, None]
		self.cachedStats = { "KEYWORDS":{}}
		self.baseAttack = Abilities.BasicAttack(owner)
		self.currentHand = 0
		
	def switchHands(self):
		if self.equipped[0] != None and self.equipped[1] != None:
			if (self.equipped[1 - self.currentHand].getStat("ITEMTYPE") == "weapon" or \
				  self.equipped[self.currentHand].getStat("ITEMTYPE") != "weapon"):
				self.currentHand = 1 - self.currentHand
				self.equipmentIteration += 1
		elif self.equipped[self.currentHand] == None and self.equipped[1 - self.currentHand] != None:
			self.currentHand = 1 - self.currentHand
			self.equipmentIteration += 1
			
	def getHand(self):
		return self.currentHand
		
	def giveNewItem(self, itemName):
		if len(self.inventory) < INVENTORYSLOTS:
			newItem = Item(itemName, self.owner)
			self.inventory += [newItem]
			return newItem
		else:
			if itemName.upper() not in ["NONE", "NOTHING"] and not os.path.exists(os.path.join("Data", "Equipment", itemName + ".txt")):
				print "ERROR in Equipment.giveNewItem:  ", itemName, "not found."
		return None
			
	def getPrimaryWeapon(self):
		if self.equipped[self.currentHand] and self.equipped[self.currentHand].getStat("ITEMTYPE") == "weapon":
			return self.equipped[self.currentHand]
		return None
		
	def getRange(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getRange()
		return 50
		
	def getDamageMod(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStat("DAMAGE")
		return 1
		
	def getMaxUnitsHit(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStat("MAXUNITSHIT")
		return 2
		
	def getAttackTime(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStat("SPEED")
		return 30
		
	def getKnockbackAmount(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getKnockbackAmount()
		return 1
		
	def getStunFactorAmount(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStunFactorAmount()
		return 1
		
	def getDamageType(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStat("DAMAGETYPE")
		return 3
		
	def getCooldown(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getStat("COOLDOWN")
		return 20
		
	def getProjectile(self):
		weap = self.getPrimaryWeapon()
		if weap:
			if not weap.getProjectile():
				return weap.getImage()
			else:
				return weap.getProjectile()
		return "Slash"
		
	def getAttack(self):
		weap = self.getPrimaryWeapon()
		if weap:
			return weap.getAttack()
		return self.baseAttack
		
	def getStatEffectedEquipment(self):
		toRet = self.equipped[2:] + [self.equipped[self.currentHand]]
		if self.equipped[0] and self.equipped[0].getStat("ITEMTYPE") != "weapon":
			toRet += [self.equipped[0]]
		if self.equipped[1] and self.equipped[1].getStat("ITEMTYPE") != "weapon":
			toRet += [self.equipped[1]]
		return toRet
		
	def getResistance(self, resNum):
		if 0 <= resNum < numDamageTypes:
			if "RESISTANCES" in self.cachedStats and self.cachedStats["RESISTANCES"][0] == self.equipmentIteration:
				return self.cachedStats["RESISTANCES"][1][resNum]
			resList = [0] * numDamageTypes
			checked = {}
			
			for e in self.getStatEffectedEquipment():
				if e and e not in checked:
					checked[e] = True
					reses = e.getStat("RESISTANCES")
					on = 0
					for i in reses:
						resList[on] += (1 - resList[on]) * i
						on += 1
			self.cachedStats["RESISTANCES"] = [self.equipmentIteration, resList]
			return self.getResistance(resNum)
		return 0
		
	def getKeyword(self, keyword):
		if keyword in self.cachedStats["KEYWORDS"] and self.cachedStats["KEYWORDS"][keyword][0] == self.equipmentIteration:
			return self.cachedStats["KEYWORDS"][keyword][1]
		total = 0
		for e in self.getStatEffectedEquipment():
			checked = {}
			if e and e not in checked:
				checked[e] = True
				if keyword in e.getStat("KEYWORDS"):
					total += (1 - total) * float(e.getStat("KEYWORDS")[keyword])
		self.cachedStats["KEYWORDS"][keyword] = [self.equipmentIteration, total]
		return total
		
	def getStat(self, stat):
		if stat in self.cachedStats and self.cachedStats[stat][0] == self.equipmentIteration:
			return self.cachedStats[stat][1]
		toAdd = []
		checked = {}
		for e in self.getStatEffectedEquipment():
			if e and e not in checked:
				checked[e] = True
				toAdd += [e.getStat(stat)]
		self.cachedStats[stat] = [self.equipmentIteration, sum(toAdd)]
		return self.getStat(stat)
		
	def getStatMod(self, stat):
		if "m" + stat in self.cachedStats and self.cachedStats["m" + stat][0] == self.equipmentIteration:
			return self.cachedStats["m" + stat][1]
		total = 1
		checked = {}
		for e in self.getStatEffectedEquipment():
			if e and e not in checked:
				checked[e] = True
				total *= e.getStat(stat)
		self.cachedStats["m" + stat] = [self.equipmentIteration, total]
		return self.getStat(stat)
		
	def addCash(self, amount):
		self.cash = max(self.cash + amount, 0)
		
	def equipItem(self, slotNum):
		if 0 <= slotNum < len(self.inventory):
			item = self.inventory[slotNum]
		else:
			return False
		
		if item.getStat("MULTISLOT"):
			if len(self.inventory) < INVENTORYSLOTS - len(item.getSlots()) + 1:
				for slot in item.getSlots():
					if not self.unequipItem(slot):
						return
				#Have to do this twice so that we don't wind up having an item "half-equipped"
				for slot in item.getSlots():
					self.equipped[slot] = item
				del self.inventory[slotNum]
		else:
			equipIn = item.getSlots()[0]
			for slot in item.getSlots():
				if 0 <= slot < len(self.equipped) and self.getEquippedItem(slot) == None:
					equipIn = slot
					break
				
			if self.unequipItem(equipIn):
				self.equipped[equipIn] = item
				del self.inventory[slotNum]
		self.equipmentIteration += 1
					
	def unequipItem(self, slotNum):
		if slotNum in [0, 1] and self.equipped[slotNum] and self.equipped[slotNum].getStat("MULTISLOT") and len(self.inventory) < INVENTORYSLOTS - 2:
			self.inventory += [self.equipped[0]]
			self.equipped[1] = None
			self.equipped[0] = None
			self.equipmentIteration += 1
		elif 0 <= slotNum < len(self.equipped) and self.equipped[slotNum] and len(self.inventory) < INVENTORYSLOTS - 1:
			self.inventory += [self.equipped[slotNum]]
			self.equipped[slotNum] = None
			self.equipmentIteration += 1
		elif not self.equipped[slotNum]:
			return True
		else:
			return False
		return True
		
	def getEquippedItems(self):
		return self.equipped
		
	def getEquippedItem(self, slot):
		if 0 <= slot < len(self.equipped):
			return self.equipped[slot]
		return None
		
	def getInventoryItem(self, slot):
		if 0 <= slot < len(self.inventory):
			return self.inventory[slot]
		return None
		
	def getInventory(self):
		toRet = self.inventory + [None] * max(INVENTORYSLOTS - len(self.inventory), 0)
		return toRet[:INVENTORYSLOTS]
		
	def getSpeedMod(self):
		return 1
		
	def handleUpdates(self, pl):
		pass
		
class Item:
	def __init__(self, file, owner):
		self.owner = owner
		self.attributes = {}
		for attr in itemTable[file]:
			self.attributes[attr] = itemTable[file][attr]
		for attr in ["BASICATTACK", "ABILITY"]:
			if self.attributes[attr]:
				self.attributes[attr] = self.attributes[attr](self.owner)
		
	def getDamageType(self):
		dType = self.getStat("DAMAGETYPE")
		if 0 <= dType < numDamageType:
			return dType
		return 0
		
	def getAttack(self):
		if "BASICATTACK" in self.attributes:
			return self.attributes["BASICATTACK"]
		return None
		
	def isMeleeWeapon(self):
		return self.attributes["MELEE"]
		
	def getRange(self):
		return self.attributes["RANGE"]
		
	def getKnockbackAmount(self):
		return self.attributes["KNOCKBACK"]
		
	def getStunFactorAmount(self):
		return self.attributes["STUNFACTOR"]
		
	def getProjectile(self):
		return self.attributes["PROJECTILE"]
			
	def getStat(self, stat):
		if stat.upper() in self.attributes:
			return self.attributes[stat.upper()]
		return 0
		
	def getSlots(self):
		return self.attributes["SLOTS"]
		
	def getImage(self):
		return [self.attributes["ITEMTYPE"], self.attributes["ICON"]]
		
	def getDescription(self):
		toRet = self.attributes["DESCRIPTION"] + "\n"
		on = 1
		for stat in ["attack", "defense"]:
			toRet += str(stat) + ":" + str(int(self.getStat(stat))) + "     "
			if on % 4 == 0:
				toRet += "\n"
			on += 1
		return toRet

treasureTable = {}
itemTable = {}

def loadTreasureTables():		
	for file in os.listdir(os.path.join("Data", "EquipmentDrops")):
		treasureTable[file[:-4]] = [[]]
		fileIn = open(os.path.join("Data", "EquipmentDrops", file))
		on = 0
		for line in fileIn:
			line = line.strip().split()
			if line[0].upper() == "AND":
				treasureTable[file[:-4]] += [[]]
				normalize(treasureTable[file[:-4]][on])
				on += 1
			else:
				treasureTable[file[:-4]][on] += [[float(line[0]), line[1]]]
		normalize(treasureTable[file[:-4]][on])
		fileIn.close()

def loadItemTables():
	fileIn = open(os.path.join("Data", "Equipment", "itemTable.csv"))
	line = fileIn.readline()
	cols = line.strip().split(",")
	for line in fileIn:
		line = line.strip().split(",")
		itemName = line[0].strip("\"")
		if not line[1] == line[2] == line[3] == line[4] == line[5] == line[6] == line[7] == "":
			if itemName != "DEFAULT":
				if itemName not in itemTable:
					itemTable[itemName] = {}
				for on in range(len(line)):
					if loadItemStat(itemName, cols[on].strip("\""), line[on].strip("\"")):
						pass
					
def loadItemStat(itemName, stat, inputValue):
	if stat in baseItemStats:
		if stat.upper() in baseItemStats:
			#Handle some special cases
			if stat.upper() == "DESCRIPTION":
				itemTable[itemName]["DESCRIPTION"] = inputValue.replace("<br>", "\n")
			elif stat.upper() in ["BASICATTACK", "ABILITY"]:
				if inputValue.upper() in Abilities.abilList:
					itemTable[itemName][stat.upper()] = Abilities.abilList[inputValue.upper()]
				else:
					if inputValue != None and inputValue.upper() not in ["NONE", "NOTHING"]:
						print "Error in loadItemStat:", inputValue, "not in Abilities.abilList"
					itemTable[itemName][stat.upper()] = None
			#Handle keywords
			elif stat.upper() == "KEYWORDS":
				itemTable[itemName][stat.upper()] = {}
				for kwPair in inputValue.split("_"):
					if kwPair:
						keyword, value = inputValue.split(":")
						itemTable[itemName][stat.upper()][keyword] = float(value)
			#Handle lists
			elif type(baseItemStats[stat.upper()]) == type([]):
				list = inputValue.split("_")
				itemTable[itemName][stat.upper()] = [0] * len(baseItemStats[stat.upper()])
				if stat.upper() == "RESISTANCES":
					on = 0
					for i in list:
						itemTable[itemName][stat.upper()][on] = float(i)
						on += 1
				elif list and isInt(list[0]):
					itemTable[itemName][stat.upper()] = intOf(list)
				else:
					itemTable[itemName][stat.upper()] = list
			#Booleans
			elif type(baseItemStats[stat.upper()]) == type(False):
				itemTable[itemName][stat.upper()] = inputValue.upper() == "TRUE"
			#Etc...
			elif isInt(baseItemStats[stat.upper()]) and "." not in str(baseItemStats[stat.upper()]):
				if isInt(inputValue):
					itemTable[itemName][stat.upper()] = int(inputValue)
			elif isFloat(inputValue):
				itemTable[itemName][stat.upper()] = float(inputValue)
			else:
				itemTable[itemName][stat.upper()] = inputValue
		return True
	return False
		
def getRandomTreasure(treasureName, depth=1):
	if depth >= 50 or treasureName.upper() in ["NONE", "NOTHING"]:
		return []
	if not treasureName in treasureTable:
		print "ERROR IN GetRandomTreasure: ", treasureName, "not found!"
		return []
	toRet = []
	for treasureList in treasureTable[treasureName]:
		selected = randFromNormalizedList(treasureList)
		if selected[:2].upper() == "G_":
			toRet += getRandomTreasure(selected[2:], depth + 1)
		else:
			toRet += [selected]
	return toRet

def awardBounty(killer, deadUnit):
	if random.random() < deadUnit.getStat("treasureChance"):
		killer.giveTreasure(getRandomTreasure(deadUnit.getStat("treasurePackage")))
		
baseItemStats = {"ICON":[0, 0], 
								 "SLOTS":[0, 1], 
								 "DESCRIPTION":"Just a quick description.\nShould be replaced.",
								 "BASICATTACK":"None",
								 "COOLDOWN":20,
								 "ABILITY":"None",
								 "ATTACK":0,
								 "DEFENSE":0,
								 "DAMAGE":0,
								 "MAXUNITSHIT":1,
								 "RANGE":50,
								 "MULTISLOT":False,
								 "PROJECTILE":"",
								 "DAMAGETYPE":damageTypes.SLASH,
								 "RESISTANCES":[0] * numDamageTypes,
								 "MELEE":True,
								 "KNOCKBACK":1.0,
								 "STUNFACTOR":1.0,
								 "MOVESPEED":1.0,
								 "ITEMTYPE":"none",
								 "KEYWORDS":{},
								 "SPEED":30,
								 "DAMAGE":1.0}
loadItemTables()
loadTreasureTables()

def printItemChances(itemName, baseChance = 1, indentation=""):
	print indentation + str(round(baseChance * 10000) / 100.0) + "% " + str(itemName)
	if itemName[:2] == "G_":
		on = 0
		for itemGroup in treasureTable[itemName[2:]]:
			on += 1
			for item in itemGroup:
				printItemChances(item[1], item[0] * baseChance, indentation + ". ")
			if on < len(treasureTable[itemName[2:]]):
				print indentation.replace(".", " ") + "  " + "+"
if "-printProb" in sys.argv:
	for item in treasureTable:
		printItemChances("G_" + item, 1, "")