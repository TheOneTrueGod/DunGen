import pygame, sys, Code.Engine.Effects as Effects, random
from Globals import *
PTRS["TRAPTYPES"] = enum('POWEREDDOOR', 'SECRETDOOR', 'WALLSPIKETRAP', 'FLOORSPIKETRAP', 'REPEATER', 'TREASURE', 'STREAMINGDOOR', 'DEFAULT', 'STAIRS', 'SHRINE')
NumTrapTypes = 8 - 2
lockPics = pygame.image.load(os.path.join("Data", "Pics", "Icons", "DoorLocks.png"))
lockPics.set_colorkey([255, 0, 255])
Directions = enum('UP', 'DOWN')
class Trap:
	TrapId = PTRS["TRAPTYPES"].DEFAULT
	def __init__(self, source, floor, args=[]):
		self.source = source
		self.floor = floor
		self.activated = 0
		self.backupActivated = 0
		self.parseArgs(args)
		self.readyToSleep = False
		self.wasDetected = False
		self.layer = 0
		
	def sleep(self):
		self.readyToSleep = True
		
	def wakeUp(self):
		self.readyToSleep = False
		
	def parseArgs(self, args):
		pass
		
	@staticmethod
	def previewTrap(self):
		return None
		
	def getPathingHeuristic(self, unit):
		return 0
		
	def addNumberParameter(self, number):
		pass
		
	def addAngleParameter(self, angle):
		pass
		
	def triggersTraps(self):
		return False
	
	def backup(self):
		self.backupActivated = self.activated
		
	def restore(self):
		self.activated = self.backupActivated
				
	def canMoveThrough(self, unit):
		return False
		
	def canSeeThrough(self):
		return False

	def activate(self, unit):
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		
	def save(self, fileOut):
		fileOut.write("TRAP " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " " + str(self.TrapId) + " ")
		self.saveParameters(fileOut)
		fileOut.write(" " + "\n")
		
	def saveParameters(self, fileOut):
		pass
		
	def update(self):
		pass
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		if self.activated:
			pygame.draw.rect(camera.getSurface(), [255, 255, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																														 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE])
		else:
			pygame.draw.rect(camera.getSurface(), [255, 0, 255], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																														 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE])
			
class PoweredDoor(Trap):
	TrapId = PTRS["TRAPTYPES"].POWEREDDOOR
	def parseArgs(self, args):
		self.locked = False
		self.unitHasKey = 0
		self.backupUnitHasKey = 0
		self.key = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-k":
					self.key = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Powered Door Error:", sys.exc_info()[0]
			
	def getPathingHeuristic(self, unit):
		if unit.getItemHeld() == self.key or unit.getItemHeld() == -1:
			return 0
		if self.activated:
			return 0
		else:
			return 10000
			
	def update(self):
		self.unitHasKey -= self.unitHasKey > 0
		
	def saveParameters(self, fileOut):
		fileOut.write("-k " + str(self.key))
		
	def getVariation(self):
		variation = 0
		if (not GetTerrain(self.floor).canMoveThrough((self.source[0], self.source[1] + 1)) or
				not GetTerrain(self.floor).canMoveThrough((self.source[0], self.source[1] - 1))):
			variation = 1
		return variation
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		variation = self.getVariation()
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Code.Engine.Terrain import getTileSubsurface
		if self.activated or self.unitHasKey:
			if PTRS["EDITORMODE"]:
				pic = getTileSubsurface("Traps", 1, 0)
			else:
				pic = getTileSubsurface("Traps", 0, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 1 + variation)
		camera.getSurface().blit(pic, pos)
		if self.key != 0 and (PTRS["EDITORMODE"] or not self.activated and not self.unitHasKey):
			pos = [pos[0] + TILESIZE[0] / 2 - lockPics.get_width() / 2, 
						 pos[1] + TILESIZE[1] /2 - lockPics.get_width() / 2]
			pic = lockPics.subsurface(((0, (self.key - 1) * lockPics.get_width()), (lockPics.get_width(), lockPics.get_width())))
			camera.getSurface().blit(pic, pos)
		
	def activate(self, unit):
		GetTerrain(self.floor).updateTrapTrigger(self.source, True)
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		GetTerrain(self.floor).updateTrapTrigger(self.source, False)
		
	def canMoveThrough(self, unit):
		if unit and (unit.getItemHeld() == self.key or unit.getItemHeld() == -1):
			p = posToCoords(unit.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				self.unitHasKey = 30
			return True
		return self.activated or self.unitHasKey
		
	def canSeeThrough(self):
		return self.activated or self.unitHasKey
		
	def backup(self):
		Trap.backup(self)
		self.backupUnitHasKey = self.unitHasKey
		
	def restore(self):
		Trap.restore(self)
		self.unitHasKey = self.backupUnitHasKey
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 1, 0)
		
	def addNumberParameter(self, number):
		if 0 <= number < 5:
			PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], self.floor, 
																											[255] * 3, 30, str(number)))
			self.key = number

