#Potential gods:  God of Good, God of Money, God of War, God of Chaos
from Globals import *
import Code.Engine.Effects as Effects
import Code.Units.Buffs as Buffs
TimeBetweenMoveTicks = 15
class FavourStruct:
	def __init__(self, unit):
		self.gods = [Nature(unit), Water(unit), Death(unit)]
		self.unit = unit
		self.nextMoveTick = 0
	
	def moveTick(self):
		if self.nextMoveTick <= 0:
			self.nextMoveTick = TimeBetweenMoveTicks
			for g in self.gods:
				g.moveTick()
		self.nextMoveTick -= 1
		
	def hitTarget(self, target, amount):
		for g in self.gods:
			g.hitTarget(target, amount)
		
	def takeDamage(self, amount, source, damageType):
		for g in self.gods:
			g.takeDamage(amount, source, damageType)
	
class NoGod:
	PassiveNoWorshipAmount = -0.01
	PassiveWorshipAmount = 0.02
	MaxWorshipTime = 3 * 2 #3 ~= 1 second
	Image = [0, 0]
	FavourLevels = [-350, -250, -150, -50, 50, 150, 250]
	FavourNames = ["Cursed", "Loathe", "Hate", "Dislike", "Neutral", "Like", "Favour", "Adore", "Blessed"]
	DisplayName = "NoGod"
	def __init__(self, unit):
		self.unit = unit
		self.childInit()
		self.worshipPos = [-10, -10]
		self.worshipTime = 0
		self.unitLastPos = [-10, -10]
		self.worshippedAt = {}
		self.favour = 0
		self.beingWorshipped = False
		self.worshipFrame = 0
		self.interactedAt = {}
		
	def modFavour(self, amount):
		if self.shrineInRange(1):
			amount *= 2
		if not self.beingWorshipped:
			amount *= 0.25
		self.favour += amount
		
	def getFavourPct(self):
		favourLevel = min(max(self.favour - self.FavourLevels[0], 0), self.FavourLevels[len(self.FavourLevels) - 1] - self.FavourLevels[0])
		return favourLevel / float(self.FavourLevels[len(self.FavourLevels) - 1] - self.FavourLevels[0])
		
	def getFavourColour(self):
		favourPct = self.getFavourPct()
		c = pygame.Color(0, 0, 0, 0)
		c.hsva = [int(favourPct * 240), 100, 100, 100]
		return c
		
	def getFavourName(self, favourLevel):
		return self.FavourNames[favourLevel]
		
	def getFavourLevel(self):
		lv = 0
		while lv < len(self.FavourLevels):
			if self.favour < self.FavourLevels[lv]:
				return lv
			lv += 1
		return lv
		
	def childInit(self):
		pass
		
	def moveTick(self):
		self.checkForWorshipping()
		room = GetDungeonGrid(self.unit.floor).getRoom(posToDungeonGrid(self.unit.getPos()))
		if room not in self.interactedAt:
			shrine = self.shrineInRange(1)
			if shrine:
				self.interactedAt[room] = True
				self.interactWithUnit(shrine)
		if self.unitLastPos[0] != self.unit.getPos()[0] or self.unitLastPos[1] != self.unit.getPos()[1]:
			if self.beingWorshipped:
				self.modFavour(self.PassiveWorshipAmount)
			else:
				self.modFavour(self.PassiveNoWorshipAmount)
			
		self.unitLastPos = self.unit.getPos()
				
	def interactWithUnit(self, shrine):
		if self.favour < self.FavourLevels[2]:
			self.unit.addDamage(self.unit.getMaxHealth() / 3.0, None, 0)
			PTRS["EFFECTS"].addEffect(Effects.SpellEffect("Ignite", self.unit.getPos(), self.unit.floor, 40, True, None, self.unit))
		elif self.favour > self.FavourLevels[-2]:
			self.unit.heal(self.unit.getMaxHealth() / 4.0, None)
			self.unit.addBuff(Buffs.StatBuff(None, self.unit, 200, {"moveSpeed": 1.2, "defense":20}))
			PTRS["EFFECTS"].addEffect(Effects.SpellEffect("Buffed", self.unit.getPos(), self.unit.floor, 40, True, None, self.unit))
		
	def hitTarget(self, target, amount):
		pass
		
	def takeDamage(self, amount, source, damageType):
		pass
		
	def worship(self):
		pass
		
	def isShrineSquare(self, gridPos):
		return gridPos in GetDungeonGrid(self.unit.floor).majorNodes and GetDungeonGrid(self.unit.floor).majorNodes[gridPos]["type"] == "shrine" and \
				GetDungeonGrid(self.unit.floor).majorNodes[gridPos]["god"] == self.ShrineName
		
	#Worshipping condition is: all units are dead, and they stand still near the shrine.
	def checkForWorshipping(self):
		gridPos = posToDungeonGrid(self.unit.getPos())
		room = GetDungeonGrid(self.unit.floor).getRoom(gridPos)
		if room not in self.worshippedAt and self.unit.currState == "idle" and \
					self.unit.getPos()[0] == self.worshipPos[0] and self.unit.getPos()[1] == self.worshipPos[1] and \
					self.isShrineSquare(gridPos):
			self.worshipTime += 1
			if self.worshipTime >= self.MaxWorshipTime:
				if room.allUnitsDead():
					self.worshipTime = 0
					self.worship()
					self.worshippedAt[room] = True
		else:
			self.worshipTime = 0
			self.worshipPos = self.unit.getPos()
		
	def shrineInRange(self, ran):
		dungeon = GetDungeonGrid(self.unit.floor)
		gridPos = posToDungeonGrid(self.unit.getPos())
		for x in range(-ran, ran + 1):
			for y in range(-ran, ran + 1):
				gPos = (gridPos[0] + x, gridPos[1] + y)
				if self.isShrineSquare(gPos) and dungeon.getRoom(gridPos) is dungeon.getRoom(gPos):
					return gPos
		return None
		
