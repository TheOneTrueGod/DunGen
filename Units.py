import pygame, os, math, random, copy, pickle
import Code.Units.Equipment as Equipment, Code.Units.Stats as Stats, Code.Units.Projectiles as Projectiles, Code.Units.Abilities as Abilities, Code.Units.Guilds as Guilds, Code.Units.Gods as Gods, Code.Units.Buffs as Buffs
import Code.Engine.Terrain as Terrain, Code.Engine.Effects as Effects
from Globals import *
from pygame.locals import *
ENEMYFRAMES = 3
DAMAGEDISPLAYTIME = 180
#animationFrames = {"idle":[1, 1,
#													 "idle"],
#									 "walk":[0, 1, 2, 1,
#													 "walk"],
#									 "windup":[5, 6, 7,
#												"attack"],
#									 "attack":[5, 6, 7, 8, 9,"idle"],
#									 "stunned":[3, 3, 3, "idle"],
#									 "dead":[3,3,3,"dead"]}

stateTimes = {"walk":40, "idle":20, "windup":30, "attack":7, "stunned":30, "dead":5}
deadUnits = readAllLinesInFile(os.path.join("Profiles", "DeadPlayers.txt"))

def ReviveUnit(deadChar):
	u = pickle.load(open(os.path.join("Profiles", deadChar[0] + ".prof")))
	u.health = u.getMaxHealth()
	u.targetHealth = u.health
	u.currState = "idle"
	u.animationFrames = u.framesToUse["idle"]
	u.frame = 0
	u.saveToFile(os.path.join("Profiles", deadChar[0] + ".prof"))
	deadUnits.remove(deadChar)
	PTRS["UNITS"].saveDeadUnits()

def loadCharPic(pic):
	path = os.path.join("Data", "Pics", "Actors", pic + ".PNG")
	if "Enemies" in pic:
		frames = ENEMYFRAMES
	else:
		frames = 5
	if not os.path.exists(path):
		print "ERROR, file not found: '" + path + "'"
		if os.path.exists(os.path.join("Data", "Pics", "Actors", "NoChar.PNG")):
			return loadCharPic("NoChar")
		#CRASH HERE
	pic = pygame.image.load(path)
	#pic = pygame.transform.scale(pic, [int(pic.get_width() * 1.5), int(pic.get_height() * 1.5)])
	#pic.set_colorkey([255, 0, 255])
	width = pic.get_width() / frames
	toRet = []
	for x in xrange(frames):
		toRet += [[]]
		for y in xrange(pic.get_height() / width):
			toRet[x] += [pic.subsurface([x * width, y * width, width, width])]
	
	return toRet

def drawCharPic(surface, pic, pos, frame, angle):
	global CHARPICTURES
	if pic in CHARPICTURES:
		toDraw = pygame.transform.rotate(CHARPICTURES[pic][frame % 5][frame / 5], 180 - angle + 90)
		pos = [pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2]
		surface.blit(toDraw, pos)
	else:
		CHARPICTURES[pic] = loadCharPic(pic)
		drawCharPic(surface, pic, pos, frame, angle)
		
def drawEnemyPic(surface, pic, pos, frame, tintRed = False):
	global CHARPICTURES
	if pic in CHARPICTURES:
		toDraw = CHARPICTURES[pic][frame % ENEMYFRAMES][frame / ENEMYFRAMES]
		pos = [pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2]
		if tintRed:
			toDraw.fill([255, 0, 0], special_flags=BLEND_MULT)#BLEND_RGB_MULT)
		surface.blit(toDraw, pos)
	else:
		CHARPICTURES[pic] = loadCharPic(os.path.join("Enemies", pic))
		drawEnemyPic(surface, pic, pos, frame)
		
class UnitStruct:
	def __init__(self):
		self.enemyUnits = []
		self.alliedUnits = [None, None]#ImmobileUnit([400, 299], 1)]

		self.unitsDone = []
		
	def save(self):
		on = 0
		for u in self.getPlayers():
			if PLAYERFILES[on] and u:
				u.saveToFile(PLAYERFILES[on])
			on += 1
			GetDungeonGrid(u.floor).saveToFile()
		self.saveDeadUnits()
			
	def saveDeadUnits(self):
		fileOut = open(os.path.join("Profiles", "DeadPlayers.txt"), "w")
		found = [self.alliedUnits[0] == None]
		if NUMPLAYERS == 2:
			found += [self.alliedUnits[1] == None]
		for u in deadUnits:
			if os.path.exists(os.path.join("Profiles", u[0] + ".prof")):
				fileOut.write(" ".join(u) + "\n")
				#found = False
				on = 0
				for p in self.alliedUnits:
					if p and p.getName() == u[0]:
						found[on] = True
					on += 1
		for i in range(NUMPLAYERS):
			u = self.alliedUnits[i]
			if not found[i] and u and u.isDead():
				fileOut.write(u.getName() + " " + u.getPicture() + "\n")
		fileOut.close()
			
	def unitExited(self, unit):
		self.unitsDone += [unit]
		
	def readjustCamera(self, camera, unitId):
		if self.alliedUnits[unitId]:
			camera.setPos(intOf(self.alliedUnits[unitId].getPos()), self.alliedUnits[unitId].floor)
		
	def selectUnit(self, number, selectedBy):
		for a in self.getPlayers():
			if a.selected == selectedBy:
				a.selected = 0
		if self.alliedUnits[number]:
			self.alliedUnits[number].selected = selectedBy

	def startBattle(self, selected):
		for i in range(len(selected)):
			if self.alliedUnits[selected[i]]:
				self.alliedUnits[selected[i]].controlled = i + 1
				self.alliedUnits[selected[i]].controller = i + 1
				self.alliedUnits[selected[i]].selected = False
				self.alliedUnits[selected[i]].health = self.alliedUnits[selected[i]].getMaxHealth()
				self.alliedUnits[selected[i]].target = None
				self.alliedUnits[selected[i]].setState("idle")
				
	def clear(self):
		self.unitsDone = []
		
		while len(self.alliedUnits):
			del self.alliedUnits[0]
		while len(self.enemyUnits):
			del self.enemyUnits[0]
			
		self.alliedUnits = [None, None]

	def setUnits(self, units):
		self.alliedUnits = units
		
	def getNextUnit(self, player, curr, reverse = False):
		list = range(curr + 1, len(self.alliedUnits)) + range(0, curr)
		if reverse:
			list = reversed(list)
		for i in list:
			if self.alliedUnits[i].isSelectable(player + 1):
				return self.alliedUnits[i], i
		return None, None
		
	def getFinishedUnits(self):
		return self.unitsDone
		
	def update(self, cams):
		on = 0
		for unit in self.getPlayers():
			unit.update(cams[on])
			on += 1
		for unit in self.enemyUnits:
			unit.update(None)
			
		i = 0
		while i < len(self.enemyUnits):
			if self.enemyUnits[i].readyToSleep:
				del self.enemyUnits[i]
			else:
				i += 1
		"""i = 0
		while i < len(self.alliedUnits):
			if self.alliedUnits[i].readyToDelete():
				del self.alliedUnits[i]
			else:
				i += 1"""
	
	def getTargets(self, team, hitsAllies, hitsEnemies):
		unitList = []
		if (team == 1):
			if hitsAllies:
				unitList += [u for u in PTRS["UNITS"].getPlayers() if not u.isDead()]
			if hitsEnemies:
				unitList += [u for u in PTRS["UNITS"].getEnemyUnits() if not u.isDead()]
		else:
			if hitsEnemies:
				unitList += [u for u in PTRS["UNITS"].getPlayers() if not u.isDead()]
			if hitsAllies:
				unitList += [u for u in PTRS["UNITS"].getEnemyUnits() if not u.isDead()]
		return unitList
		
	def createEnemyUnit(self, pos, floor, room, type):
		e = EnemyUnit(pos, type, 1, floor, room)
		return e
		
	def addEnemyUnit(self, pos, floor, type):
		e = self.createEnemyUnit(pos, floor, type)
		if e != None:
			self.enemyUnits += [e]
		return e
		
	def wakeUpUnit(self, unit):
		self.enemyUnits += [unit]
			
	def addPlayerUnit(self, unit):
		self.alliedUnits += [unit]
			
	def getPlayers(self):
		return [u for u in self.alliedUnits if u != None]
		
	def getEnemyUnits(self):
		return self.enemyUnits
		
	def drawMe(self, camera, atStart):
		for unit in self.enemyUnits:
			unit.drawMe(camera, atStart)
		on = 1
		for unit in self.getPlayers():
			unit.drawMe(camera, False, camera.getNum() == on)
			on += 1
			