class StreamingDoor(PoweredDoor):
	TrapId = PTRS["TRAPTYPES"].STREAMINGDOOR
	def getVariation(self):
		variation = 0
		if (GetTerrain(self.floor).getAtCoord((self.source[0], self.source[1] + 1)) == 1 or
				GetTerrain(self.floor).getAtCoord((self.source[0], self.source[1] - 1)) == 1):
			variation = 1
		return variation
		
	def lock(self):
		self.locked = True
		
	def unlock(self):
		self.locked = False
		
	def checkForStreaming(self):
		dunGrid = GetDungeonGrid(self.floor)
		if self.getVariation() == 0: # Up / Down
			p = ((self.source[0]) / (DUNGEONBOXSIZE[0] + 1), (self.source[1] + 1) / (DUNGEONBOXSIZE[1] + 1))
			leftP = ((self.source[0]) / (DUNGEONBOXSIZE[0] + 1), (self.source[1] - 1) / (DUNGEONBOXSIZE[1] + 1))
			if dunGrid.getGrid(p) == 1 or GetTerrain(self.floor).getAtCoord([self.source[0], self.source[1] + 1]) == 9:
				dunGrid.streamPiece(p, isRoom=(not dunGrid.getRoom(leftP).isRoom))
			else:
				if dunGrid.getGrid(leftP) == 1 or GetTerrain(self.floor).getAtCoord([self.source[0], self.source[1] - 1]) == 9:
					dunGrid.streamPiece(leftP, isRoom=(not dunGrid.getRoom(p).isRoom))
		else: # Left / Right
			p = ((self.source[0] + 1) / (DUNGEONBOXSIZE[0] + 1), (self.source[1]) / (DUNGEONBOXSIZE[1] + 1))
			bottomP = ((self.source[0] - 1) / (DUNGEONBOXSIZE[0] + 1), (self.source[1]) / (DUNGEONBOXSIZE[1] + 1))
			if dunGrid.getGrid(p) == 1 or GetTerrain(self.floor).getAtCoord([self.source[0] + 1, self.source[1]]) == 9:
				dunGrid.streamPiece(p, isRoom=(not dunGrid.getRoom(bottomP).isRoom))
			else:
				if dunGrid.getGrid(bottomP) == 1 or GetTerrain(self.floor).getAtCoord([self.source[0] - 1, self.source[1]]) == 9:
					dunGrid.streamPiece(bottomP, isRoom=(not dunGrid.getRoom(p).isRoom))
					
	def wakeUpRooms(self):
		dunGrid = GetDungeonGrid(self.floor)
		if self.getVariation() == 0: # Up / Down
			for i in [-1, 1]:
				p = coordsToDungeonGrid((self.source[0], self.source[1] + i))
				if dunGrid.getGrid(p) != 1:
					dunGrid.wakeUpRoom(p)
		else: # Left / Right
			for i in [-1, 1]:
				p = coordsToDungeonGrid((self.source[0] - i, self.source[1]))
				if dunGrid.getGrid(p) != 1:
					dunGrid.wakeUpRoom(p)
					
	def update(self):
		self.unitHasKey -= self.unitHasKey > 0
	
	def canMoveThrough(self, unit):
		if unit and unit.team == 1 and unit.floor == self.floor and not self.locked:
			p = posToCoords(unit.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				if not self.unitHasKey:
					self.checkForStreaming()
				self.wakeUpRooms()
				self.unitHasKey = DOORHOLDTIME
			return True
		return False#self.activated or self.unitHasKey
		
class Stairs(Trap):
	def parseArgs(self, args):
		self.direction = args[0]
		self.timer = 0
		self.maxTime = 50
		self.activated = False
		
	def update(self):
		if not self.activated and self.timer < self.maxTime:
			self.timer = max(self.timer - 1, 0)
		self.activated = False
		
	def canMoveThrough(self, unit):
		if unit and unit.team == 1:
			p = posToCoords(unit.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				self.timer = min(self.timer + 1, self.maxTime)
				if self.timer >= self.maxTime:
					dunGrid = GetDungeonGrid(unit.floor)
					dunGrid.saveToFile()
					unit.floor += 1
					#p = posToDungeonGrid(unit.pos)
					#if dunGrid.getGrid(p) == 1:
					#	dunGrid.streamPiece(p)
				self.activated = True
		return True
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Code.Engine.Terrain import getTileSubsurface
		if self.direction == Directions.UP:
			pic = getTileSubsurface("Traps", 7, 0)
		else:
			pic = getTileSubsurface("Traps", 8, 0)
		camera.getSurface().blit(pic, pos)
		if 0 < self.timer <= self.maxTime:
			pygame.draw.rect(camera.getSurface(), [255, 255, 0], [pos, [max(int(TILESIZE[0] * self.timer / float(self.maxTime)), 1), 4]])
			pygame.draw.rect(camera.getSurface(), [255] * 3, [pos, [TILESIZE[0], 4]], 1)
			
class SecretDoor(Trap):
	TrapId = PTRS["TRAPTYPES"].SECRETDOOR
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		variation = 0
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Code.Engine.Terrain import getTileSubsurface, tilesetLookup
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif not self.activated:
			tileset = tilesetLookup(GetTerrain(self.floor).getAtCoord((self.source[0], self.source[1]), 0))
			pic = getTileSubsurface(tileset, 1, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 0)
		camera.getSurface().blit(pic, pos)
		
	def getPathingHeuristic(self, unit):
		return 0
		
	def activate(self, unit):
		GetTerrain(self.floor).updateTrapTrigger(self.source, True)
		self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		GetTerrain(self.floor).updateTrapTrigger(self.source, False)
		
	def canMoveThrough(self, unit):
		return self.activated
		
	def canSeeThrough(self):
		return self.activated
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface, tilesetLookup
		return getTileSubsurface("Traps", 6, 0)
		
class WallSpikeTrap(Trap):
	TrapId = PTRS["TRAPTYPES"].WALLSPIKETRAP
	DamageType = damageTypes.PIERCE
	def parseArgs(self, args):
		self.timer = 0
		
	def getPathingHeuristic(self, unit):
		return 50
		
	def activate(self, unit):
		if unit.team == 1:
			self.activated += 1
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Code.Engine.Terrain import getTileSubsurface
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif self.timer >= 30:
			if (not GetTerrain(self.floor).canMoveThrough((self.source[0] - 1, self.source[1]), True)):
				x = 2; y = 1;
			elif (not GetTerrain(self.floor).canMoveThrough((self.source[0], self.source[1] - 1), True)):
				x = 1; y = 1;
			elif (not GetTerrain(self.floor).canMoveThrough((self.source[0], self.source[1] + 1), True)):
				x = 2; y = 2;
			else:
				x = 1; y = 2;
			if self.timer <= 40 or self.timer > 48:
				x += 2
			pic = getTileSubsurface("Traps", x, y)
		else:
			pic = getTileSubsurface("Traps", 0, 0)
		camera.getSurface().blit(pic, pos)
		
	def update(self):
		if self.activated:
			if self.timer > 47 and self.timer <= 48 and self.timer % 2 == 0:
				self.fire()
		self.timer = max(self.timer - 1, 0)
		if self.timer <= 0 and self.activated:
			self.timer = 50
				
	def fire(self):
		for u in PTRS["UNITS"].getTargets(1, True, True):
			p = posToCoords(u.getPos())
			if p[0] == self.source[0] and p[1] == self.source[1]:
				u.addDamage(1, None, self.DamageType)
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 2, 2)
		
	def canMoveThrough(self, unit):
		return True
		
	def canSeeThrough(self):
		return True
		
class FloorSpikeTrap(WallSpikeTrap):
	TrapId = PTRS["TRAPTYPES"].FLOORSPIKETRAP
	def parseArgs(self, args):
		self.timer = 0
		
	def getPathingHeuristic(self, unit):
		return 50
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
		from Code.Engine.Terrain import getTileSubsurface
		pic = None
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif self.timer >= 35:
			x = 4; y = 0;
			if self.timer <= 42 or self.timer > 48:
				x = 3; y = 0;
			pic = getTileSubsurface("Traps", x, y)
		elif self.wasDetected:
			pic = getTileSubsurface("Traps", 2, 0)
		if pic:
			camera.getSurface().blit(pic, pos)
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 4, 0)
		