#Spheres: Life, Nature, Good
#Likes: Slimes, Animals
#Dislikes: Unnatural things. (Undead, Elementals)
#Gain favour by fighting undead / elementals, and by hanging around near flowers.
#Gain favour by withstanding animal attacks
#Lose favour by attacking animals and slimes.
#Lose favour by attacking when near flowers
class Nature(NoGod):
	ShrineName = "Nature"
	Image = [1, 0]
	DisplayName = "Kezra"
	def childInit(self):
		self.favour = 0
		self.unitLastCoord = [0, 0]
		self.flowerRepititions = 0
		self.maxFlowerRepititions = 20
		
	def getFavourColour(self):
		favourPct = self.getFavourPct()
		c = pygame.Color(0, 0, 0)
		c.hsva = [int(44 + (121 - 44) * favourPct), int(68 + 31 * favourPct), 78 + int(21 * favourPct)]
		return c
		
	def worship(self):
		self.modFavour(100)
		
	def moveTick(self):
		NoGod.moveTick(self)
		coord = posToCoords(self.unit.getPos())
		gridPos = posToDungeonGrid(self.unit.getPos())
		terrain = GetTerrain(self.unit.floor)
		#If they're standing in flowers, favour +!
		if terrain.getAtPos(self.unit.getPos(), 0) == "0":
			if self.flowerRepititions <= self.maxFlowerRepititions and (coord[0] != self.unitLastCoord[0] or coord[1] != self.unitLastCoord[1])\
						and terrain.getAtPos(self.unit.getPos(), 1) == 5:
				self.unitLastCoord = coord
				if self.unit.currState == "attack":
					self.modFavour(-2)
					self.flowerRepititions = max(self.flowerRepititions - 1, 0)
				else:
					self.modFavour(1 * (1 - self.flowerRepititions / float(self.maxFlowerRepititions)))
					self.flowerRepititions += 1
		else:
			self.flowerRepititions -= max(self.flowerRepititions - 0.1, 0)
			
	def hitTarget(self, target, amount):
		if target.getStat("unitType") in [enemyTypes.ANIMAL, enemyTypes.SLIME]:
			self.modFavour(-amount / float(50 * target.floor))
		elif target.getStat("unitType") in [enemyTypes.ELEMENTAL, enemyTypes.UNDEAD]:
			self.modFavour(amount / float(50 * target.floor))
		
	def takeDamage(self, amount, source, damageType):
		if not source:
			return
		if source.getStat("unitType") in [enemyTypes.ELEMENTAL, enemyTypes.UNDEAD]:
			self.modFavour(20 * amount / float(self.unit.getMaxHealth()))
		elif source.getStat("unitType") in [enemyTypes.ANIMAL, enemyTypes.SLIME] and\
					source not in self.unit.lastHitTargets:
			self.modFavour(10 * amount / float(self.unit.getMaxHealth()))
	
class Water(NoGod):
	ShrineName = "Water"
	DisplayName = "Triton"
	Image = [2, 0]
	def childInit(self):
		self.favour = 0
		self.unitLastCoord = [0, 0]
		self.flowerRepititions = 0
		self.maxFlowerRepititions = 20
		
	def getFavourColour(self):
		favourPct = self.getFavourPct()
		c = pygame.Color(0, 0, 0)
		c.hsva = [233, int(99 * favourPct), 73 + int(26 * favourPct)]
		return c
		
	def worship(self):
		self.modFavour(100)
		
#Fuck potions
class Death(NoGod):
	ShrineName = "Death"
	DisplayName = "Azuul"
	PassiveNoWorshipAmount = -0.02
	PassiveWorshipAmount = 0
	Image = [3, 0]
	FavourLevels = [-150, -50, 50, 150, 250, 350, 450]
	def childInit(self):
		self.favour = 0
		self.unitLastCoord = [0, 0]
		self.flowerRepititions = 0
		self.maxFlowerRepititions = 20
		
	def hitTarget(self, target, amount):
		if target.getStat("unitType") in [enemyTypes.HUMANOID, enemyTypes.ANIMAL]:
			self.modFavour(amount / float(30 * target.floor))
			
	def moveTick(self):
		NoGod.moveTick(self)
		
	def getFavourColour(self):
		favourPct = self.getFavourPct()
		c = pygame.Color(0, 0, 0)
		c.hsva = [304, int(76 * favourPct), 52 + int(20 * favourPct)]
		return c
		
	def worship(self):
		self.modFavour(100)