class RNG(object): #Random Number Generator
	def __init__(self):
		self.randSeed = random.random()
		self.backupSeed = self.randSeed
	
	def primeRNG(self):
		random.seed(self.randSeed)
		self.randSeed = random.random()
	
	def uniform(self, start, end):
		self.primeRNG()
		return random.uniform(start, end)
	
	def randint(self, start, end):
		self.primeRNG()
		return random.randint(start, end)
		
	def random(self):
		self.primeRNG()
		return random.random()
	
	def randChoice(self, list):
		self.primeRNG()
		return random.choice(list)
		
	def backup(self):
		#self.randSeed = random.random()
		self.backupSeed = self.randSeed
		#if self.team == 2:
		#	print "backup: ", self.backupSeed
		
	def restore(self, previousUnit):
		#if self.team == 2:
		#	print "restore: ", previousUnit.backupSeed
		self.randSeed = previousUnit.backupSeed
		#self.backupSeed = self.randSeed
	
class TargetDummy:
	def __init__(self, pos, floor):
		self.pos = pos
		self.floor = floor
		self.lastHit = 0
		self.readyToSleep = False
		self.size = 5
		
	def getKeyword(self, keyword):
		return 0
		
	def isTrainingDummy(self):
		return True
		
	def addDamage(self, amount, source, damageType, stunFactor = 0):
		pass
		
	def setPos(self, pos, floor):
		self.pos = pos
		self.floor = floor
		
	def getPos(self):
		return self.pos
		
	def isDead(self):
		return False
		
	def getHealth(self):
		return 1
		
	def getMaxHealth(self):
		return 1
		
	def isSpawned(self):
		return True
	