class Treasure(Trap):
	TrapId = PTRS["TRAPTYPES"].TREASURE
	def parseArgs(self, args):
		self.open = [0, 100]
		self.dungeonRoom = None
		on = 0
		self.type = 0
		self.lastUnitTouched = None
		try:
			while on < len(args):
				if args[on] == "-d":
					self.dungeonRoom = args[on + 1]
					on += 1
				elif args[on] == "-t":
					self.type = args[on + 1]
				on += 1
		except:
			print "Treasure Error:", sys.exc_info()[0]
		
	def getPathingHeuristic(self, unit):
		return 0
		
	def activate(self, unit):
		if unit.team == 1:
			self.activated += 1
			self.lastUnitTouched = unit
		
	def deactivate(self, unit):
		self.activated = max(self.activated - 1, 0)
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Code.Engine.Terrain import getTileSubsurface
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
		elif self.open[0] < self.open[1]:
			pic = getTileSubsurface("Traps", 6 + self.type, 1)
		else:
			pic = getTileSubsurface("Traps", 6 + self.type, 2)
		camera.getSurface().blit(pic, pos)
		if 0 < self.open[0] < self.open[1]:
			pygame.draw.rect(camera.getSurface(), [255, 255, 0], [pos, [int(TILESIZE[0] * self.open[0] / float(self.open[1])), 4]])
			pygame.draw.rect(camera.getSurface(), [255] * 3, [pos, [TILESIZE[0], 4]], 1)
		
	def update(self):
		if self.activated and self.open[0] < self.open[1]:
			self.open[0] = min(self.open[0] + 1, self.open[1])
			if self.open[0] >= self.open[1]:
				if self.dungeonRoom:
					self.dungeonRoom.treasureCollected(self.type, self.lastUnitTouched)
		elif self.open[0] < self.open[1]:
			self.open[0] = max(self.open[0] - 1, 0)
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 6, 1)
		
	def canMoveThrough(self, unit):
		return True
		
	def canSeeThrough(self):
		return True
		
