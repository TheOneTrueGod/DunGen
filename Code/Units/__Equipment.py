from pygame.locals import *
from Globals import *
import Abilities
EquipmentSlots = enum('RightHand', 'LeftHand',   'Head',   'Chest',     'Glove',    'Legs',    'Feet',     'LeftRing', 'RightRing', 'Potion1',  'Potion2',  'Potion3')
EmptyPics =           ["NoWeapon", "NoOffhand", "NoHelm", "ShirtSlot", "NoGloves", "NoPants", "NoBoots",    "NoRing",   "NoRing",   "NoPotion", "NoPotion", "NoPotion"]
class Equipment:
	def __init__(self, owner):
		self.equipmentIteration = 0
		self.owner = owner
		self.cash = 0
		self.inventory = [Item("PineBow", owner), Item("StoneSword", owner)]
		self.equipped = [None, None, None, None, None, None, None, None, None, None, None, None]
		self.cachedStats = {}
		self.baseAttack = Abilities.SwordsmanAbil(owner)
		
	def giveNewItem(self, itemName):
		if len(self.inventory) < INVENTORYSLOTS:
			self.inventory += [Item(itemName, self.owner)]
		
	def getAttack(self):
		if self.equipped[EquipmentSlots.RightHand]:
			if self.equipped[EquipmentSlots.RightHand].getAttack():
				return self.equipped[EquipmentSlots.RightHand].getAttack()
		if self.equipped[EquipmentSlots.LeftHand]:
			if self.equipped[EquipmentSlots.LeftHand].getAttack():
				return self.equipped[EquipmentSlots.LeftHand].getAttack()
		return self.baseAttack
		
	def getStat(self, stat):
		if stat in self.cachedStats and self.cachedStats[stat][0] == self.equipmentIteration:
			return self.cachedStats[stat][1]
		toAdd = []
		for e in self.equipped:
			if e:
				toAdd += [e.getStat(stat)]
		self.cachedStats[stat] = [self.equipmentIteration, sum(toAdd)]
		return self.cachedStats[stat][1]
		
	def addCash(self, amount):
		self.cash = max(self.cash + amount, 0)
		
	def equipItem(self, slotNum):
		if 0 <= slotNum < len(self.inventory):
			item = self.inventory[slotNum]
			equipIn = item.getSlots()[0]
			for slot in item.getSlots():
				if 0 <= slot < len(self.equipped) and self.getEquippedItem(slot) == None:
					equipIn = slot
					break
			if self.getEquippedItem(equipIn) != None:
				self.inventory[slotNum] = self.getEquippedItem(equipIn)
			else:
				del self.inventory[slotNum]
			self.equipped[equipIn] = item
			self.equipmentIteration += 1
			
	def unequipItem(self, slotNum):
		if 0 <= slotNum < len(self.equipped) and len(self.inventory) < INVENTORYSLOTS:
			self.inventory += [self.equipped[slotNum]]
			del self.equipped[slotNum]
			self.equipmentIteration += 1
		
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
		self.attributes = {"ICON":"Sword", "SLOTS":[0, 1], 
											 "DESCRIPTION":"Just a quick description.\nShould be replaced in " + file + ".txt",
											 "ABILITY":"None",
											 "ATTACK":0,
											 "DEFENSE":0,
											 "DAMAGE":0,
											 "RANGE":0}
		self.loadFromFile(file)
		
	def getAttack(self):
		if "ABILITY" in self.attributes:
			return self.attributes["ABILITY"]
		return None
		
	def loadFromFile(self, file):
		fileIn = open(os.path.join("Data", "Equipment", file + ".txt"))
		for line in fileIn:
			line = line.strip().split()
			if line[0].upper() in self.attributes:
				if type(self.attributes[line[0].upper()]) == type([]):
					list = line[1].split(",")
					if list and isInt(list[0]):
						self.attributes[line[0].upper()] = intOf(list)
					else:
						self.attributes[line[0].upper()] = list
				elif len(line) > 1 and isFloat(line[1]):
					self.attributes[line[0].upper()] = float(line[1])
				elif len(line) > 1:
					self.attributes[line[0].upper()] = " ".join(line[1:])
		fileIn.close()
		self.attributes["DESCRIPTION"] = self.attributes["DESCRIPTION"].replace("<br>", "\n")
		if self.attributes["ABILITY"].upper() in Abilities.abilList:
			self.attributes["ABILITY"] = Abilities.abilList[self.attributes["ABILITY"].upper()](self.owner)
		else:
			self.attributes["ABILITY"] = None
		
	def getStat(self, stat):
		if stat.upper() in self.attributes:
			return self.attributes[stat.upper()]
		return 0
		
	def getSlots(self):
		return self.attributes["SLOTS"]
		
	def getImage(self):
		return self.attributes["ICON"]
		
	def getDescription(self):
		return self.attributes["DESCRIPTION"]
		
equipmentList = {1:[[], [], []]}
fileIn = open(os.path.join("Data", "Equipment", "EquipmentList.txt"))
level = 1
for line in fileIn:
	line = line.strip().split("|")
	if len(line) == 1:
		level = int(line[0])
		if level not in equipmentList:
			equipmentList[level] = [[], [], []]
	else:
		if len(line) >= 2 and int(line[1]) > 0:
			equipmentList[level][0] += [[int(line[1]), line[0]]]
		if len(line) >= 3 and int(line[2]) > 0:
			equipmentList[level][1] += [[int(line[2]), line[0]]]
		if len(line) >= 4 and int(line[3]) > 0:
			equipmentList[level][2] += [[int(line[3]), line[0]]]
for key in equipmentList:
	for i in range(len(equipmentList[key])):
		normalize(equipmentList[key][i])
fileIn.close()
	