class Unit(RNG):
	framesToUse			 = {"idle":[1, 1,
													 "idle"],
									 "walk":[0, 1, 2, 1,
													 "walk"],
									 "windup":[5, "attack"],
									 "attack":[5, 6, 7, "idle"],
									 "attack2":[10, 11, 12,"idle"],
									 "stunned":[3, 3, 3, "idle"],
									 "dead":[3,3,3,"dead"]}
	def __init__(self, startPos, level, floor):
		super(Unit, self).__init__()
		self.floor = floor
		self.damageTime = 0
		self.pos = [startPos[0], startPos[1]]
		self.startPos = [startPos[0], startPos[1]]
		self.lastPos = [startPos[0], startPos[1]]
		self.speed = [0, 0]
		self.onGround = False
		self.level = level
		self.logicTickIn = 3
		self.angle = math.pi / 2.0 * 3
		self.angleFacing = self.angle
		self.frame = 0
		self.attackCooldown = 0
		self.currState = "idle"
		self.size = 10
		self.buffs = Buffs.BuffStruct(self)
		self.maxHealth = 2
		self.health = self.getMaxHealth()
		self.range = 5
		self.hitFrames = [0]
		self.attacked = False
		self.casting = False
		self.abilList = []
		self.attackCallback = None
		self.team = 2
		self.enabled = True
		self.picture = "Player1"
		self.frameRate = 1
		self.knockback = [0, 0]
		self.animationFrames = []
		self.setState(self.currState)
		self.stats = {}
		self.attackBonuses = {}
		self.rageTable = {}
		self.selected = False
		self.damageAngle = 0
		self.itemHeld = None
		self.readyToSleep = False
		self.abilCurrentlyUsing = None
		self.lastHit = 0
		self.stunFactor = 0
		self.stunTime = 0
		self.disabledCount = 0
		self.lastDamageAmount = 0
		
	def isTrainingDummy(self):
		return False
		
	def giveTreasure(self, treasureList):
		pass
		
	def addBuff(self, buff):
		self.buffs.addBuff(buff)
		
	def disable(self):
		self.disabledCount += 1
		self.enabled = False
		
	def enable(self):
		self.disabledCount = max(0, self.disabledCount - 1)
		if not self.disabledCount:
			self.enabled = True
		
	def addExperience(self, amount):
		pass
		
	def getResistance(self, resNum):
		return 0
		
	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat] 
		return Stats.baseStats[stat]
		
	def getStatMod(self, stat):
		bStat = self.buffs.getStatMod(stat)
		return bStat
		
	def getKeyword(self, keyword):
		toRet = 0
		if keyword in self.keywords:
			toRet = self.keywords[keyword]
		bKeyword = self.buffs.getKeyword(keyword)
		if bKeyword:
			toRet += (1 - toRet) * bKeyword
		return 0
		
	def sleep(self):
		self.readyToSleep = True
	
	def wakeUp(self):
		self.readyToSleep = False
		#self.pos = [self.startPos[0], self.startPos[1]]
		
	def backup(self):
		super(Unit, self).backup()
		self.itemHeldBackup = self.itemHeld
		
	def restore(self, previousUnit):
		super(Unit, self).restore(previousUnit)
		self.itemHeld = previousUnit.itemHeldBackup
		
	def getItemHeld(self):
		return self.itemHeld
		
	def isDead(self):
		return self.health <= 0
		
	def setAttackBonuses(self, bonusDict):
		for k in bonusDict:
			self.attackBonuses[k] = bonusDict[k]
		
	def setStats(self, statDict):
		for key in statDict:
			self.stats[key] = statDict[key]
			
	def getBounty(self):
		return self.getStat("bounty")
		
	def getListenRange(self, abil=None):
		return self.getBasicAttack().Range
		
	def getAbilRange(self):
		return self.getBasicAttack().Range

	def canSeeUnit(self, unit, abil=None):
		if self.floor == unit.floor and dist(unit.getPos(), self.getPos()) <= self.getListenRange(abil):
			for square in raytrace([int(self.getPos()[0] / TILESIZE[0]), int(self.getPos()[1] / TILESIZE[1])], 
							 [int(unit.getPos()[0] / TILESIZE[0]), int(unit.getPos()[1] / TILESIZE[1])]):
				if not GetTerrain(self.floor).canSeeThrough(intOf(square)):
					return False
			return True
		return False
			
	def getAttack(self, type):
		toRet = self.getStat("attack")
		if type in self.attackBonuses:
			toRet += self.attackBonuses[type]
		return toRet
		
	def addKnockback(self, knockback):
		self.knockback = knockback
						
	def hitTarget(self, target, amount):
		pass
			
	def addDamage(self, amount, source, damageType, stunFactor = 0):
		if source:
			self.damageAngle = math.atan2(source.getPos()[1] - self.getPos()[1], source.getPos()[0] - self.getPos()[0])
			self.lastHitBy = source
		if self.itemHeld == itemTypes.DEFEND:
			self.itemHeld = None
		else:
			res = self.getResistance(damageType)
			amount = amount * (1 - res)
			if not self.isDead():
				size = 1
				if res >= 0.5:
					size = 0
				elif res <= -0.5:
					size = 2
				PTRS["EFFECTS"].addEffect(Effects.DamageTextEffect(self.pos, self.floor, [255, 0, 0], 50, \
						str(int(self.health) - int(self.health - amount)), size))
			amount = min(amount, self.health)
			if source:
				source.addExperience(self.getStat("experience") * amount / float(self.getMaxHealth()))
			lastHealth = self.health
			self.health -= amount
			self.damageTime = DAMAGEDISPLAYTIME
			if self.lastHitBy != None and self.health <= 0 and lastHealth > 0:
				Equipment.awardBounty(self.lastHitBy, self)
			
			self.stunFactor += stunFactor * (1 - self.getStat("stunResistance")) * (1 - res)
			if self.stunFactor >= 1 and (self.currState != "attack" or (self.abilCurrentlyUsing and self.abilCurrentlyUsing.Interruptable or self.stunFactor > 3)):
				if amount and not self is PlayerUnit:
					if self.currState == "attack" and self.abilCurrentlyUsing:
						self.abilCurrentlyUsing.interrupt()
					self.setState("stunned", STUNTIME * int(self.stunFactor))
				self.stunFactor -= int(self.stunFactor)
			self.lastHit = 0
			return amount
		self.lastHit = 0
		return 0
			
	def getHealth(self):
		return self.health
		
	def getMaxHealth(self):
		return self.maxHealth
		
	def readyToDelete(self):
		return self.health <= 0
		
	def resetPosition(self):
		self.pos = [self.startPos[0], self.startPos[1]]
		self.speed = [0, 0]
		
	def update(self, camera):
		if self.isDead():
			if self.currState is not "dead":
				self.setState("dead")
			#return
		self.buffs.update()
		self.logicTickIn -= 1
		if self.logicTickIn <= 0:
			self.logicTick()
			self.logicTickIn = 3
		self.damageTime -= self.damageTime > 0
		
		if self.team == 1:
			self.move(camera)
		else:
			self.move()
		self.updateAbilities()
		self.lastHit += 1
		
	def getSelectedAbility(self):
		return None
			
	def updateAbilities(self):
		if not self.enabled:
			return
			
		for abil in self.abilList:
			if abil is not None:
				abil.update()
				
		if not self.getBasicAttack() == self.abilList[0]:
			self.getBasicAttack().update()

	def updateAnimation(self):
		self.frame += self.frameRate
		#print self.hitFrames
		if len(self.hitFrames) > 0 and self.frame >= self.hitFrames[0] and not self.attacked:
			del self.hitFrames[0]
			self.casting = False
			if len(self.hitFrames) <= 0:
				self.attacked = True
			self.abilCurrentlyUsing.useCallback(self)
		
	def move(self, advanceFrame = True):
		self.stunTime -= self.stunTime > 0
		self.lastPos = [self.pos[0], self.pos[1]]
		self.attackCooldown -= (self.attackCooldown > 0)
		
		if advanceFrame:
			self.updateAnimation()
			
		if (self.frame >= len(self.animationFrames) - 1):
			self.setState(self.animationFrames[len(self.animationFrames) - 1])
	
		speed = [self.knockback[0], self.knockback[1]]
		#if math.fabs(self.knockback[0]) == 0 and math.fabs(self.knockback[1]) == 0:
		if (self.currState is not "stunned") and not self.isDead() and self.enabled:
			speed[0] += self.speed[0]
			speed[1] += self.speed[1]
		speedMod = Terrain.getTerrainSpeedMods(self, GetTerrain(self.floor).getAtPos(self.pos, 0), GetTerrain(self.floor).getAtPos(self.pos, 1))
		speed = [speed[0] * speedMod, speed[1] * speedMod]

		if GetTerrain(self.floor).canMoveThrough(posToCoords([self.pos[0] + speed[0], self.pos[1]]), self):
			self.pos[0] += speed[0]
		else:
			if speed[0] > 0:
				self.pos[0] = int(self.pos[0] / 20 + 1) * 20 - 0.001
			else:
				self.pos[0] = int(self.pos[0] / 20) * 20 + 0.001
		if GetTerrain(self.floor).canMoveThrough(posToCoords([self.pos[0], self.pos[1] + speed[1]]), self):
			self.pos[1] += speed[1]
		else:
			if speed[1] > 0:
				self.pos[1] = int(self.pos[1] / 20 + 1) * 20 - 0.001
			else:
				self.pos[1] = int(self.pos[1] / 20) * 20 + 0.001
			
		if self.lastPos[0] != self.pos[0] or self.lastPos[1] != self.pos[1]:
			GetTerrain(self.floor).notifyUnitMovement(self, self.lastPos, self.pos)
			
		for i in [0, 1]:
			self.knockback[i] *= 0.90
			if math.fabs(self.knockback[i]) <= 0.5:
				self.knockback[i] = 0
			if math.fabs(self.knockback[i]) <= 1 and self.currState == "attack":
				self.knockback[i] = 0
				
		if self.currState == "walk" and self.lastPos[0] == self.pos[0] and self.lastPos[1] == self.pos[1]:
			self.setState("idle")
		elif self.currState == "idle" and (self.lastPos[0] != self.pos[0] or self.lastPos[1] != self.pos[1]):
			self.setState("walk")
			
		roomPos = posToDungeonGrid(self.pos)
		
	def logicTick(self):
		pass
		
	def isSpawned(self):
		return True
		
	def setState(self, stateName, duration=-1, animationFramesToUse = []):
		self.attacked = True
		self.casting = False
		if ("attack" in stateName):
			self.attacked = False
			self.currState = "attack"
			self.casting = True
			
		if animationFramesToUse == []:
			self.animationFrames = self.framesToUse[stateName]
		else:
			self.animationFrames = animationFramesToUse
		if (duration == -1):
			duration = stateTimes[stateName]
		if stateName == "stunned":
			self.stunTime = duration + self.stunTime
			duration = self.stunTime
		else:
			self.stunTime = 0
		self.currState = stateName
		self.frameRate = (len(self.animationFrames) - 1) / float(duration)
		self.frame = 0
		
	def attack(self, abil, overrideAttack = False):
		if self.currState == "idle" or self.currState == "walk" or self.currState == "attack" and overrideAttack and self.abilCurrentlyUsing.overrideValue < abil.overrideValue:
			abil.use(self)
			self.abilCurrentlyUsing = abil
		
	def getPos(self):
		return [self.pos[0], self.pos[1]]
	
	def drawMe(self, camera, atStart):
		if camera.floor != self.floor:
			return
		pos = intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()])
		size = int(self.size)
		if self.selected == 1:
			pygame.draw.circle(camera.getSurface(), [255, 0, 0], pos, size, 3)
		elif self.selected == 2:
			pygame.draw.circle(camera.getSurface(), [0, 0, 255], pos, size, 3)
		drawCharPic(camera.getSurface(), self.picture, pos, int(self.animationFrames[int(self.frame)]), int(self.angleFacing * 180 / math.pi))
		if self.itemHeld != None:
			Terrain.drawItem(camera, [self.pos[0], self.pos[1] - self.size], self.itemHeld)
	
