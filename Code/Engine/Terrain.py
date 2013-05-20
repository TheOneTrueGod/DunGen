import pygame, os, random, Globals
import Code.Engine.Traps as Traps
from Globals import *
def loadTerrainPics(terrainPics):
	dirPath = os.path.join("Data", "Pics", "Tiles")
	for file in os.listdir(dirPath):
		file = os.path.splitext(file)
		if file[1].upper() == ".PNG":
			terrainPics[file[0]] = pygame.image.load(os.path.join(dirPath, "".join(file)))
			#if file[0] != "WaterTiles":
			#	terrainPics[file[0]].set_colorkey([255, 0, 255])
terrainPics = {}
tilesetMap = {}

def loadTilesetMap(tilesetMap):
	filePath = os.path.join("Data", "Pics", "Tiles", "Tilesets.txt")
	if os.path.isfile(filePath):
		fileIn = open(filePath)
		line = fileIn.readline()
		while line:
			line = line.split()
			if len(line) == 2 and len(line[1]) < 3 and line[1].isdigit() and len(line[0]) < 30 and line[1] not in tilesetMap:
				tilesetMap[line[1]] = line[0]
			line = fileIn.readline()
		fileIn.close()
	else:
		from Data.Pics.Tiles.TSReg import registerTilesets
		registerTilesets()
		
def tilesetLookup(tilesetNum):
	global tilesetMap
	if tilesetNum in tilesetMap:
		return tilesetMap[tilesetNum]
	else:
		return "Default"
	
def getTileSubsurface(tileset, tile, variation, tilesize = TILESIZE):
	return terrainPics[tileset].subsurface([[tile * tilesize[0], variation * tilesize[1]], tilesize])
	
offsetLookup = {0:[0, 0], 1:[1, 0], 2:[2, 0], 3:[3, 0], 4:[4, 0], 5:[5, 0], 6:[6, 0], 7:[7, 0]}
mergeList = {0:[0, 1, 2, 3, 5, 9], 1:[1], 2:[2], 3:[3, 9], 5:[5, 9], 9:[]}
#0 - Grass, 1 - Wall, 2 - Water, 3 - Path, 4 - Lava, 5 - Regular Decoration, 6 - Slowing Decoration
dirLookup = {0:[None], 1:[None], 2:[None], 3:[[0,1]], 4:[None], 5:[None], 6:[[0, 0]], 
								7:[[0, 3], [0, 4]], 8:[None], 9:[[1, 1]], 10:[None], 
							 11:[[1, 5], [2, 5]], 12:[[1, 0]], 13:[[3, 3], [3, 4]], 14:[[1, 2], [2, 2]], 15:[[1, 3], [2, 3], [1, 4], [2, 4]]}
diagLookup = {0:[None], 1:[[1, 1]], 2:[[0, 1]], 3:[[1, 5], [2, 5]], 4:[[0, 0]], 5:[[1, 3]], 6:[[0, 3], [0, 4]], 
							  7:[[2, 1]], 8:[[1, 0]], 9:[[3, 3], [3, 4]], 10:[[1, 3]], 
							 11:[[3, 1]], 12:[[1, 2], [2, 2]], 13:[[3, 0]], 14:[[2, 0]], 15:[[1, 3], [2, 3], [1, 4], [2, 4]]}
							 
def getAdjustedTile(tileset, TPtr, coord, offset):
	tileType = TPtr.getAtCoord(coord)
	surface = pygame.Surface(TILESIZE)
	#				1   2
	#				8   4
	
	#     [9] 1 [3]
	#      8     2
	#    [12] 4 [6]
	#  If the tile in that quadrant is the same type, that bit is on.
	for x in [0, 1]:
		for y in [0, 1]:
			directions = 0
			on = 0
			#dirs = []
			for dir in [[0, -1], [1, 0], [0, 1], [-1, 0]]:
				atCoord = TPtr.getAtCoord((coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2))
				TSAtCoord = TPtr.getAtCoord((coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2), 0)
				directions += ((tileset == TSAtCoord or atCoord in [9] or (atCoord == 3 == tileType)) and atCoord in mergeList[tileType]) * 2 ** on
				#dirs += [[(coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2), TPtr.getAtCoord((coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2))]]
				on += 1
			#if direction in [3, 6, 12, 9]:
				#yTest = -(direction / 1 % 2 == 1) + (direction / 4 % 2 == 1)
				#xTest = -(direction / 8 % 2 == 1) + (direction / 2 % 2 == 1)
				#if (TPtr.getAtCoord((coord[0] + (xTest + dir[0]) / 2, coord[1] + (yTest + dir[1]) / 2)) not in [tileType, 9])
			dl = random.choice(dirLookup[directions])
			if not dl:
				print "No Direction Lookup!  Tiletype:", tileType, "directions:",directions
			else:
				if directions == 15:
					directions = 0
					on = 0
					for dir in [[-1, -1], [1, -1], [1, 1], [-1, 1]]:
						atCoord = TPtr.getAtCoord((coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2))
						TSAtCoord = TPtr.getAtCoord((coord[0] + (x + dir[0]) / 2, coord[1] + (y + dir[1]) / 2), 0)
						directions += ((tileset == TSAtCoord or atCoord == 9) and atCoord in mergeList[tileType]) * 2 ** on
						on += 1
					dl = random.choice(diagLookup[directions])
				
				surface.blit(
					getTileSubsurface(tilesetLookup(tileset), offset[0] * 2 * 2 + dl[0], offset[1] * 3*2 + dl[1], [TILESIZE[0] / 2, TILESIZE[1] / 2]), 
						[x * TILESIZE[0] / 2, y * TILESIZE[1] / 2])
	return surface
	
def generateVariation(tileset):
	noiseTypes = int(terrainPics[tilesetLookup(tileset)].get_height() / TILESIZE[1])
	if noiseTypes:
		nt = random.randint(0, noiseTypes - 1) #max(min(int(random.triangular(0, noiseTypes, 0)) + 1, noiseTypes - 1), 0)
		for i in range(1, noiseTypes):
			if nt > i:
				nt = random.randint(0, noiseTypes - 1)
			else:
				break
		
		return nt
	return 0
	