class Shrine(Treasure):
	TrapId = PTRS["TRAPTYPES"].SHRINE
	FileName = "Shrines"
	def __init__(self, topLeft, floor, shrineX, shrineY, layer=0, solid=True):
		Trap.__init__(self, topLeft, floor, args=[])
		self.shrineX = shrineX
		self.shrineY = shrineY
		self.layer = layer
		self.isSolid = solid
		
	def canMoveThrough(self, unit):
		return not self.isSolid
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		from Code.Engine.Terrain import getTileSubsurface
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		pic = getTileSubsurface(self.FileName, self.shrineX, self.shrineY)
		camera.getSurface().blit(pic, pos)
		
class SolidSquare(Trap):
	TrapId = PTRS["TRAPTYPES"].SHRINE
	def __init__(self, topLeft, floor, shrineX, shrineY):
		Trap.__init__(self, topLeft, floor, args=[])
		self.shrineX = shrineX
		self.shrineY = shrineY
		
	def drawMe(self, camera):
		pass
		
	def canMoveThrough(self, unit):
		return False
		
class Decoration(Shrine):
	FileName = "Decorations"
		
"""
class BoulderTrap(Trap):
	TrapId = PTRS["TRAPTYPES"].POWEREDDOOR
	def parseArgs(self, args):
		self.unitHasKey = 0
		self.backupUnitHasKey = 0
		self.key = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-k":
					self.key = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Powered Door Error:", sys.exc_info()[0]
			
	def getPathingHeuristic(self, unit):
		if unit.getItemHeld() == self.key or unit.getItemHeld() == -1:
			return 0
		if self.activated:
			return 0
		else:
			return 10000
			
	def update(self):
		self.unitHasKey -= self.unitHasKey > 0
		
	def saveParameters(self, fileOut):
		fileOut.write("-k " + str(self.key))
		
	def drawMe(self, camera):
		pos = [self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()]
		from Code.Engine.Terrain import getTileSubsurface
		if self.activated or self.unitHasKey:
			if PTRS["EDITORMODE"]:
				pic = getTileSubsurface("Traps", 1, 0)
			else:
				pic = getTileSubsurface("Traps", 0, 0)
		else:
			pic = getTileSubsurface("Traps", 0, 1 + variation)
		camera.getSurface().blit(pic, pos)
		if self.key != 0 and (PTRS["EDITORMODE"] or not self.activated and not self.unitHasKey):
			pos = [pos[0] + TILESIZE[0] / 2 - lockPics.get_width() / 2, 
						 pos[1] + TILESIZE[1] /2 - lockPics.get_width() / 2]
			pic = lockPics.subsurface(((0, (self.key - 1) * lockPics.get_width()), (lockPics.get_width(), lockPics.get_width())))
			camera.getSurface().blit(pic, pos)
		
	def activate(self, unit):
		self.activated = True
		
	def deactivate(self, unit):
		pass
		
	def canMoveThrough(self, unit):
		return self.activated
		
	def canSeeThrough(self):
		return self.activated
		
	def deactivate(self):
		pass
		
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 5, 1)
		
	def addNumberParameter(self, number):
		if 0 <= number < 5:
			PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], self.floor, 
																											[255] * 3, 30, str(number)))
			self.key = number

		"""