class PlayerUnit(Unit):
	def __init__(self, name, floor):
		self.equipment = Equipment.Equipment(self)
		Unit.__init__(self, [0, 0], 1, floor)
		self.damageTime = 0
		self.frame = 0
		self.team = 1
		self.target = None
		self.name = name
		self.guilds = Guilds.GuildLevels(self)
		self.maxHealth = self.getStat("health")
		self.health = self.maxHealth
		self.picture = "Thief"
		self.abilList = [Abilities.BasicAttack(self)]
		self.abilSelected = 1
		self.controlled = False
		self.controller = 0
		self.spawned = False
		self.inPortal = False
		self.respawnTimer = 0
		self.targetHealth = self.health
		self.abilsKnown = []
		self.abilsSelected = []
		self.selectedAbil = 0
		self.lastHitTargets = []
		self.guilds.setStartingGuild()
		self.favour = Gods.FavourStruct(self)
		self.attackSide = 0
		
		self.targetDummy = TargetDummy(self.pos, self.floor)
		
	def setMaxHealth(self, amt):
		currPct = self.health / float(self.maxHealth)
		targPct = self.targetHealth / float(self.maxHealth)
		self.maxHealth = amt
		self.health = self.maxHealth * currPct
		self.targetHealth = targPct * self.maxHealth
		
	def teachAbil(self, abil):
		self.abilsKnown += [abil]
		
	def giveTreasure(self, treasureList):
		for treasureName in treasureList:
			if treasureName == None:
				PTRS["EFFECTS"].addEffect(Effects.ItemCollectEffect(["slots", [9, 0]], self, self.floor))
			elif "Cash" in treasureName:
				PTRS["EFFECTS"].addEffect(Effects.ItemCollectEffect(["slots", [8, 0]], self, self.floor))
				self.addCash(int(treasureName.strip("Cash")) * random.uniform(0.8, 1.2))
			else:
				treasure = self.equipment.giveNewItem(treasureName)
				if treasure:
					PTRS["EFFECTS"].addEffect(Effects.ItemCollectEffect(treasure.getImage(), self, self.floor))
				elif len(self.equipment.inventory) >= INVENTORYSLOTS:
					PTRS["EFFECTS"].addEffect(Effects.ItemCollectEffect(["slots", [9, 0]], self, self.floor))
		
	def addExperience(self, amount):
		self.guilds.addExperience(amount)
		
	def getSpellLevel(self, guilds):
		maxLvl = 0
		for guild in guilds:
			maxLvl = max(self.guilds.getLevel(guild), maxLvl)
		return maxLvl
		
	def getResistance(self, resNum):
		if 0 <= resNum < numDamageTypes:
			return self.equipment.getResistance(resNum)
		return self.equipment.getResistance(0)
		
	def getLearnedAbilities(self):
		return [Abilities.playerAbilDict[k] for k in self.abilsKnown]
		
	def unEquipAbil(self, slotNum):
		if 0 <= slotNum < len(self.abilsSelected):
			del self.abilsSelected[slotNum]
			
	def getLearnedAbil(self, slotNum):
		if 0 <= slotNum < len(self.abilsKnown):
			return Abilities.playerAbilDict[self.abilsKnown[slotNum]]
	
	def getEquippedAbil(self, slotNum):
		if 0 <= slotNum < len(self.abilsSelected):
			return self.abilsSelected[slotNum]
			
	def switchHands(self):
		self.equipment.switchHands()
		self.attackSide = self.equipment.currentHand#1 - self.attackSide
		
	def getHand(self):
		return self.attackSide
		
	def update(self, camera):
		self.target = self.targetDummy
		Unit.update(self, camera)
		keys = self.getKeysObject()
		self.targetDummy.setPos([camera.Left() + keys.getMousePos()[0], camera.Top() + keys.getMousePos()[1]], self.floor)
			
	def updateAbilities(self):
		Unit.updateAbilities(self)
		notComplete = False
		if self.getSelectedAbility() and not self.getSelectedAbility().cooldown[0] == 0:
			notComplete = True
		for abil in self.abilsSelected:
			abil.update()
		if notComplete and self.getSelectedAbility().cooldown[0] == 0:
			PTRS["EFFECTS"].addEffect(Effects.CooldownDoneEffect("SkillReady", self, 8))
			
	def hitTarget(self, target, amount):
		if target not in self.lastHitTargets:
			self.lastHitTargets += [target]
		self.favour.hitTarget(target, amount)
			
	def equipAbil(self, abil):
		if 0 <= abil < len(self.abilsKnown):
			if self.abilsKnown[abil] in Abilities.playerAbilDict:
				self.abilsSelected += [Abilities.playerAbilDict[self.abilsKnown[abil]](self)]
			else:
				print "ERROR: '" + abil + "' not in playerAbilDict"
		
	def getSelectedAbil(self, slotNum):
		if 0 <= slotNum < len(self.abilsSelected):
			return self.abilsSelected[slotNum]
		return None
		
	def getStat(self, stat):
		if stat in self.stats:
			eStat = self.equipment.getStat(stat)
			gStat = self.guilds.getStat(stat)
			bStat = self.buffs.getStat(stat)
			return self.stats[stat] + eStat + gStat + bStat
		else:
			self.stats[stat] = Stats.baseStats[stat]
		return self.getStat(stat)
		
	def getStatMod(self, stat):
		eStat = self.equipment.getStatMod(stat)
		bStat = self.buffs.getStatMod(stat)
		return eStat * bStat
		
	def getKeyword(self, keyword):
		eKeyword = self.equipment.getKeyword(keyword)
		bKeyword = self.buffs.getKeyword(keyword)
		toRet = 0
		if eKeyword:
			toRet += eKeyword
		if bKeyword:
			toRet += (1 - toRet) * bKeyword
		return toRet
		
	def getBasicAttack(self):
		return self.equipment.getAttack()
	
	def getListenRange(self, abil=None):
		if abil:
			return abil.Range
		return self.getBasicAttack().Range
		
	def getInventoryItem(self, itemSlot):
		return self.equipment.getInventoryItem(itemSlot)
		
	def equipItem(self, itemSlot):
		self.equipment.equipItem(itemSlot)
		
	def unequipItem(self, itemSlot):
		self.equipment.unequipItem(itemSlot)

	def getEquippedItem(self, itemSlot):
		return self.equipment.getEquippedItem(itemSlot)
	
	def getEquippedItems(self):
		return self.equipment.getEquippedItems()
		
	def setPicture(self, pic):
		self.picture = pic
		
	def getInventoryList(self):
		return self.equipment.getInventory()
		
	def getPicture(self):
		return self.picture
		
	def getName(self):
		return self.name
		
	def addCash(self, amount):
		self.equipment.addCash(amount)
		
	def saveToFile(self, path):
		pickle.dump(self, open(path, "wb"))
		
	def getTargetHealth(self):
		return self.targetHealth
		
	def isSpawned(self):
		return self.spawned
		
	def backup(self):
		super(PlayerUnit, self).backup()
		
	def addDamage(self, amount, source, damageType, stunFactor = 0):
		if not self.isDead() and not self.inPortal:
			res = self.getResistance(damageType)
			amount = amount * (1 - res)
			PTRS["EFFECTS"].addEffect(Effects.DamageTextEffect(self.pos, self.floor, [255, 0, 0], 50, \
					str(int(self.health) - int(self.health - amount))))
			self.favour.takeDamage(amount, source, damageType)
			self.lastDamageAmount += amount
			self.targetHealth -= amount
			self.lastHit = 0
			return amount
		return 0
		
	def heal(self, amount, source):
		amount = min(amount, self.maxHealth - self.health)
		self.health = min(self.health + amount, self.maxHealth)
		PTRS["EFFECTS"].addEffect(Effects.DamageTextEffect(self.pos, self.floor, [0, 255, 0], 50, \
					str(amount)))
		
	def setAbils(self, abils):
		self.abilList = [self.abilList[0]] + abils
		
	def isValidTarget(self, unit, abil):
		if unit:
			return not unit.isDead() and unit.isSpawned() and not unit.readyToSleep and unit.floor == self.floor
		return False
		
	def findClosestTarget(self):
		closest = -1
		targ = None
		for unit in PTRS["UNITS"].getEnemyUnits():
			d = dist(self.getPos(), unit.getPos())
			if not inSameRoom(self, unit):
				d += 10000
			if self.isValidTarget(unit, None) and (closest == -1 or d < closest):
				closest = d
				targ = unit
		return targ
		
	def findTargetForAbil(self):
		if self.target and self.isValidTarget(self.target, None):#and not self.target.isDead() and self.target.isSpawned() and dist(self.pos, self.target.pos) < abil.getRange() and self.canSeeUnit(self.target, abil):
			return self.target
		return self.findClosestTarget()
		
	def getNextTarget(self):
		if not self.target or not inSameRoom(self, self.target) or not isOnscreen(self.getPos(), self.target.getPos()):
			#self.target = None
			return self.findTargetForAbil()
		targs = PTRS["UNITS"].getEnemyUnits()
		if not targs:
			return
		first = None
		found = False
		return self.findClosestTarget()
		
		for u in targs:
			if not first:
				if self.isValidTarget(u, None) and inSameRoom(self, u) and isOnscreen(self.getPos(), u.getPos()):
					return u
					first = u
			if not found:
				if u == self.target:
					found = True
			else:
				if self.isValidTarget(u, None) and inSameRoom(self, u) and isOnscreen(self.getPos(), u.getPos()):
					return u
		return first
					
	def isSelectable(self, player):
		return not self.isDead() and not self.inPortal and self.selected in [player, 0]
				
	def getKeysObject(self):
		keys = PTRS["KEYS"]
		return keys
		
	def getSelectedAbility(self):
		if 0 <= self.selectedAbil < len(self.abilsSelected):
			return self.abilsSelected[self.selectedAbil]
		return None
		
	def findNextTargetForAbil(self, abil, direction):
		targ = self.target
		if not targ:
			return None
		closest = None
		dist = 0
		for u in PTRS["UNITS"].getEnemyUnits():
			for i in [0, 1]:
				if direction[i] != 0:
					if u != targ and \
							(u.getPos()[i] < targ.getPos()[i] and direction[i] < 0 or u.getPos()[i] > targ.getPos()[i] and direction[i] > 0) and \
							(closest == None or math.fabs(u.getPos()[i] - targ.getPos()[i]) < dist) and \
							self.isValidTarget(u, abil):
						closest = u
						dist = math.fabs(u.getPos()[1] - targ.getPos()[1])
					break
		if closest:
			pass
			#self.target = closest
		
	def move(self, camera):
		if camera and self.lastDamageAmount > 0:
			if self.targetHealth > 0 and self.targetHealth - self.lastDamageAmount <= 0:
				camera.shake(10, 50)
			else:
				camera.shake(3, 10)
			self.lastDamageAmount = 0
		self.health += (self.targetHealth - self.health) * DELTADAMAGERATE
		if math.fabs(self.health - self.targetHealth) <= 1:
			self.health = self.targetHealth
		
		if self.target and self.target.floor != self.floor:
			#self.target = None
			self.setState("idle")
		
		self.guilds.moveTick()
		self.favour.moveTick()
			
		on = 0
		while on < len(self.lastHitTargets):
			if self.target == self.lastHitTargets[on] and on != 0:
				last = self.lastHitTargets[on]
				del self.lastHitTargets[on]
				self.lastHitTargets = [last] + self.lastHitTargets
			elif self.lastHitTargets[on].lastHit > HITDISPLAYTIME or self.lastHitTargets[on].readyToSleep:
				del self.lastHitTargets[on]
			else:
				on += 1
				
		if self.target != None and self.target not in self.lastHitTargets:
			self.lastHitTargets = [self.target] + self.lastHitTargets
			
		if not (self.isDead() or self.inPortal) and self.enabled:
			if self.controlled:
				keys = PTRS["KEYS"]
				
			if keys != None:
				if not self.spawned and self.respawnTimer <= 0:
					if self.controller:#keys.keyPressed(getPlayerControls(self.controller, "ACTIVATE")):
						self.spawned = True
						self.pos = GetTerrain(self.floor).getSpawnPos()
					else:
						return
				elif self.respawnTimer > 0:
					self.pos = GetTerrain(self.floor).getSpawnPos()
					self.respawnTimer -= 1
					return
				self.speed[1] = 0
				self.speed[0] = 0
				
				if (self.currState in ["idle", "walk"]):
					speedMod = 1
				else:
					speedMod = self.abilCurrentlyUsing.getAttackingMoveSpeed()
				if 1 in keys.getMouseButtons():
					targ = self.targetDummy
					if targ:
						#self.target = targ
						self.moveState = "alerted"
						override = 1 in keys.getMouseButtonsDown()
						self.attack(self.getBasicAttack(), override)
					
				if keys.keyDown(getPlayerControls(self.controller, "SPECIALSWITCH")) and len(self.abilsSelected):
					self.selectedAbil = (self.selectedAbil + 1) % len(self.abilsSelected)
				
				if 3 in keys.getMouseButtons() and self.getSelectedAbility() and self.getSelectedAbility().isUsable(self): #keys.keyPressed(getPlayerControls(self.controller, "SPECIALATTACK"))
					self.attack(self.getSelectedAbility(), True)
					
				if not (self.abilCurrentlyUsing and self.casting and self.abilCurrentlyUsing.NeedsCasting):
					if keys.keyPressed(getPlayerControls(self.controller, "UP")):
						self.speed[1] += -self.getMaxSpeed() * speedMod
					if keys.keyPressed(getPlayerControls(self.controller, "DOWN")):
						self.speed[1] += self.getMaxSpeed() * speedMod
				
					if keys.keyPressed(getPlayerControls(self.controller, "LEFT")):
						self.speed[0] += -self.getMaxSpeed() * speedMod
					if keys.keyPressed(getPlayerControls(self.controller, "RIGHT")):
						self.speed[0] += self.getMaxSpeed() * speedMod
					
			if self.currState == "attack" and self.target:
				self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
			elif self.speed[1] != 0 or self.speed[0] != 0:
				self.angle = math.atan2(self.speed[1], self.speed[0])
				
			if GetTerrain(self.floor).getAtPos(self.pos) == 9:
				GetDungeonGrid(self.floor).streamPiece(posToDungeonGrid(self.getPos()))
				
		advanceFrame = True
				
		Unit.move(self, advanceFrame)
		if self.enabled:
			self.angleFacing = self.angle
		
	def getMaxSpeed(self):
		toRet = max(min(Stats.baseStats["moveSpeed"] * self.getStatMod("moveSpeed"), MAXRUNSPEED), MINRUNSPEED)
		return toRet
		
	def drawMe(self, camera, atStart, myCamera = False):
		if camera.floor != self.floor or self.inPortal:
			return
				
		if not atStart and self.controlled:
			if self.respawnTimer > 1:
				pct = self.respawnTimer / float(RESPAWNTIME)
				pygame.draw.circle(camera.getSurface(), [255, 255, 0], 
					intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()]), 
					int(50 * pct), 1)
						
		if myCamera and self.target and not (self.target.isDead() or self.target.readyToSleep) and DRAWTARGETTINGCIRCLE:
			p = intOf([self.target.getPos()[0] - camera.Left(), self.target.getPos()[1] - camera.Top()])
			if self.getSelectedAbility() and dist(self.target.getPos(), self.getPos()) <= self.getSelectedAbility().getRange():
				pygame.draw.circle(camera.getSurface(), [0, 255, 0], p, int(self.target.size + 5), 2)
			else:
				pygame.draw.circle(camera.getSurface(), [255, 0, 0], p, int(self.target.size + 5), 1)
		
		if self.spawned:
			Unit.drawMe(self, camera, atStart)
		elif atStart:
			spawnP = GetTerrain(self.floor).getSpawnPos()
			offsetMap = [[-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0]]
			self.pos = [spawnP[0] + offsetMap[atStart % len(offsetMap)][0] * 20, spawnP[1] + offsetMap[atStart % len(offsetMap)][1] * 20]
			Unit.drawMe(self, camera, atStart)