class PatrolPath:
	def __init__(self, line, loadFromLine = True):
		self.destinations = []
		self.searchAngles = []
		self.scanTime = DEFAULTSCANTIME
		if not loadFromLine:
			self.source = [int(line[0]), int(line[1])]
			return
		self.source = [int(line[1]), int(line[2])]
		on = 3
		try:
			while on < len(line):
				if line[on] == "-d":
					self.destinations += [(int(line[on+1]), int(line[on+2]))]
					on += 2
				elif line[on] == "-t":
					self.scanTime = int(line[on+1])
					on += 1
				elif line[on] == "-a":
					self.searchAngles += [int(line[on+1]) / 180.0 * math.pi]
					on += 1
				on += 1
		except:
			print "Patrol Path Error:", sys.exc_info()[0]
	
	def save(self, fileOut):
		fileOut.write("PATROLPATH " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " ")
		for d in self.destinations:
			fileOut.write("-d " + str(int(d[0])) + " " + str(int(d[1])) + " ")
		fileOut.write("-t " + str(int(self.scanTime)) + " ")
		for a in self.searchAngles:
			fileOut.write("-a " + str(int(a / math.pi * 180)) + " ")
		fileOut.write("\n")
		
	def getScanTime(self):
		return self.scanTime
		
	def getScanAngles(self):
		return self.searchAngles
		
	def setScanTime(self, time):
		self.scanTime = int(time)
		
	def addTargetAngle(self, angle):
		a = angle % (math.pi * 2)
		try:
			self.searchAngles.remove(a)
		except ValueError:
			self.searchAngles += [a]
		
	def addDestination(self, newDest):
		if newDest not in self.destinations and (newDest[0] != self.source[0] or newDest[1] != self.source[1]):
			self.destinations += [newDest]
			
	def removeDestination(self, dest):
		try:
			self.destinations.remove((dest[0], dest[1]))
			return True
		except:
			return False
		
	def getDestination(self, destNum):
		if 0 <= destNum < len(self.destinations):
			return (self.destinations[destNum][0], self.destinations[destNum][1])
		return [self.source[0], self.source[1]]
		
	def getNumDestinations(self):
		return len(self.destinations)
		
	def drawMe(self, camera):
		pygame.draw.rect(camera.getSurface(), [0, 255, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), 
																												 self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE], 1)
		src = [self.source[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), self.source[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
		for dest in self.destinations:
			pygame.draw.rect(camera.getSurface(), [0, 255, 0], [[dest[0] * TILESIZE[0] + 2 - camera.Left(), dest[1] * TILESIZE[1] + 2 - camera.Top()], [TILESIZE[0] - 4, TILESIZE[1] - 4]], 1)
			
			dst = [dest[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), dest[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
			ang = math.atan2(dst[1] - src[1], dst[0] - src[0])
			dst = [dst[0] - math.cos(ang) * 10, dst[1] - math.sin(ang) * 10]
			
			pygame.draw.line(camera.getSurface(), [0, 255, 0], [src[0] + math.cos(ang) * 10, src[1] + math.sin(ang) * 10], 
																						 dst)
			pygame.draw.line(camera.getSurface(), [0, 255, 0], dst, [dst[0] + math.cos(ang + math.pi * 3 / 4) * 7, dst[1] + math.sin(ang + math.pi * 3 / 4) * 7])
			pygame.draw.line(camera.getSurface(), [0, 255, 0], dst, [dst[0] + math.cos(ang - math.pi * 3 / 4) * 7, dst[1] + math.sin(ang - math.pi * 3 / 4) * 7])
		
		for a in self.searchAngles:
			pygame.draw.line(camera.getSurface(), [200, 0, 0], [src[0] + math.cos(a) * 5, src[1] + math.sin(a) * 5],
																						 [src[0] + math.cos(a) * 20, src[1] + math.sin(a) * 20])
		
class TrapTrigger:
	def __init__(self, line, floor, loadFromLine = True):
		self.floor = floor
		self.destinations = []
		self.delayTime = 1
		if not loadFromLine:
			self.source = [int(line[0]), int(line[1])]
			self.destinations = [(int(line[0]), int(line[1]))]
			return
		self.source = [int(line[1]), int(line[2])]
		self.destinations = [(int(line[1]), int(line[2]))]
		on = 3
		try:
			while on < len(line):
				if line[on] == "-d":
					self.destinations += [(int(line[on+1]), int(line[on+2]))]
					on += 2
				elif line[on] == "-t":
					self.delayTime = int(line[on+1])
					on += 1
				on += 1
		except:
			print "Trap Trigger Error:", sys.exc_info()[0]
			
	def finishedLoading(self):
		if GetTerrain(self.floor).triggersTraps((self.source[0], self.source[1])):
			for d in self.destinations:
				trap = GetTerrain(self.floor).getTrapAtCoord(d)
				if trap:
					trap.activate(None)
	
	def save(self, fileOut):
		fileOut.write("TRAPTRIGGER " + str(int(self.source[0])) + " " + str(int(self.source[1])) + " ")
		for d in self.destinations:
			fileOut.write("-d " + str(int(d[0])) + " " + str(int(d[1])) + " ")
		fileOut.write("-t " + str(int(self.delayTime)) + " ")
		fileOut.write("\n")
		
	def getDelayTime(self):
		return self.delayTime
		
	def setDelayTime(self, time):
		self.delayTime = int(time)
		
	def addDestination(self, newDest):
		if newDest not in self.destinations and (newDest[0] != self.source[0] or newDest[1] != self.source[1]):
			self.destinations += [newDest]
			if GetTerrain(self.floor).triggersTraps((self.source[0], self.source[1])):
				trap = GetTerrain(self.floor).getTrapAtCoord(newDest)
				if trap:
					trap.activate(None)
			
	def removeDestination(self, dest):
		try:
			if GetTerrain(self.floor).triggersTraps((self.source[0], self.source[1])):
				on = 0
				while on < len(self.destinations) and self.destinations[on] != (dest[0], dest[1]):
					on += 1
				if on < len(self.destinations):
					trap = GetTerrain(self.floor).getTrapAtCoord(self.destinations[on])
					trap.deactivate(None)
					del self.destinations[on]
			else:
				self.destinations.remove((dest[0], dest[1]))
			return True
		except:
			return False
			
	def removeAllDestinations(self):
		while len(self.destinations) and self.removeDestination(self.destinations[0]):
			pass
			
	def activate(self):
		for d in self.destinations:
			trap = GetTerrain(self.floor).getTrapAtCoord(d)
			if trap:
				trap.activate(None)
				
	def deactivate(self):
		for d in self.destinations:
			trap = GetTerrain(self.floor).getTrapAtCoord(d)
			if trap:
				trap.deactivate(None)
			
	def getDestination(self, destNum):
		if 0 <= destNum < len(self.destinations):
			return (self.destinations[destNum][0], self.destinations[destNum][1])
		return [self.source[0], self.source[1]]
		
	def getNumDestinations(self):
		return len(self.destinations)
		
	def unitEnteredTrigger(self, unit):
		for dest in self.destinations:
			trap = GetTerrain(unit.floor).getTrapAtCoord(dest)
			if trap:
				trap.activate(unit)
		
	def unitExitedTrigger(self, unit):
		for dest in self.destinations:
			trap = GetTerrain(unit.floor).getTrapAtCoord(dest)
			if trap:
				trap.deactivate(unit)
		
	def notifyUnitMovement(self, unit, lastPos, currPos):
		if currPos[0] != lastPos[0] or currPos[1] != lastPos[1]:
			if currPos[0] == self.source[0] and currPos[1] == self.source[1]:
				self.unitEnteredTrigger(unit)
			elif lastPos[0] == self.source[0] and lastPos[1] == self.source[1]:
				self.unitExitedTrigger(unit)
		
	def drawMe(self, camera):
		pygame.draw.rect(camera.getSurface(), [255, 0, 0], [[self.source[0] * TILESIZE[0] - camera.Left(), self.source[1] * TILESIZE[1] - camera.Top()], TILESIZE], 1)
		src = [self.source[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), self.source[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
		for dest in self.destinations:
			if dest[0] != self.source[0] or dest[1] != self.source[1]:
				pygame.draw.rect(camera.getSurface(), [255, 0, 0], [[dest[0] * TILESIZE[0] + 2 - camera.Left(), dest[1] * TILESIZE[1] + 2 - camera.Top()], [TILESIZE[0] - 4, TILESIZE[1] - 4]], 1)
				
				dst = [dest[0] * TILESIZE[0] + TILESIZE[0] / 2 - camera.Left(), dest[1] * TILESIZE[1] + TILESIZE[1] / 2 - camera.Top()]
				ang = math.atan2(dst[1] - src[1], dst[0] - src[0])
				dst = [dst[0] - math.cos(ang) * 10, dst[1] - math.sin(ang) * 10]
				
				pygame.draw.line(camera.getSurface(), [255, 0, 0], [src[0] + math.cos(ang) * 10, src[1] + math.sin(ang) * 10], 
																							 dst)
				pygame.draw.line(camera.getSurface(), [255, 0, 0], dst, [dst[0] + math.cos(ang + math.pi * 3 / 4) * 7, dst[1] + math.sin(ang + math.pi * 3 / 4) * 7])
				pygame.draw.line(camera.getSurface(), [255, 0, 0], dst, [dst[0] + math.cos(ang - math.pi * 3 / 4) * 7, dst[1] + math.sin(ang - math.pi * 3 / 4) * 7])
		
		
class IncompleteStream:
	def __init__(self, room, boxSize):
		self.room = room
		self.stage = 0
		self.boxSize = boxSize
		self.tileOn = 0
		self.tileX = 0
		self.tileY = 0
		
class Terrain:
	def __init__(self, floor):
		self.terrain = [[[0, 1, 0]] * 40] + [[[0, 1, 0]] + [[0, 0, 0]] * 38 + [[0, 1, 0]]] * 28 + [[[0, 1, 0]] * 40]
		self.spawners = []
		self.terrainChanges = {}
		self.patrolPaths = {}
		self.enemies = {}
		self.trapTriggers = {}
		self.traps = {}
		self.backupItems = {}
		self.players = []
		self.backupSpawner = [0, 0]
		self.worldSize = (1600, 1200)
		self.tileset = "Default"
		self.terrainPic = None
		self.floor = floor
		self.incompleteStreams = []
					
	def update(self):
		l = [p for p in self.traps]
		on = 0
		while on < len(l):
			self.traps[l[on]].update()
			if self.traps[l[on]].readyToSleep:
				del self.traps[l[on]]
				del l[on]
			else:
				on += 1
				
	def initializeStreamedDungeon(self, floor):
		boxWidth = DUNGEONBOXSIZE[0]
		boxHeight = DUNGEONBOXSIZE[1]
		self.worldSize = ((DUNGEONSIZE[0] * (boxWidth + 1) + 1) * TILESIZE[0],
											(DUNGEONSIZE[1] * (boxHeight + 1) + 1) * TILESIZE[1])
		self.terrainPic = None
		GetTerrain(floor).createSquareArea(GetDungeonGrid(floor), DUNGEONBOXSIZE)
		
		x = STREAMSTARTPOS[0] * (boxWidth + 1) + 1 + int(boxWidth / 2)
		y = STREAMSTARTPOS[0] * (boxHeight + 1) + 1 + int(boxHeight / 2)
		
		if self.terrain[y][x][1] != 1:
			#self.setTile([x, y], [1, 2, 1])
			self.spawners += [(x, y)]
			self.spawnPos = (x * TILESIZE[0] + TILESIZE[0] / 2, y * TILESIZE[1] + TILESIZE[1] / 2)

	def createSquareArea(self, dungeonGrid, boxSize = (2, 2)):
		self.level = "RandDungeon.txt"
		boxWidth = boxSize[0]
		boxHeight = boxSize[1]
		size = (len(dungeonGrid.grid[0]), len(dungeonGrid.grid))
		self.spawners = []
		self.patrolPaths = {}
		self.trapTriggers = {}
		self.traps = {}
		self.enemies = {}
		self.players = []
		self.terrain = []
		self.terrain += [[]]
		del self.terrainPic
		self.terrainPic = None
		#Build the top wall
		for x in range(size[0] * (boxWidth+1)+1):
			self.terrain[0] += [[1, 1, 0]]
			#self.drawTile([x, 0])
		for y in range(size[1] * (boxWidth + 1) - 1):
			self.terrain += [[[1, 1, 0]]]
			#self.drawTile([0, y + 1])
			for x in range(size[0] * (boxWidth + 1) - 1):
				self.terrain[y+1] += [[0, 9, 0]]
			self.terrain[y+1] += [[1, 1, 0]]
			#self.drawTile([len(self.terrain[y]) - 1, y + 1])
			
		self.terrain += [[]]
		for x in range(size[0] * (boxWidth+1)+1):
			self.terrain[y+2] += [[1, 1, 0]]
			#self.drawTile([x, y + 2])
			
	def reset(self, firstLoad = False):
		self.loadFromFile(self.level, firstLoad)
		
	def getPatrolPathAtPos(self, pos):
		coords = posToCoords(pos)
		if coords in self.patrolPaths:
			return self.patrolPaths[coords]
		return None
		
	def getTrapTriggerAtPos(self, pos):
		coords = posToCoords(pos)
		if coords in self.trapTriggers:
			return self.trapTriggers[coords]
		return None
		
	def notifyUnitMovement(self, unit, lastPos, pos):
		lPos = posToCoords(lastPos)
		cPos = posToCoords(pos)
		if cPos in self.trapTriggers:
			self.trapTriggers[cPos].notifyUnitMovement(unit, lPos, cPos)
		if lPos in self.trapTriggers:
			self.trapTriggers[lPos].notifyUnitMovement(unit, lPos, cPos)
		#for pos in self.trapTriggers:
		#	
		
	def addNumberParameter(self, coord, number):
		coords = (int(coord[0]), int(coord[1]))
		if coords in self.traps:
			self.traps[coords].addNumberParameter(number)
		
	def addAngleParameter(self, coord, angle):
		coords = (int(coord[0]), int(coord[1]))
		if coords in self.traps:
			self.traps[coords].addAngleParameter(angle)
		
	def changeTrapType(self, pos, trapType, remove):
		coords = (int(pos[0]), int(pos[1]))
		newTrap = None
		if coords in self.traps and self.traps[coords].TrapId == trapType:
			del self.traps[coords]
		else:
			if coords in self.traps:
				del self.traps[coords]
			if not remove:
				newTrap = Traps.createTrap(coords, trapType, [])
		if newTrap:
			self.traps[coords] = newTrap
			
	def addTrapAtCoords(self, coords, trapType, floor, args=[]):
		coords = (int(coords[0]), int(coords[1]))
		newTrap = Traps.createTrap(coords, floor, trapType, args)
		self.traps[coords] = newTrap
		return newTrap
		
	def addTrap(self, trap):
		self.traps[trap.source] = trap
		
	def getSpawnPos(self):
		return [self.spawnPos[0], self.spawnPos[1]]
		#for sp in self.spawners:
		#	if self.getAtCoord(sp) == 2:
		#		return [sp[0] * TILESIZE[0] + TILESIZE[0] / 2, sp[1] * TILESIZE[1] + TILESIZE[1] / 2]
				
	def removePatrolDestination(self, source, dest):
		if (self.patrolPaths[source].removeDestination(dest) and not self.patrolPaths[source].destinations) or source == dest:
			del self.patrolPaths[source]
			
	def removeTrapDestination(self, source, dest):
		#if source in self.trapTriggers and (self.trapTriggers[source].removeDestination(dest) and not self.trapTriggers[source].destinations) or source == dest:
		if source in self.trapTriggers:
			self.trapTriggers[source].removeAllDestinations()
			del self.trapTriggers[source]
		
	def getTerrainChanges(self, playerNum):
		toRet = []
		if playerNum in self.terrainChanges:
			toRet = " ".join(self.terrainChanges[playerNum])
			del self.terrainChanges[playerNum]
		return toRet
		
	def randomizeVariations(self):
		y = 0
		for line in self.terrain:
			x = 0
			for square in line:
				self.terrain[y][x] = (square[0], square[1], generateVariation(square[0]))
				self.setTile([x, y], self.terrain[y][x])
				x += 1
			y += 1
			
	def getWorldSize(self):
		return self.worldSize
		
	def loadFromFile(self, floor, firstLoad = False):
		print "Loading"
		self.floor = floor
		del self.terrainPic
		self.terrainPic = None
		self.terrain = []
		self.spawners = []
		self.spawnPos = [-20, -20]
		self.tileset = "Default"
		#fileIn = open(os.path.join("Data", "Levels", file))
		fileIn = open(os.path.join("Profiles", "Dungeons", "Terrain"+str(self.floor)+".lv"))
		on = 0
		line = fileIn.readline()
		line = line.strip().split()
		rows = int(line[0]); cols = int(line[1])
		self.worldSize = (int(cols * TILESIZE[0]), int(rows * TILESIZE[1]))
		line = fileIn.readline()
		while line and not "END" in line:
			line = line.strip().split()
			if line[0].upper() == "TILESET" or line[0].upper() == "TS":
				if len(line) >= 2:
					self.tileset = line[1]
			else:
				self.terrain += [[]]
				x = 0
				while 0 <= x < len(line):
					p = line[x]
					if p.isdigit():
						self.terrain[on] += [[0, int(p), generateVariation(0)]]
						p = int(p)
						coords = [len(self.terrain[on]) - 1, on]
						self.setTile(coords, self.terrain[on][len(self.terrain[on]) - 1])
						if int(p) != 9:
							self.drawTile(coords)
					elif p.upper() == "TILESET" or p.upper() == "TS":
						if len(line) > x + 1:
							self.tileset = line[x + 1]
							x += 1
					else:
						p = p.split("-")
						if len(p) >= 3 and p[0].isdigit() and p[1].isdigit() and p[2].isdigit():
							self.terrain[on] += [[int(p[0]), int(p[1]), int(p[2])]]
							coords = [len(self.terrain[on]) - 1, on]
							self.setTile(coords, self.terrain[on][len(self.terrain[on]) - 1])
							if int(p[1]) != 9:
								self.drawTile(coords)
						else:
							self.terrain[on] += [[0, 0, 0]]
							coords = [len(self.terrain[on]) - 1, on]
							self.setTile(coords, self.terrain[on][len(self.terrain[on]) - 1])
							#self.drawTile(coords)
					x += 1
				if len(self.terrain[on]) < cols:
					for i in range(cols - len(self.terrain[on])):
						self.terrain[on] += [[0, 0, 0]]
				on += 1
			line = fileIn.readline()
			
			pct = fileIn.tell() / float(os.fstat(fileIn.fileno())[6])
			#self.drawProgressBar(pct)

		if len(self.terrain) < rows:
			for i in range(rows - len(self.terrain)):
				self.terrain += [[]]
				for j in range(cols):
					self.terrain[len(self.terrain) - 1] += [[0, 0, 0]]

	def saveToFile(self):
		fileOut = open(os.path.join("Profiles", "Dungeons", "Terrain"+str(self.floor)+".lv"), "w")
		fileOut.write(str(int(self.worldSize[1] / TILESIZE[1])) + " " + str(int(self.worldSize[0] / TILESIZE[0])) + "\n")
		for row in self.terrain:
			for col in row:
				fileOut.write(str(col[0]) + "-" + str(col[1]) + "-" + str(col[2]) + " ")
			fileOut.write("\n")
		fileOut.write("END\n")
		
		fileOut.close()
		
	def loadFromFile(self, floor):
		path = os.path.join("Profiles", "Dungeons", "Terrain"+str(floor)+".png")
		print "TERRAIN LOAD", path
		self.floor = floor
		self.terrainPic = pygame.image.load(path)
		
	def saveToFile(self):
		if self.terrainPic:
			path = os.path.join("Profiles", "Dungeons", "Terrain"+str(self.floor)+".png")
			print "TERRAIN SAVE", path
			pygame.image.save(self.terrainPic, path)
	#def drawProgressBar(self, pct):
	#	size = [400, 40]
	#	pygame.draw.rect(surface, [255, 0, 0], [[SCREENSIZE[0] / 2 - size[0] / 2, SCREENSIZE[1] / 2 - size[1] / 2], [int(size[0] * pct), size[1]]])
	#	pygame.draw.rect(surface, [255] * 3, [[SCREENSIZE[0] / 2 - size[0] / 2, SCREENSIZE[1] / 2 - size[1] / 2], size], 1)
	#	pygame.display.update()
			
	def addPatrolPathSource(self, sourceCoords):
		p = (int(sourceCoords[0]), int(sourceCoords[1]))
		if p not in self.patrolPaths:
			self.patrolPaths[p] = PatrolPath(sourceCoords, False)
			
	def addTrapTriggerSource(self, sourceCoords, floor):
		p = (int(sourceCoords[0]), int(sourceCoords[1]))
		if p not in self.trapTriggers:
			self.trapTriggers[p] = TrapTrigger(sourceCoords, floor, False)
			
	def getTrapAtCoord(self, coord):
		if coord in self.traps:
			return self.traps[coord]
		return None
		
	def updateTrapTrigger(self, coord, activate):
		if coord in self.trapTriggers:
			if activate:
				self.trapTriggers[coord].activate()
			else:
				self.trapTriggers[coord].deactivate()
			
	def getRandomSpawnPos(self, type):
		if type in self.spawners:
			spawner = self.spawners[type][random.randint(0, len(self.spawners[type]) - 1)]
			return [spawner[0] * TILESIZE[0] + int(TILESIZE[0] / 2), spawner[1] * TILESIZE[1] + int(TILESIZE[1])]
		
	def setAtPos(self, pos, newType):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		if 0 <= coords[1] < len(self.terrain) and 0 <= coords[0] < len(self.terrain[coords[1]]):
			self.terrain[coords[1]][coords[0]] = newType
			for pl in range(Globals.players.getNumPlayers()):
				Globals.players.getPlayer(pl).addTerrainChange(str(coords[0]) + "|" + str(coords[1]) + "|" + str(int(newType)))
	
	def getAtPos(self, pos, type=1):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		return self.getAtCoord(coords, type)
		
	def getAtCoord(self, coords, type=1):
		if 1 <= int(coords[1]) < len(self.terrain) - 2 and 1 <= int(coords[0]) < len(self.terrain[int(coords[1])]) - 2 and 0 <= type <= 2:
			return self.terrain[int(coords[1])][int(coords[0])][type]
		if type == 1:
			return 1
		else:
			row = max(min(coords[1], len(self.terrain)), 1)
			col = max(min(coords[0], len(self.terrain[row])), 1)
			return self.terrain[row][col][type]
		
	def convertToString(self):
		toRet = ""
		for y in range(len(self.terrain)):
			for x in range(len(self.terrain[y])):
				if toRet:
					toRet += " "
				toRet += str(x) + "|" + str(y) + "|" + str("-".join(self.terrain[y][x]))
		return toRet

	def setSpawner(self, pos):
		coords = [int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1])]
		for sp in self.spawners:
			if sp[0] == coords[0] and sp[1] == coords[1]:
				for sp2 in self.spawners:
					self.setTile(sp2, (self.getAtCoord(sp2, 0), 3, self.getAtCoord(sp2, 2)))
				self.setTile(sp, (self.getAtCoord(sp, 0), 2, self.getAtCoord(sp, 2)))
				self.spawnPos = (coords[0] * TILESIZE[0] + TILESIZE[0] / 2, coords[1] * TILESIZE[1] + TILESIZE[1] / 2)
				break

	def recursiveSetTile(self, coords, newValue):
		if 0 > coords[0] or 0 > coords[1] or self.worldSize[0] / TILESIZE[0] <= coords[0] or self.worldSize[1] / TILESIZE[1] <= coords[1]:
			return
		tileAt = self.getAtCoord(coords, 1)
		tileSetAt = self.getAtCoord(coords, 0)
		self.setTile(coords, newValue)
		for mod in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
			tile = self.getAtCoord((coords[0] + mod[0], coords[1] + mod[1]), 1)
			tileSet = self.getAtCoord((coords[0] + mod[0], coords[1] + mod[1]), 0)
			if (tile == tileAt and tileSet == tileSetAt):
				self.recursiveSetTile((coords[0] + mod[0], coords[1] + mod[1]), newValue)
	
	def setTile(self, coords, newValue, override = False):
		#if (coords[0] <= 0 or coords[0] >= len(self.terrain[0]) - 1 or coords[1] <= 0 or coords[1] >= len(self.terrain) - 1) and not override:
		#	self.setTile(coords, [newValue[0], 1, newValue[2]], True)
		#	return
			
		#if isSpawner(newValue[1]):
		#	if (coords[0], coords[1]) not in self.spawners:
		#		self.spawners += [(coords[0], coords[1])]
		#	if newValue[1] == 2 or self.spawnPos[0] == -20 and self.spawnPos[1] == -20:
		# self.spawners += [(coords[0], coords[1])]
		#		self.spawnPos = (coords[0] * TILESIZE[0] + TILESIZE[0] / 2, coords[1] * TILESIZE[1] + TILESIZE[1] / 2)
		#elif (coords[0], coords[1]) in self.spawners:
		#	self.spawners.remove((coords[0], coords[1]))
		self.terrain[coords[1]][coords[0]] = (newValue[0], newValue[1], newValue[2])
		
	def drawTile(self, coords, recurse=False):
		#print "DrawTile", coords
		if not (0 <= coords[1] < len(self.terrain) and 0 <= coords[0] < len(self.terrain[coords[1]])):
			return
		if self.terrainPic is None:
			self.terrainPic = pygame.Surface(self.worldSize)
			
		pos = (coords[0] * TILESIZE[0], coords[1] * TILESIZE[1])
		t = [self.getAtCoord((coords[0], coords[1]), 0),
				 self.getAtCoord((coords[0], coords[1]), 1),
				 self.getAtCoord((coords[0], coords[1]), 2)]
		if t[1] == 9:
			return
		self.terrainPic.blit(getAdjustedTile(t[0], self, coords, offsetLookup[t[1]]), [coords[0] * TILESIZE[0], coords[1] * TILESIZE[1]])
		if recurse:
			for i in [[0, -1], [1, 0], [0, 1], [-1, 0]]:
				c = [coords[0] + i[0], coords[1] + i[1]]
				self.drawTile(c, False)
				
	def streamDungeonGrid(self, dungeonGrid, room, piece, boxSize = (2, 2)):
		#for istr in self.incompleteStreams:
		#	if istr.room == room:
		#		return
		#self.incompleteStreams += [IncompleteStream(room, boxSize)]
		#return
		streamBox = (room.pos, (room.pos[0] + room.piece.getWidth(), room.pos[1] + room.piece.getHeight()))
		tileset = 1
		solidTile = 1
		self.level = "RandDungeon.txt"
		boxWidth = boxSize[0]
		boxHeight = boxSize[1]
		#size = (streamBox[1][0] - streamBox[0][0],streamBox[1][1] - streamBox[0][1])
		##LW - Left Wall, TW - Top Wall, RW - Right Wall, BW - Bottom Wall
		##--------------------------------------
		##|        TW      ooooo     TW        |
		##| LW   (x, y) RW ox,yo LW (x+1,y) RW |
		##|        BW      ooooo     BW        |
		##--------ox,yo----ox,yo----------------
		##|        TW      ooooo     TW        |
		##| LW  (x, y+1)  RW | LW (x+1,y+1) RW |
		##|        BW        |       BW        |
		##--------------------------------------
		for p in room.spawnableTiles:
			x = p[0]
			y = p[1]
			for h in range(boxHeight):
				for w in range(boxWidth):
					#Build the center
					if 0 <= y < dungeonGrid.getHeight() and 0 <= x < dungeonGrid.getWidth():
						xPos = x * (boxWidth + 1) + w + 1
						yPos = y*(boxHeight + 1)+h + 1
						if dungeonGrid.grid[y][x]:
							tileset = dungeonGrid.getTilesetAt((x, y), False)
							self.setTile([xPos, yPos], [tileset, solidTile, generateVariation(tileset)])
						else:
							if self.terrain[yPos][xPos][1] in [1, 9]:
								tileset = dungeonGrid.getTilesetAt((x, y))
								self.setTile([xPos, yPos], [tileset, dungeonGrid.getRandomWalkableTile((x, y), (xPos, yPos)), generateVariation(tileset)])
		#Build the walls
		for y in range(streamBox[0][1], streamBox[1][1]):
			for x in range(streamBox[0][0] - 1, streamBox[1][0]):
				for h in range(boxHeight):
					#Build the y-axis walls
					if 0 <= y < dungeonGrid.getHeight() and 0 <= x < dungeonGrid.getWidth() and ((x, y) in room.spawnableTiles or (x + 1, y) in room.spawnableTiles):
						xPos = (x+1) * (boxWidth + 1)
						yPos = y*(boxHeight + 1)+h + 1
						if dungeonGrid.grid[y][x] or dungeonGrid.walls[y][x] & RIGHTWALL or getAtCoord(dungeonGrid.walls, (x + 1, y)) & LEFTWALL or x == streamBox[1][0] - 1:
							if self.terrain[yPos][xPos][1] == 9:
								tileset = dungeonGrid.getTilesetAt((x, y), False)
								self.setTile([xPos, yPos], [tileset, solidTile, generateVariation(tileset)])
						else:
							if self.terrain[yPos][xPos][1] in [1, 9]:
								tileset = dungeonGrid.getTilesetAt((x, y))
								self.setTile([xPos, yPos], [tileset, dungeonGrid.getRandomWalkableTile((x, y), (xPos, yPos)), generateVariation(tileset)])
		for y in range(streamBox[0][1] - 1, streamBox[1][1]):
			for x in range(streamBox[0][0], streamBox[1][0]):
			#Build the x-axis walls
				if 0 <= y < dungeonGrid.getHeight() and 0 <= x < dungeonGrid.getWidth() and ((x, y) in room.spawnableTiles or (x, y + 1) in room.spawnableTiles):
					for w in range(boxWidth):
						xPos = (x * (boxWidth + 1)) + w + 1
						yPos = (y+1)*(boxHeight + 1)
						if dungeonGrid.grid[y][x] or dungeonGrid.walls[y][x] & BOTWALL or getAtCoord(dungeonGrid.walls, (x, y + 1)) & TOPWALL or y == streamBox[1][1] - 1:
							if self.terrain[yPos][xPos][1] == 9:
								tileset = dungeonGrid.getTilesetAt((x, y), False)
								self.setTile([xPos, yPos], [tileset, solidTile, generateVariation(tileset)])
						else:
							if self.terrain[yPos][xPos][1] in [1, 9]:
								tileset = dungeonGrid.getTilesetAt((x, y))
								self.setTile([xPos, yPos], [tileset, dungeonGrid.getRandomWalkableTile((x, y), (xPos, yPos)), generateVariation(tileset)])
		for y in range(streamBox[0][1] - 1, streamBox[1][1]):
			for x in range(streamBox[0][0] - 1, streamBox[1][0]):
				if 0 <= y < dungeonGrid.getHeight() and 0 <= x < dungeonGrid.getWidth() and ((x, y) in room.spawnableTiles or (x + 1, y) in room.spawnableTiles or (x, y + 1) in room.spawnableTiles or (x + 1, y + 1) in room.spawnableTiles):
					xPos = (x+1) * (boxWidth  + 1)
					yPos = (y+1) * (boxHeight + 1)
					#The dot in between four corners
					if x == streamBox[1][0] - 1 or dungeonGrid.grid[y][x] or getAtCoord(dungeonGrid.walls, (x, y)) & BOTWALL or getAtCoord(dungeonGrid.walls, (x, y)) & RIGHTWALL or \
													 getAtCoord(dungeonGrid.walls, (x + 1, y)) & BOTWALL or getAtCoord(dungeonGrid.walls, (x + 1, y)) & LEFTWALL or \
													 getAtCoord(dungeonGrid.walls, (x, y + 1)) & RIGHTWALL or getAtCoord(dungeonGrid.walls, (x, y + 1)) & TOPWALL or \
													 getAtCoord(dungeonGrid.walls, (x + 1, y + 1)) & LEFTWALL or getAtCoord(dungeonGrid.walls, (x + 1, y + 1)) & TOPWALL:
						if self.terrain[yPos][xPos][1] == 9:
							tileset = dungeonGrid.getTilesetAt((x, y), False)
							self.setTile([xPos, yPos], [tileset, solidTile, generateVariation(tileset)])
					else:
						if self.terrain[yPos][xPos][1] in [1, 9]:
							tileset = dungeonGrid.getTilesetAt((x, y))
							self.setTile([xPos, yPos], [tileset, dungeonGrid.getRandomWalkableTile((x, y), (xPos, yPos)), generateVariation(tileset)])
				
		#Time to add the doors
		for p in room.spawnableTiles:
			w = p[0]
			h = p[1]
			if (w, h) in dungeonGrid.doors:
				for d in dungeonGrid.doors[(w, h)]:
					#d = dungeonGrid.doors[(w, h)]
					x, y = getDoorCoordinates((w, h), (boxWidth, boxHeight), d)
					#x = w * (boxWidth + 1) + 1 + int(boxWidth / 2) + int(boxWidth / 2 + 1) * d[0]
					#y = h * (boxHeight + 1) + 1 + int(boxHeight / 2) + int(boxHeight / 2 + 1) * d[1]
					if boxWidth % 2 == 0 and d[0] > 0:
						x -= 1
					if boxHeight % 2 == 0 and d[1] > 0:
						y -= 1
					
					if self.terrain[y][x][1] in [1, 9]:
						tileset = dungeonGrid.getTilesetAt((x, y))
						self.setTile([x, y], [self.getAtCoord((x, y), 0), dungeonGrid.getRandomWalkableTile((w - (d[0] < 0), h - (d[1] < 0)), (x, y)), self.getAtCoord((x, y), 2)])
					self.traps[(x, y)] = Traps.StreamingDoor((x, y), dungeonGrid.floor)
		
		dungeonGrid.setDecorativeTiles(self, room, boxSize)
		
				#Draw all of the tiles
		for p in room.spawnableTiles:
			x = p[0]
			y = p[1]
			for h in range(-1, boxHeight + 1):
				for w in range(-1, boxWidth + 1):
					#Build the center
					if 0 <= y < dungeonGrid.getHeight() and 0 <= x < dungeonGrid.getWidth():
						xPos = x * (boxWidth + 1)  + w + 1
						yPos = y * (boxHeight + 1) + h + 1
						if 0 < yPos < len(self.terrain) - 1 and 0 < xPos < len(self.terrain[yPos]) - 1:
							if xPos == 1:
								self.drawTile([xPos - 1, yPos])
								if yPos == 1:
									self.drawTile([xPos - 1, yPos - 1])
							if yPos == 1:
								self.drawTile([xPos, yPos - 1])
							self.drawTile([xPos, yPos])
	
	def drawMe(self, camera):
		if not self.terrainPic:
			return
		camera.getSurface().blit(self.terrainPic.subsurface([
				(max(camera.Left(), 0), max(camera.Top(), 0)), 
				(min(camera.Width(), self.worldSize[0] - camera.Left()), min(camera.Height(), self.worldSize[1] - camera.Top()))
				]), [max(-camera.Left(), 0), max(-camera.Top(), 0)])
			
	def drawTraps(self, camera, layer):
		for p in self.traps:
			if self.traps[p].layer == layer:
				if camera.Left() - TILESIZE[0] < coordsToPos(self.traps[p].source)[0] < camera.Right() + TILESIZE[0] and \
					 camera.Top() - TILESIZE[1] < coordsToPos(self.traps[p].source)[1] < camera.Bottom() + TILESIZE[1]:
					self.traps[p].drawMe(camera)
			
	def canMoveThrough(self, coord, unit = None, ignoreTraps = False):
		#if unit and unit.team == 2 and self.getAtCoord(coord) == 9:
		#	return False
		if canMoveThrough(self.getAtCoord(coord)):
			if coord not in self.traps or ignoreTraps or self.traps[coord].canMoveThrough(unit):
				return True
		return False
		
	def triggersTraps(self, coord):
		if (not self.canMoveThrough(coord)) or coord in self.traps and self.traps[coord].triggersTraps():
			return True
		return False
	
	def canSeeThrough(self, coord, unit = None):
		coord = (coord[0], coord[1])
		if canSeeThrough(self.getAtCoord(coord)):
			if coord not in self.traps or self.traps[coord].canSeeThrough():
				return True
		return False
	
	@staticmethod
	def getCost(self,	nodeA, nodeB, unit):
		cost = abs(nodeA[0] - nodeB[0]) + abs(nodeA[1] - nodeB[1])
		toRet = 100000
		if cost == 1:
			toRet = 10
		if cost == 2:
			toRet = 14
		return toRet
		
	@staticmethod	
	def getCostWithTraps(self,	nodeA, nodeB, unit):
		cost = abs(nodeA[0] - nodeB[0]) + abs(nodeA[1] - nodeB[1])
		toRet = 100000
		if cost == 1:
			toRet = 10
		if cost == 2:
			toRet = 14
		if (nodeB[0], nodeB[1]) in self.traps:
				toRet += self.traps[(nodeB[0], nodeB[1])].getPathingHeuristic(unit)
		return toRet
		
	def getShortestPath(self, start, target, radius, unit, checkForTraps = False, costFunc = None):
		if costFunc is None:
			if checkForTraps:
				costFunc = self.getCostWithTraps
			else:
				costFunc = self.getCost
		#if ((start[0], start[1]), (target[0], target[1])) in self.cachedPaths:
		#	return self.cachedPaths[((start[0], start[1]), (target[0], target[1]))]
		finish = target
		#walkable = self.createWalkableGrid(chars)
		closedSet = {}
		openSet = {(start[0], start[1]):[0,self.calcH(start,finish),None]}
		closest = (start[0], start[1])
		while openSet:
			curr = self.getLowest(openSet)
			closedSet[curr] = openSet[curr]
			if closedSet[closest][1] > closedSet[curr][1]:
				closest = curr
			if distance(curr, finish) <= radius:
				return self.reconstruct(curr,closedSet)
			del openSet[curr]
			for y in [(curr[0] + 1, curr[1] + 1),(curr[0], curr[1] + 1),(curr[0] - 1, curr[1] + 1),
								(curr[0] + 1, curr[1]    )                       ,(curr[0] - 1, curr[1]    ),
								(curr[0] + 1, curr[1] - 1),(curr[0], curr[1] - 1),(curr[0] - 1, curr[1] - 1)]:
				if self.canMoveThrough(y, unit):
					if y in closedSet:
						if closedSet[y][0] > closedSet[curr][0] + costFunc(self, curr, y, unit):
							closedSet[y][0] = closedSet[curr][0] + costFunc(self, curr, y, unit)
							closedSet[y][2] = curr
					elif y not in openSet:
						openSet[y] = [closedSet[curr][0] + costFunc(self, curr, y, unit), self.calcH(y, finish), curr]
					elif y in openSet:
						if openSet[y][0] > closedSet[curr][0] + + costFunc(self, curr, y, unit):
							openSet[y][0] = closedSet[curr][0] + costFunc(self, curr, y, unit)
							openSet[y][2] = curr
		return self.reconstruct(closest,closedSet)
		
	def calcH(self,node,goal):
		diagDist = min(abs(node[0] - goal[0]), abs(node[1] - goal[1]))
		straightDist = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
		return 14 * diagDist + 10 * (straightDist - diagDist * 2)
		
	def getLowest(self, set):
		lowest = (99999, 99999)
		toRet = 0
		for i in set:
			currScore = set[i][0] + set[i][1]
			if lowest[0] + lowest[1] > currScore:
				lowest = (set[i][0], set[i][1])
				toRet = i
			if lowest[0] + lowest[1] == currScore and lowest[1] > set[i][1]:
					lowest = (set[i][0], set[i][1])
					toRet = i	
		return toRet
		
	def reconstruct(self,tail,set):
		if set[tail][2] != None:
			return [tail] + self.reconstruct(set[tail][2],set)
		else:
			return []
		
def canMoveThrough(terrain):
	return terrain not in [1, 9] #in [0, 2, 3, 4, 5, 8]
	
def canSeeThrough(terrain):
	return terrain not in [1]
	
def getTerrainSpeedMods(unit, tileset, terrain):
	if int(tileset) == 1 and terrain in [0, 2] or int(tileset) == 0 and terrain in [2]:
		return TERRAINSPEEDMODS[int(tileset)][terrain] + (1 - TERRAINSPEEDMODS[int(tileset)][terrain]) * (unit.getKeyword("WaterWalking"))
	if 0 <= int(tileset) < len(TERRAINSPEEDMODS) and 0 <= terrain < len(TERRAINSPEEDMODS[int(tileset)]):
		return TERRAINSPEEDMODS[int(tileset)][terrain]
	return 1
	
def isWater(terrain):
	return terrain in [2]
	
def isIce(terrain):
	return terrain in [5]

def isSpawner(terrain):
	return terrain in []
	
def isInactiveSpawner(terrain):
	return terrain in []
	
def isExitPortal(terrain):
	return terrain in []

def distance(p1,p2):
	return max(abs(p1[0] - p2[0]),abs(p1[1] - p2[1]))

def getAtCoord(grid, coords):
		if 0 <= int(coords[1]) < len(grid) and 0 <= int(coords[0]) < len(grid[int(coords[1])]):
			return grid[int(coords[1])][int(coords[0])]
		return 1
		
def isStreamingDoor(trap):
	if trap.TrapId in [PTRS["TRAPTYPES"].STREAMINGDOOR]:
		return True
	return False
		
loadTilesetMap(tilesetMap)
loadTerrainPics(terrainPics)
	
#PTRS["TERRAIN"] = Terrain(False)