class Repeater(Trap):
	TrapId = PTRS["TRAPTYPES"].REPEATER
	def parseArgs(self, args):
		self.time = 70
		self.timer = random.randint(0, self.time / 2)
		self.backupTime = 0
		on = 0
		try:
			while on < len(args):
				if args[on] == "-t":
					self.time = int(args[on+1])
					on += 1
				on += 1
		except:
			print "Repeater Error:", sys.exc_info()[0]
			
		self.timer = random.randint(0, self.time / 2)
			
	def addNumberParameter(self, number):
		numberLookup = {0:6, 1:20, 2:40, 3:60, 4:80, 5:100, 6:150, 7:200, 8:300, 9:600}
		PTRS["EFFECTS"].addEffect(Effects.TextEffect([self.source[0] * TILESIZE[0], self.source[1] * TILESIZE[1]], self.floor, 
																										[255] * 3, 30, str(numberLookup[number])))
		self.time = numberLookup[number]
		
	def saveParameters(self, fileOut):
		fileOut.write("-t " + str(self.time))
		
	def backup(self):
		self.backupTime = self.timer
		
	def restore(self):
		self.timer = self.backupTime
		
	def update(self):
		self.timer = (self.timer + 1) % self.time
		if self.timer == self.time - 1:
			GetTerrain(self.floor).updateTrapTrigger(self.source, True)
		elif self.timer == 0:
			GetTerrain(self.floor).updateTrapTrigger(self.source, False)
			
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		if PTRS["EDITORMODE"]:
			pic = self.previewTrap()
			pos = [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE]
			camera.getSurface().blit(pic, pos)
			
	def previewTrap(self):
		from Code.Engine.Terrain import getTileSubsurface
		return getTileSubsurface("Traps", 5, 0)
		
	def canMoveThrough(self, unit):
		return True
		
	def canSeeThrough(self):
		return True
		
	def triggersTraps(self):
		return self.timer > self.time / 2
		
		
	def activate(self, unit):
		pass
		
	def deactivate(self, unit):
		pass
	
def createTrap(coords, type, floor, args):
	toRet = None
	if type == PTRS["TRAPTYPES"].POWEREDDOOR:
		toRet = PoweredDoor
	elif type == PTRS["TRAPTYPES"].WALLSPIKETRAP:
		toRet = WallSpikeTrap
	elif type == PTRS["TRAPTYPES"].FLOORSPIKETRAP:
		toRet = FloorSpikeTrap
	elif type == PTRS["TRAPTYPES"].REPEATER:
		toRet = Repeater
	elif type == PTRS["TRAPTYPES"].SECRETDOOR:
		toRet = SecretDoor
	elif type == PTRS["TRAPTYPES"].TREASURE:
		toRet = Treasure
	elif type == PTRS["TRAPTYPES"].STAIRS:
		toRet = Stairs
	else:
		toRet = Trap
	if toRet:
		return toRet(coords, floor, args)
	return None
	