class EnemyUnit(Unit):
	framesToUse		 = {"idle":[1, 1,
													 "idle"],
									 "walk":[0, 1, 2, 1,
													 "walk"],
									 "windup":[2, 2,
												"attack"],
									 "attack":[3, 4, 5, "idle"],
									 "stunned":[7, 7, "idle"],
									 "dead":[6, 6,"dead"]}
	def __init__(self, startPos, type, level, floor, room):
		self.enemyType = type
		self.lastHitBy = None
		Unit.__init__(self, startPos, level, floor)
		self.maxHealth = self.getStat("health")
		self.health = self.getMaxHealth()
		self.room = room
		self.frame = 0
		self.target = None
		for abil in self.getStat("ability"):
			self.abilList += [abil[0](self, abil[1])]
		self.nextDistanceCheck = 0
		self.team = 2
		self.picture = self.getStat("picture")
		self.offset = 0
		self.patrolDest = [self.pos[0] / TILESIZE[0], self.pos[1] / TILESIZE[1]]
		self.scanTime = 1
		self.scanDeltaTime = 1
		self.scanDeltaAng = 0
		self.scanType = "Passive"
		self.scanAngle = 0
		self.angleFacing = self.angle
		self.moveState = "patrol"
		self.alerted = 0
		self.reachedTarget = False
		self.deathInvestigated = False
		self.moveTarget = None
		self.attackMoveTarget = None
		self.attackMoveOffset = [0, 0]
		self.walkList = []
		self.investigateAngle = 0
		self.itemHeld = 0
		self.damageTime = 0
		self.sameAttackTime = [70, 70] #How long the unit will move towards/stand around a single spot attacking you for.
		
	def getResistance(self, resNum):
		if 0 <= resNum < numDamageTypes:
			return self.getStat("resistances")[resNum]
		return self.getStat("resistances")[0]
	
	def getStat(self, stat):
		if stat in self.stats:
			bStat = self.buffs.getStat(stat)
			if type(self.stats[stat]) == type(bStat):
				return self.stats[stat] + bStat
			return self.stats[stat]
		if self.floor in Stats.enemyStats and self.enemyType in Stats.enemyStats[self.floor] and stat in Stats.enemyStats[self.floor][self.enemyType]:
			s = Stats.enemyStats[self.floor][self.enemyType][stat]
		else:
			print "ERROR:  COULD NOT FIND STAT '" + str(stat) + "' FOR UNIT TYPE '" + self.enemyType + "'"
			s = Stats.baseEnemyStats[stat]
		self.stats[stat] = s
		return self.getStat(stat)
		
	def getKeyword(self, keyword):
		bKeyword = self.buffs.getKeyword(keyword)
		toRet = 0
		if keyword in self.getStat("keywords"):
			toRet = self.getStat("keywords")[keyword]
		if bKeyword:
			toRet += (1 - toRet) * bKeyword
		return 0
		
	def getListenRange(self, abil=None):
		if self.alerted:
			return self.getStat("alertedListenRad")
		return self.getStat("listenRad")
	
	def pickTarget(self):
		self.nextDistanceCheck = 10
		highPri = 1
		closest = None
		for unit in PTRS["UNITS"].getTargets(self.team, False, True):
			dMod = max(2000 - dist(unit.pos, self.pos), 0) / 2000.0 #1 at close range, 0 at 500 or more
			pri = 0
			if unit.health > 0 and self.canSeeUnit(unit):
				pri = 50 + dMod
				
			#if unit in self.rageTable:
			#	pri += self.rageTable[unit] / (self.getMaxHealth() * 5.0) #0 to 2 (assuming rageMult of 10)
			#pri += d
			#pri += self.uniform(0, 0.1)

			if (closest == None or pri > highPri) and pri > 0:
				closest = unit
				highPri = pri
		if closest != None:
			self.target = closest
			self.moveState = "alerted"
			
	def activateConditionCheck(self):
		if dist(self.pos, self.target.getPos()) <= self.getStat("activateRange"):
			#targAng = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0]) % (math.pi * 2)
			#selfAng = self.angleFacing % (math.pi * 2)
			#angDiff = getAngDiff(selfAng, targAng)
			return True
		return False
		
	def getMoveSpeed(self):
		return float(self.getStat("walkSpeed"))

	def updateAngleFacing(self):
		targAng = self.angle % (math.pi * 2)
		selfAng = self.angleFacing % (math.pi * 2)
		angDiff = getAngDiff(selfAng, targAng)
		
		if self.alerted:
			rotationSpeed = math.pi / 32.0
		elif math.fabs(angDiff) > math.pi / 3.0:
			rotationSpeed = math.pi / 32.0
		else:
			rotationSpeed = math.pi / 64.0
			
		if math.fabs(angDiff) < rotationSpeed:
			self.angleFacing = targAng
		else:
			self.angleFacing = (self.angleFacing + max(min(angDiff, rotationSpeed), -rotationSpeed)) % (math.pi * 2)

	def getScanAngle(self):
		return random.uniform(0, math.pi * 2)
			
	def scanMove(self):
		self.moveState == "scan"
		self.speed = [0, 0]
		if self.scanTime <= 0:#When we just reached the spot
			self.scanTime = DEFAULTSCANTIME
			self.scanAngle = self.angle
			self.startAng = self.angle
			self.targAng = self.angle
			self.scanDeltaTime = 1
			self.scanDeltaAng = 0
			
		self.scanTime -= self.scanTime > 0
		if self.alerted:
			self.scanTime -= self.scanTime > 0
		
		#While we're still scanning
		self.scanDeltaTime -= 1
		#self.angle += self.scanDeltaAng
		if self.scanDeltaTime <= 0:
			self.startAng = self.angle
			if self.scanType == "Stop":
				self.scanDeltaTime = self.randint(10, 15)
				self.targAng = self.angle
				self.scanType = "Passive"
			elif self.scanType == "Passive":
				if not self.alerted:
					self.scanType = "Stop"
					self.scanDeltaTime = self.randint(30, 40)
					self.targAng = self.getScanAngle() + math.pi / 4 * (self.random() - 0.5)
				else:
					self.scanDeltaTime = self.randint(20, 25)
					self.targAng = self.getScanAngle() + math.pi / 2 * (self.random() - 0.5)
			elif self.scanType == "Active":
				self.scanDeltaTime = self.randint(20, 25)
				self.targAng = self.getScanAngle() + math.pi / 2 * (self.random() - 0.5)
			self.angle = self.targAng
			#self.scanDeltaAng = (self.targAng - self.angle) / (self.scanDeltaTime)
		
		if self.scanTime <= 0:#When the counter has run down.
			self.moveState = "patrol"
			self.patrolDest = GetDungeonGrid(self.floor).getRandomPositionInRoom(self.pos)
			self.patrolDest = [self.patrolDest[0] / TILESIZE[0], self.patrolDest[1] / TILESIZE[1]]
		
	def patrolMove(self):
		moveDest = (self.patrolDest[0] * TILESIZE[0] + TILESIZE[0] / 2, 
								self.patrolDest[1] * TILESIZE[1] + TILESIZE[1] / 2)
		if (math.fabs(self.pos[0] - moveDest[0]) <= TILESIZE[0] / 2 and
				math.fabs(self.pos[1] - moveDest[1]) <= TILESIZE[1] / 2 ):
			self.moveState = "scan"
			self.patrolDest = GetDungeonGrid(self.floor).getRandomPositionInRoom(self.pos)
		else:
			self.moveTowardsTile(self.patrolDest)
		
	def alertedMove(self):
		if (self.target != None):
			self.angle = math.atan2(self.target.pos[1] - self.pos[1], self.target.pos[0] - self.pos[0])
		else:
			pass
			
	def moveTowards(self, pos, ignoreAngle = False, speedMod = 1):
		sp = self.getMoveSpeed() * speedMod * self.getStatMod("moveSpeed")
		if not ignoreAngle:
			targAng = self.angle % (math.pi * 2)
			selfAng = self.angleFacing % (math.pi * 2)
			angDiff = getAngDiff(selfAng, targAng)
			moveAng = math.pi / 3.0
			if math.fabs(angDiff) > moveAng:
				sp *= 0.3
		d = dist(self.pos, pos)
		ang = math.atan2(pos[1] - self.pos[1], pos[0] - self.pos[0])
		if d < sp:
			self.speed = [math.cos(ang) * d, math.sin(ang) * d]
		else:
			self.speed = [math.cos(ang) * sp, math.sin(ang) * sp]
			self.angle = ang
		
	def moveTowardsTile(self, coords, speedMod=1):
		oldMode = False
		
		if not oldMode:
			selfPos = intOf([self.pos[0] / TILESIZE[0], self.pos[1] / TILESIZE[1]])
			
			if self.moveTarget != (int(coords[0]), int(coords[1])):
				self.moveTarget = (int(coords[0]), int(coords[1]))
				self.walkList = GetTerrain(self.floor).getShortestPath(selfPos, self.moveTarget, 0, self, self.alerted)
			elif (not self.walkList):
				pass
				#print "This is the case"
			elif self.moveTarget == (int(coords[0]), int(coords[1])):
				checkDist = 1
				if len(self.walkList) > 1:
					checkDist = self.getMoveSpeed()
				moveTarg = (self.walkList[len(self.walkList) - 1][0] * TILESIZE[0] + TILESIZE[0] / 2, 
										self.walkList[len(self.walkList) - 1][1] * TILESIZE[1] + TILESIZE[1] / 2)
				if math.fabs(moveTarg[0] - self.pos[0]) <= checkDist and math.fabs(moveTarg[1] - self.pos[1]) <= checkDist:
					del self.walkList[len(self.walkList) - 1]
				if self.walkList:
					self.moveTowards(moveTarg, speedMod=speedMod)
		else:
			pos = [int(coords[0]) * TILESIZE[0] + TILESIZE[0] / 2, int(coords[1]) * TILESIZE[1] + TILESIZE[1] / 2]
			self.moveTowards(pos, speedMod=speedMod)
		
	def moveTowardsTarget(self, unit, speedMod = 1):
		if self.sameAttackTime[0] >= self.sameAttackTime[1]:
			a = random.uniform(0, math.pi * 2)
			d = random.uniform(self.getStat("chargeDist") / 2.0, self.getStat("chargeDist"))
			self.attackMoveOffset = [math.cos(a) * d, math.sin(a) * d]
			self.sameAttackTime[0] = 0
		self.sameAttackTime[0] += 1
		targ = (unit.getPos()[0] + self.attackMoveOffset[0], unit.getPos()[1] + self.attackMoveOffset[1])
		if dist(self.pos, targ) > TILESIZE[0]:#self.getMoveSpeed() * 4:
			self.moveTowards(targ, speedMod = speedMod)
			
	def InvestigateMove(self):	
		if not self.reachedTarget:
			self.moveTowardsTile(self.investigateTile)
			if math.fabs(self.pos[0] / TILESIZE[0] - self.investigateTile[0]) + math.fabs(self.pos[1] / TILESIZE[1] - self.investigateTile[1]) < 1:
				self.reachedTarget = True
				self.angle = self.uniform(0, math.pi * 2)
				self.scanTime = 106
				self.speed = [0, 0]
		else:
			self.scanTime -= 1
			if self.scanTime % 15 == 0:
				if self.investigateAngle:
					self.angle = self.investigateAngle + self.uniform(-math.pi / 3, math.pi / 3)
				else:
					self.angle = self.uniform(0, math.pi * 2)
			if self.scanTime <= 0:
				self.moveState = "patrol"
			return
				
	def move(self):
		Unit.move(self)
		if not self.isDead():
			if self.moveState == "patrol":
				self.patrolMove()
			elif self.moveState == "alerted":
				self.alertedMove()
			elif self.moveState == "scan":
				self.scanMove()
			self.updateAngleFacing()
		#if GetDungeonGrid(self.floor).getRoom(posToDungeonGrid(self.pos)) != None != self.room:
			#if self in self.room.getUnits():
			#	self.room.units.remove(self)
			#	self.room = GetDungeonGrid(self.floor).getRoom(posToDungeonGrid(self.pos))
		
	def getBasicAttack(self):
		return self.abilList[0]
			
	def logicTick(self):
		if self.isDead():
			return
		if self.target != None and (self.target.health <= 0 or not self.canSeeUnit(self.target) or \
				GetDungeonGrid(self.floor).getRoom(posToDungeonGrid(self.pos)) != GetDungeonGrid(self.floor).getRoom(posToDungeonGrid(self.target.getPos()))):
			self.moveState = "patrol"
			self.target = None
			self.attackMoveTarget = None
		self.nextDistanceCheck -= self.nextDistanceCheck > 0

		if (self.target == None or self.nextDistanceCheck <= 0):
			self.pickTarget()
		
		if (self.target != None):
			self.alerted = max(self.alerted, 100)
			abil = None
			for a in self.abilList:
				if abil == None or a.cooldown[0] <= abil.cooldown[0] or (a.UsePriority > abil.UsePriority and a.cooldown[0] <= abil.cooldown[0]):
					abil = a
			if self.currState == "attack" or self.currState == "windup" or abil != None and dist(self.pos, self.target.getPos()) <= abil.getRange():
				self.speed = [0, 0]
				self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
				#self.angleFacing = self.angle
				if self.currState not in ["windup", "dead"] and len(self.abilList) > 0 and self.activateConditionCheck():
					self.attack(abil)
				self.moveTowardsTarget(self.target, 0.5)
			else:
				self.moveTowardsTarget(self.target)
				#self.speed = [math.cos(self.angle) * self.getMoveSpeed(), math.sin(self.angle) * self.getMoveSpeed()]
				
		self.alerted -= self.alerted > 0
		for unit in PTRS["UNITS"].getEnemyUnits():
			if not unit.isDead() and ((self.alerted or unit.alerted) and not (self.alerted and unit.alerted)) and self.canSeeUnit(unit):
				unit.alerted = max(self.alerted, unit.alerted)
				self.alerted = max(self.alerted, unit.alerted)
			
	def drawMe(self, camera, atStart):
		if camera.floor != self.floor:
			return
		pos = intOf([self.pos[0] - camera.Left(), self.pos[1] - camera.Top()])
		size = int(self.size)
		tintRed = False
		if self.currState == "stunned" and self.frame < 1 / 2.0:
			tintRed = True
		drawEnemyPic(camera.getSurface(), self.picture, pos, int(self.animationFrames[int(self.frame)]), tintRed = tintRed)
		
		if PTRS["DRAWDEBUG"]:
			if not self.isDead():
				pygame.draw.circle(camera.getSurface(), [155, 0, 0], pos, int(self.getListenRange()), 1)
			for p in self.walkList:
				pygame.draw.circle(camera.getSurface(), [0, 0, 255], [p[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), 
																															p[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()], 5, 3)

def drawUnit(surface, unitStr):
	s = unitStr.split("|")
	pos = [int(s[1]), int(s[2])]
	size = int(s[5])
	healthPct = int(s[6])
	pygame.draw.circle(surface, [255, 0, 0], pos, size, 1)
	pygame.draw.line(surface, [255, 0, 0], [pos[0] - size, pos[1] - size - 2], [pos[0] - size + int(size * 2 * healthPct / 100.0), pos[1] - size - 2])
	drawCharPic(surface, s[0], pos, int(s[4]), int(s[3]))
	
playerUnitMap = {"SWORDSMAN":PlayerUnit}
PTRS["UNITS"] = UnitStruct()

PTRS["ENEMYTYPES"] = [None, "ARCHER", "CIVILIAN"]