import Effects, pickle, sys, time, mazeGen
import Code.Engine.Traps as Traps
import Code.Units.Equipment as Equipment
from Globals import *
from math import e
RIGHTWALL = 1
BOTWALL = 2
LEFTWALL = 4
TOPWALL = 8	

#GENERATOR CONSTANTS
STAIRCHANCE = 0.1
ROOMDOORCHANCE = 0.7
TWODOORCHANCE = 0.2
WATERDISTANCES = [3, 15, 20, 30]
LAVADISTANCES = [1, 10, 30, 40]
NOSHOWCLIMATEDISTANCE = 0.5 # If the climate level is less than this, it will not display the 'climate tile'

TREASURECHANCE = 0.1
ITEMCHANCE = 0.3
TRAPCHANCE = 0.0
ENEMYSPAWNCHANCE = 0.9

MAXROOMSIZE = 100
ROOMSIZEMOD = 1#Roomsize * RoomSizeMod = unit group size budget
HALLWAYSIZEMOD = 1

RIVERSIZEDECREASE = 0.1
RIVERSIZESTART = 6
RIVERSPLITCHANCE = 0.05
RIVERSPLITSIZEDECREASE = 1

ROOMSLEEPDELAY = DOORHOLDTIME - 1

GENERATEMAZEMODE = True
"""-- Climate Idea --
	Use a growth style algorithm to "grow" climate zones.

	Start with a blank grid with some climate "seeds"

	.......W.....
	...H.........
	........S....
	...W....W...S

	W - water
	H - Heat
	S - Sand

	Based on the parameters, each climate type has a chance to "grow" each iteration.
	They can only grow to an empty space.

	-- Advanced --
	What happens when two climate zones collide?  If we have:
	WWW
	WSW
	WWW
	The S should obviously be starved out of existance..."""
class ClimateStruct:
	def __init__(self, size=(50,50)):
		self.tiles = []
		for i in range(size[1]):
			self.tiles += [["."] * size[0]]
			
		self.size = size
		#0 - Grassland, 1 - Wetland, 2 - Darkland
		choiceList = [[1, "0"], [1, "1"], [0.5, "2"]]
		normalize(choiceList)
		for i in range(15):
			tile = (random.randint(0, size[0] - 1), random.randint(0, size[1] - 1))
			type = randFromNormalizedList(choiceList)
			self.tiles[tile[1]][tile[0]] = type
			
	def getTile(self, pos):
		y = min(max(pos[1], 0), len(self.tiles) - 1)
		x = min(max(pos[0], 0), len(self.tiles[0]) - 1)
		return self.tiles[y][x]
			
	def iterate(self):
		newTiles = []
		climateDist = 1
		neighbourUtopia = 5
		maxDist = dist([climateDist, climateDist], [0, 0]) ** 2 + 1
		emptyTile = False
		for y in range(self.size[1]):
			newTiles += [[]]
			for x in range(self.size[0]):
				possibleClimates = []
				numNeighbours = 0
				currTile = self.getTile([x, y])
				for xOff in range(-climateDist, climateDist + 1):
					for yOff in range(-climateDist, climateDist + 1):
						xCheck = x + xOff
						yCheck = y + yOff
						tileAt = self.getTile([xCheck, yCheck])
						if tileAt != ".":
							possibleClimates += [[maxDist - dist([xOff, yOff], [0, 0]) ** 2, tileAt]]
							if tileAt == currTile:
								numNeighbours += 1
				if numNeighbours >= neighbourUtopia:
					newTiles[y] += currTile
				elif possibleClimates:
					normalize(possibleClimates)
					newTiles[y] += randFromNormalizedList(possibleClimates)
				else:
					newTiles[y] += "."
					emptyTile = True
		self.tiles = newTiles
		return not emptyTile
		
	def generate(self):
		doneCount = 0
		while doneCount <= 4:
			if self.iterate():
				doneCount += 1
			
	def __str__(self):
		result = ""
		y = 0
		for i in self.tiles:
			y += 1
			x = 0
			for j in i:
				x += 1
				if x == 21 == y:
					result += "*"
				else:
					result += j
			result += "\n"
		return result
		
class RoadStruct:
	MaxRoadDistance = 50
	MaxRoadsPerNode = 3
	RoadDirections = [[0, -1], [1, 0], [0, 1], [-1, 0]]
	def __init__(self, size=(50,50), majorNodes = []):
		self.tiles = []
		for i in range(size[1]):
			self.tiles += [[0] * size[0]]
		self.size = size
		self.majorNodes = [p for p in majorNodes]
			
	def getTile(self, pos):
		if 0 <= pos[1] < self.size[1] and 0 <= pos[0] < self.size[0]:
			return self.tiles[pos[1]][pos[0]]
		return 0
			
	def isRoadAdjacent(self, pos, ignoreDirection = [0, 0]):
		for d in RoadDirections:
			if self.getTile((pos[0] + d[0], pos[1] + d[1])) != "." and (d[0] != ignoreDirection[0] or d[1] != ignoreDirection[1]):
				return True
		return False
		
	def inBounds(self, pos):
		if 0 <= pos[0] < self.size[0] and 0 <= pos[1] < self.size[1]:
			return True
		return False
		
	def generate(self):
		nodesLeft = [k for k in self.majorNodes]
		while len(nodesLeft) > 1:
			random.shuffle(nodesLeft)
			while nodesLeft and nodesLeft[0][1] <= 0:
				del nodesLeft[0]
			if nodesLeft and nodesLeft[0][1] > 0:
				p = nodesLeft[0]
				foundOne = False
				for p2 in nodesLeft:
					if p is not p2 and p2[1] > 0 and p[1] > 0 and dist(p[0], p2[0]) <= self.MaxRoadDistance:
						foundOne = True
						prev = p[0]
						nodesLeft[0][1] -= 1
						p2[1] -= 1
						for square in raytrace(p[0], p2[0]):
							dirs = (square[1] < prev[1]) * 1 + (square[0] > prev[0]) * 2 + (square[1] > prev[1]) * 4 + (square[0] < prev[0]) * 8
							self.tiles[prev[1]][prev[0]] = self.tiles[prev[1]][prev[0]] | dirs
							dirs = (square[1] > prev[1]) * 1 + (square[0] < prev[0]) * 2 + (square[1] < prev[1]) * 4 + (square[0] > prev[0]) * 8
							self.tiles[square[1]][square[0]] = self.tiles[square[1]][square[0]] | dirs
							prev = square
						dirs = (p2[0][1] < prev[1]) * 1 + (p2[0][0] > prev[0]) * 2 + (p2[0][1] > prev[1]) * 4 + (p2[0][0] < prev[0]) * 8
						self.tiles[p2[0][1]][p2[0][0]] = self.tiles[p2[0][1]][p2[0][0]] | dirs
				if not foundOne:
					nodesLeft[0][1] -= 1
			
	def __str__(self):
		result = ""
		for i in self.tiles:
			for j in i:
				result += hex(j)[2]
			result += "\n"
		return result
		
class DungeonGrid:
	def __init__(self, size, floor=1):
		from Code.Units.Stats import loadAllEnemies
		loadAllEnemies(floor)
		self.size = size
		self.doors = {}
		self.riverTiles = {}
		self.climateGrid = None
		self.roadGrid = None
		self.majorNodes = {}
		self.resetGrid()
		self.rooms = {}
		self.roomsToUpdate = []
		self.floor = floor
		self.toStream = []
		
	def saveToFile(self):
		pickle.dump(self, open(os.path.join("Profiles", "Dungeons", "Floor"+str(self.floor)+".dng"), "wb"))
		#t = GetTerrain(self.floor)
		#t.saveToFile()
		
	def update(self):
		r = 0
		while r < len(self.roomsToUpdate):
			if self.roomsToUpdate[r].update():
				r += 1
				
		for u in PTRS["UNITS"].getPlayers():
			gPos = posToDungeonGrid(u.getPos())
			if gPos in self.rooms:
				self.rooms[gPos].wakeUp()
				if LOADBYPROXIMITY:
					for dir in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
						targPos = (gPos[0] + dir[0], gPos[1] + dir[1])
						if gPos in self.doors:
							foundIt = False
							for d in self.doors[gPos]:
								if d[0] == dir[0] and d[1] == dir[1]:
									foundIt = True
									break
							if foundIt:
								if targPos in self.rooms and GetTerrain(self.floor).getAtCoord(dungeonGridToCoords(targPos)) != 9:
									self.rooms[targPos].wakeUp()
								else:
									self.streamPiece(targPos, initialTile = False, isRoom=(not self.rooms[gPos].isRoom))
					
	def roomWakingUp(self, room):
		self.roomsToUpdate += [room]
		
	def roomGoingToSleep(self, room):
		self.roomsToUpdate.remove(room)
				
	def wakeUpRoom(self, gridCoord):
		if gridCoord in self.rooms:
			self.rooms[gridCoord].wakeUp()
			
	def getRandomPositionInRoom(self, startPos):
		gridPos = posToDungeonGrid(startPos)
		if gridPos in self.rooms:
			return self.rooms[gridPos].getRandomPosition()
		return startPos
		
	def getRoom(self, gridPos):
		if gridPos in self.rooms:
			return self.rooms[gridPos]
		return None
	
	def resetGrid(self):
		self.grid = []
		self.walls = []
		self.doors = {}
		self.riverTiles = {}
		self.majorNodes = {}
		self.climateGrid = ClimateStruct((self.size[0], self.size[1]))
		self.climateGrid.generate()
		self.roadGrid = RoadStruct((self.size[0], self.size[1]), [[pos, self.majorNodes[pos]["maxRoads"]] for pos in self.majorNodes])
		#self.roadGrid.generate()
		
		for y in range(self.size[1]):
			self.grid += [[]]
			self.walls += [[]]
			for x in range(self.size[0]):
				self.grid[y] += [1]
				self.walls[y] += [0]
				
		if GENERATEMAZEMODE:
			self.maze = mazeGen.createGrid(self.size[0], self.size[1])
			self.createMazeRooms()
			seeds = [[STREAMSTARTPOS[0], STREAMSTARTPOS[1]]]
			mazeGen.createMaze(seeds, self.maze)
			#mazeGen.transformToBraidMaze(self.maze)
			mazeGen.printMaze(self.maze)
			
	def createMazeRooms(self):
		self.majorNodes[(STREAMSTARTPOS[0], STREAMSTARTPOS[1])] = {"type":"hub", "maxRoads":4}
		sectorsToGenerate = 5
		sectorSizeY = len(self.maze) / float(sectorsToGenerate)
		sectorSizeX = len(self.maze[0]) / float(sectorsToGenerate)
		for x in range(sectorsToGenerate):
			for y in range(sectorsToGenerate):
				offsetX = 2
				offsetY = 2
				curPos = [int(sectorSizeX * x + offsetX), int(sectorSizeY * y + offsetY)]
				size = [int(sectorSizeX - offsetX - 2), int(sectorSizeY - offsetY - 2)]
				if not (curPos[0] <= STREAMSTARTPOS[0] <= curPos[0] + size[0] and curPos[1] <= STREAMSTARTPOS[1] <= curPos[1] + size[1]):
					tiles = mazeGen.addRoom(curPos[0], curPos[1], size[0], size[1], self.maze)
					if tiles:
						nodePos = random.choice(tiles)
						self.createMajorNode((int(nodePos[0]), int(nodePos[1])))
					
	def createMajorNode(self, pos):
		randChoice = random.randint(0, 1)
		if randChoice == 0:
			self.majorNodes[pos] = self.createShrine(pos)
		else:
			self.majorNodes[pos] = self.createBoss(pos)
		
	def createBoss(self, pos):
		toRet = {"type":"boss", "maxRoads":0}
		return toRet
		
	def createShrine(self, gridPos):
		climateAt = self.climateGrid.getTile(gridPos)
		toRet = {}
		if int(climateAt) == 0:
			toRet = {"type":"shrine", "god":"Nature", "maxRoads":1}
		elif int(climateAt) == 1:
			toRet = {"type":"shrine", "god":"Water", "maxRoads":3}
		elif int(climateAt) == 2:
			toRet = {"type":"shrine", "god":"Death", "maxRoads":3}
		else:
			print int(climateAt)
		return toRet
					
	def transformMaze(self, value):
		if value == mazeGen.WALL:
			return 1
		return 0

	def getWidth(self):
		return len(self.grid[0])
		
	def getHeight(self):
		return len(self.grid)
		
	def getMaze(self, coord):
		if 0 <= coord[1] < len(self.maze) and 0 <= coord[0] < len(self.maze[coord[1]]):
			return self.maze[coord[1]][coord[0]]
		return mazeMgr.WALL
				
	def getGrid(self, coord):
		if 0 <= coord[1] < len(self.grid) and 0 <= coord[0] < len(self.grid[coord[1]]):
			return self.grid[coord[1]][coord[0]]
		return 1
		
	def getWall(self, coord):
		if 0 <= coord[1] < len(self.walls) and 0 <= coord[0] < len(self.walls[coord[1]]):
			return self.walls[coord[1]][coord[0]]
		return 0
		
	def setGrid(self, coord, new):
		if 0 <= coord[1] < len(self.grid) and 0 <= coord[0] < len(self.grid[coord[1]]):
			self.grid[coord[1]][coord[0]] = new
		
	def setWall(self, coord, new):
		if 0 <= coord[1] < len(self.walls) and 0 <= coord[0] < len(self.walls[coord[1]]):
			self.walls[coord[1]][coord[0]] |= new
			
	def isValidPlaceForPiece(self, piece, pos):
		if 0 <= pos[0] < self.getWidth() - piece.getWidth() and 0 <= pos[1] < self.getHeight() - piece.getHeight():
			for px in range(piece.getWidth()):
				for py in range(piece.getHeight()):
					if self.getGrid((pos[0] + px, pos[1] + py)) != 1 and piece.getGrid((px, py)) != 1:
						return False
			return True
		return False
			
	def findRandomSpotForPiece(self, piece):
		for y in range(self.getHeight() - piece.getHeight()):
			for x in range(self.getWidth() - piece.getWidth()):
				if self.isValidPlaceForPiece(piece, (x, y)):
					return (x, y)
		return ()
		
	def addRightDoors(self, topLeft, piece, room, streamed = False):
		if not ALLDOORSMODE and not GENERATEMAZEMODE and random.random() >= ROOMDOORCHANCE:
			return
		
		validRightDoors = []
		for y in range(len(piece.grid)):
			x = len(piece.grid[y]) - 1
			while x >= 0 and piece.getGrid((x, y)) != 0:
				x -= 1
			if GENERATEMAZEMODE:
				if mazeGen.getTile(self.maze, (topLeft[0] + x + 1, topLeft[1] + y)) != mazeGen.WALL and \
					(x >= 0 and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x + 1, topLeft[1] + y)) == 1):
					validRightDoors += [(topLeft[0] + x, topLeft[1] + y)]
			else:
				if (not streamed and (x >= 0 and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x + 1, topLeft[1] + y)) == 0)) or \
					 (streamed and (x >= 0 and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x + 1, topLeft[1] + y)) == 1) and 0 < topLeft[0] + x < self.getWidth() - 1 and 0 < topLeft[1] + y < self.getHeight() - 1):
					validRightDoors += [(topLeft[0] + x, topLeft[1] + y)]
				
		#Now actually add them.
		if ALLDOORSMODE:
			self.addRandomValidDoor(room, validRightDoors, (1, 0), 50)
		else:
			self.addRandomValidDoor(room, validRightDoors, (1, 0), (random.random() < TWODOORCHANCE) + 1)
				
	def addLeftDoors(self, topLeft, piece, room, streamed = False):
		if not ALLDOORSMODE and not GENERATEMAZEMODE and random.random() >= ROOMDOORCHANCE:
			return
		
		validLeftDoors = []
		#LEFT
		for y in range(len(piece.grid)):
			##print "LEFT: ", 0, y, piece.grid[y][0], self.getGrid((topLeft[0] - 1, topLeft[1] + y))
			x = 0
			while x < len(piece.grid[y]) and piece.getGrid((x, y)) != 0:
				x += 1
			if GENERATEMAZEMODE:
				if mazeGen.getTile(self.maze, (topLeft[0] + x - 1, topLeft[1] + y)) != mazeGen.WALL and \
					(x < len(piece.grid[y]) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] - 1 + x, topLeft[1] + y)) == 1):
					validLeftDoors += [(topLeft[0] + x, topLeft[1] + y)]
			else:
				if (not streamed and (x < len(piece.grid[y]) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] - 1 + x, topLeft[1] + y)) == 0)) or \
					(streamed and (x < len(piece.grid[y]) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] - 1 + x, topLeft[1] + y)) == 1) and 0 < topLeft[0] + x < self.getWidth() - 1 and 0 < topLeft[1] + y < self.getHeight() - 1):
					validLeftDoors += [(topLeft[0] + x, topLeft[1] + y)]
		if ALLDOORSMODE or GENERATEMAZEMODE:
			self.addRandomValidDoor(room, validLeftDoors, (-1, 0), 50)
		else:
			self.addRandomValidDoor(room, validLeftDoors, (-1, 0), (random.random() < TWODOORCHANCE) + 1)
		
	def addTopDoors(self, topLeft, piece, room, streamed = False):
		if not ALLDOORSMODE and not GENERATEMAZEMODE and random.random() >= ROOMDOORCHANCE:
			return
		validTopDoors = []
		#TOP
		for x in range(len(piece.grid[0])):
			##print "TOP: ", x, 0, piece.grid[0][x], self.getGrid((topLeft[0] + x, topLeft[1] - 1))
			y = 0
			while y < len(piece.grid) and piece.getGrid((x, y)) != 0:
				y += 1
			if GENERATEMAZEMODE:
				if mazeGen.getTile(self.maze, (topLeft[0] + x, topLeft[1] + y - 1)) != mazeGen.WALL and \
					(y < len(piece.grid) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] - 1 + y)) == 1):
					validTopDoors += [(topLeft[0] + x, topLeft[1] + y)]
			else:
				if (not streamed and (y < len(piece.grid) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] - 1 + y)) == 0)) or \
					(streamed and (y < len(piece.grid) and piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] - 1 + y)) == 1) and 0 < topLeft[0] + x < self.getWidth() - 1 and 0 < topLeft[1] + y < self.getHeight() - 1):
					validTopDoors += [(topLeft[0] + x, topLeft[1] + y)]
		if ALLDOORSMODE or GENERATEMAZEMODE:
			self.addRandomValidDoor(room, validTopDoors, (0, -1), 50)
		else:
			self.addRandomValidDoor(room, validTopDoors, (0, -1), (random.random() < TWODOORCHANCE) + 1)
		
	def addBottomDoors(self, topLeft, piece, room, streamed = False):
		if not ALLDOORSMODE and not GENERATEMAZEMODE and  random.random() >= ROOMDOORCHANCE:
			return
		validBottomDoors = []
					
		#BOTTOM
		for x in range(len(piece.grid[0])):
			##print "BOTTOM: ", x, len(piece.grid) - 1, piece.grid[len(piece.grid) - 1][x], self.getGrid((topLeft[0] + x, topLeft[1] + len(piece.grid)))
			y = len(piece.grid) - 1
			while y >= 0 and piece.getGrid((x, y)) != 0:
				y -= 1
			if GENERATEMAZEMODE:
				if mazeGen.getTile(self.maze, (topLeft[0] + x, topLeft[1] + y + 1)) != mazeGen.WALL and \
					(piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] + y + 1)) == 1):
					validBottomDoors += [(topLeft[0] + x, topLeft[1] + y)]
			else:
				if (not streamed and (piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] + y + 1)) == 0)) or \
					(streamed and (piece.grid[y][x] == 0 and self.getGrid((topLeft[0] + x, topLeft[1] + y + 1)) == 1) and 0 < topLeft[0] + x < self.getWidth() - 1 and 0 < topLeft[1] + y < self.getHeight() - 1):
					validBottomDoors += [(topLeft[0] + x, topLeft[1] + y)]
		if ALLDOORSMODE or GENERATEMAZEMODE:
			self.addRandomValidDoor(room, validBottomDoors, (0, 1), 50)
		else:
			self.addRandomValidDoor(room, validBottomDoors, (0, 1), (random.random() < TWODOORCHANCE) + 1)
	
	def addRandomValidDoor(self, room, validDoors, doorDirection, numDoors = 1):
		i = numDoors
		while i > 0 and validDoors:
			i -= 1
			l = random.randint(0, len(validDoors) - 1)
			if validDoors[l] not in self.doors:
				self.doors[validDoors[l]] = []
			self.doors[validDoors[l]] += [(doorDirection[0], doorDirection[1])]
			
			otherSide = (validDoors[l][0] + doorDirection[0], validDoors[l][1] + doorDirection[1])
			if otherSide not in self.doors:
				self.doors[otherSide] = []
			self.doors[otherSide] += [(-doorDirection[0], -doorDirection[1])]
			
			del validDoors[l]
		
	def placePieceAt(self, topLeft, piece, room, streamed = False):
		if len(topLeft) == 2:
			for y in range(len(piece.grid)):
				for x in range(len(piece.grid[y])):
					if self.getGrid((topLeft[0] + x, topLeft[1] + y)) == 1:
						self.setGrid((topLeft[0] + x, topLeft[1] + y), piece.getGrid((x, y)))
						
			if piece.getWidth() > 1 or piece.getHeight() > 1 or GENERATEMAZEMODE:
				self.addLeftDoors(topLeft, piece, room, streamed)
				self.addRightDoors(topLeft, piece, room, streamed)
				self.addTopDoors(topLeft, piece, room, streamed)
				self.addBottomDoors(topLeft, piece, room, streamed)
					
			for p in room.spawnableTiles:
				dirs = getDirectionList(self.roadGrid.getTile(p))
				for dir in dirs:
					if self.getRoom((p[0] + dir[0], p[1] + dir[1])) != room:
						self.addRandomValidDoor(room, [(p[0], p[1])], dir, 1)
					
			for y in range(len(piece.walls)):
				for x in range(len(piece.walls[y])):
					self.setWall((topLeft[0] + x, topLeft[1] + y), piece.getWall((x, y)))
					
	def findStreamingSpotForPiece(self, streamPos, piece):
		for y in range(piece.getHeight()):
			for x in range(len(piece.grid[y])):
				if piece.grid[y][x] == 0:
					p = (streamPos[0] - x, streamPos[1] - y)
					if self.isValidPlaceForPiece(piece, p):
						return (streamPos[0] - x, streamPos[1] - y)
					
	def streamPiece(self, streamPos, initialTile = False, isRoom=False):
		self.toStream += [[streamPos, initialTile, isRoom]]
	
	def streamQueuedPieces(self):
		while self.toStream:
			self.streamQueuedPiece(*self.toStream[0])
			del self.toStream[0]
			
	def streamQueuedPiece(self, streamPos, initialTile = False, isRoom=False):
		if streamPos not in self.rooms:
			if GENERATEMAZEMODE:
				pos, piece = getFittedDungeonPiece(self, streamPos, self.maze, self.grid)
			else:
				piece = getRandomDungeonPiece(self, isRoom)
				pos = self.findStreamingSpotForPiece(streamPos, piece)
				toAttempt = 3
				while not pos and toAttempt > 0:
					toAttempt -= 1
					piece = getRandomDungeonPiece(self, isRoom)
					pos = self.findStreamingSpotForPiece(streamPos, piece)
				if not pos:
					if "OnePiece" not in loadedPieces:
						loadedPieces["OnePiece"] = DungeonPiece("OnePiece.txt")
					piece = loadedPieces["OnePiece"]
					pos = streamPos
			room = DungeonRoom(pos, piece, initialTile, self.floor, isRoom = isRoom, forceEmpty = (len(self.rooms) < 1) or initialTile)
			for square in room.spawnableTiles:
				majorNodeType = self.getMajorNodeType((square[0], square[1]))
				if majorNodeType == "boss":
					room.isBossRoom = True
			for x in range(piece.getWidth()):
				for y in range(piece.getHeight()):
					if piece.getGrid((x, y)) == 0:
						self.rooms[(pos[0] + x, pos[1] + y)] = room
			self.placePieceAt(pos, piece, room, True)
			self.roomsToUpdate += [room]
		elif GetTerrain(self.floor).getAtCoord(dungeonGridToCoords(streamPos)) == 9:
			room = self.rooms[streamPos]
			pos = room.pos
			piece = room.piece
		else:
			return None
		GetTerrain(self.floor).streamDungeonGrid(self, room, piece, DUNGEONBOXSIZE)
		room.spawnEncounter()
		return room
			
	def isWaterArea(self, pos):
		if (pos[0], pos[1]) in self.riverTiles:
			return True
		return False
				
	def isRiverTile(self, pos, coords, maxDist = False):
		if pos in self.riverTiles:
			isWaterTile = False
			center = (pos[0] * (DUNGEONBOXSIZE[0] + 1) + (DUNGEONBOXSIZE[0] + 1) / 2.0,
								pos[1] * (DUNGEONBOXSIZE[1] + 1) + (DUNGEONBOXSIZE[1] + 1) / 2.0)
			#River running left
			if coords[0] <= center[0] and (pos[0] - 1, pos[1]) in self.riverTiles:
				rt = self.riverTiles[(pos[0], pos[1])] / 2.0
				if min(-rt + 0.5, 0) <= coords[1] - center[1] <= max(rt, 0):
					isWaterTile = True
			#River running right
			elif coords[0] >= center[0] and (pos[0] + 1, pos[1]) in self.riverTiles:
				rt = self.riverTiles[(pos[0], pos[1])] / 2.0
				if min(-rt + 0.5, 0) <= coords[1] - center[1] <= rt:
					isWaterTile = True
			#River running Up
			if coords[1] <= center[1] and (pos[0], pos[1] - 1) in self.riverTiles:
				rt = self.riverTiles[(pos[0], pos[1])] / 2.0
				if min(-rt + 0.5, 0) <= coords[0] - center[0] <= rt:
					isWaterTile = True
			#River running Down
			elif coords[1] >= center[1] and (pos[0], pos[1] + 1) in self.riverTiles:
				rt = self.riverTiles[(pos[0], pos[1])] / 2.0
				if min(-rt + 0.5, 0) <= coords[0] - center[0] <= rt:
					isWaterTile = True
			return isWaterTile
		return False
		
	def getTilesetAt(self, coords, checkAdjacent = True):
		toRet = []
		for d in [[0, 0]] + [[1, 0], [-1, 0], [0, 1], [0, -1]] * (checkAdjacent is not False):
			toRet += [[1, self.climateGrid.getTile((coords[0] + d[0], coords[1] + d[1]))]]
		if toRet:
			normalize(toRet)
			return randFromNormalizedList(toRet)
		return 0
		
	def getRandomWalkableTile(self, pos, coords):
		return 0
		climateAt = self.climateGrid.getTile(pos)
		if climateAt == "0":
			return 5
		elif climateAt == "1":
			return 0
		elif climateAt == "2":
			return 2
		else:
			print "FAILURE!", pos
		return 0

	@staticmethod
	def getCost(TPtr,	nodeA, nodeB, unit):
		cost = abs(nodeA[0] - nodeB[0]) + abs(nodeA[1] - nodeB[1])
		toRet = 100000
		if cost == 1:
			toRet = 10
			toRet += math.fabs(DUNGEONBOXSIZE[0] / 2 - nodeB[0] % (DUNGEONBOXSIZE[0] + 1)) + math.fabs(DUNGEONBOXSIZE[1] / 2 - nodeB[1] % (DUNGEONBOXSIZE[1] + 1))
		return toRet
		
	def setDecorativeTiles(self, TPtr, room, boxSize):
		self.drawDecorations(TPtr, room, boxSize)
		self.drawRoads(TPtr, room, boxSize)
		self.addAllShrines(TPtr, room, boxSize)
		self.addOtherDecor(TPtr, room, boxSize)
		
	def drawDecorations(self, TPtr, room, boxSize):
		#Draw random decorative tiles (water, 'decoration', and 'slowing_decoration'
		for coord in room.decorations:
			decorationType = random.choice([2, 5])
			gridPos = coordsToDungeonGrid(coord)
			tileset = self.getTilesetAt(gridPos, False)
			for x in range(1, (boxSize[0] + 1)):
				for y in range(1, (boxSize[1] + 1)):
					xPos = x + (gridPos[0]) * (boxSize[0] + 1)
					yPos = y + (gridPos[1]) * (boxSize[1] + 1)
					if math.fabs(boxSize[0] / 2 - x + 1) < boxSize[0] / 2 and math.fabs(boxSize[1] / 2 - y + 1) < boxSize[1] / 2 or random.random() <= 0.4:
						if TPtr.getAtCoord([xPos, yPos]) != 1:
							TPtr.setTile([xPos, yPos], [tileset, decorationType, 0])
	
	def addOtherDecor(self, TPtr, room, boxSize):
		for square in room.spawnableTiles:
			numToSpawn = random.randint(1, 4)
			for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
				if self.climateGrid.getTile([square[0] + off[0], square[1] + off[1]]) != self.climateGrid.getTile(square):
					numToSpawn = 0
			for i in range(numToSpawn):
				coord = square[0] * (boxSize[0] + 1) + random.randint(1, boxSize[0]), square[1] * (boxSize[1] + 1) + random.randint(1, boxSize[1])
				if TPtr.getAtCoord(coord) == 0:
					tileset = int(TPtr.getAtCoord(coord, 0))
					if tileset == 0:
						type = random.randint(0, 9)
						if type == 9:
							#coord = (square[0] * (boxSize[0] + 1) + random.randint(1, boxSize[0]), square[1] * (boxSize[1] + 1) + random.randint(1, boxSize[1] - 1))
							foundOne = False
							for t in room.decorObjects:
								if (t.source[0] == coord[0] and (t.source[1] != coord[1] or t.source[1] != coord[1] + 1)):
									foundOne = True
							if not foundOne:
								for x in range(1):
									for y in range(2):
										layer = 2
										solid = (y == 0)
										room.decorObjects += [Traps.Decoration((coord[0] + x, coord[1] - y), room.floor, 9, 1 - y, layer, solid)]
						else:
							room.decorObjects = room.decorObjects + [Traps.Decoration(coord, room.floor, type, 0, 0, False)]
					elif tileset == 1:
						type = random.randint(0, 4)
						room.decorObjects = room.decorObjects + [Traps.Decoration(coord, room.floor, type, 1, 0, False)]
					elif tileset == 2:
						type = random.randint(0, 7)
						if type in [6, 7]:
							#coord = (square[0] * (boxSize[0] + 1) + random.randint(1, boxSize[0]), square[1] * (boxSize[1] + 1) + random.randint(1, boxSize[1] - 1))
							foundOne = False
							for t in room.decorObjects:
								if (t.source[0] == coord[0] and (t.source[1] != coord[1] or t.source[1] != coord[1] + 1)):
									foundOne = True
							if not foundOne:
								for x in range(1):
									for y in range(2):
										layer = 2
										solid = (y == 0)
										room.decorObjects += [Traps.Decoration((coord[0] + x, coord[1] - y), room.floor, type, 3 - y, layer, solid)]
						else:
							room.decorObjects = room.decorObjects + [Traps.Decoration(coord, room.floor, type, 2, 0, False)]
					
	def getMajorNode(self, square):
		if (square[0], square[1]) in self.majorNodes:
			return self.majorNodes[(square[0], square[1])]
		else:
			return {}
			
	def getMajorNodeType(self, square):
		if (square[0], square[1]) in self.majorNodes and "type" in self.majorNodes[(square[0], square[1])]:
			return self.majorNodes[(square[0], square[1])]["type"]
		else:
			return "none"
			
	def addStairs(self, TPtr, room, boxSize):
		for square in room.spawnableTiles:
			if self.getMajorNodeType((square[0], square[1])) == "stairs":
				stairInfo = getMajorNode(self, square)
				self.traps += [Traps.createTrap(stairInfo["coord"], PTRS["TRAPTYPES"].STAIRS, self.floor, [stairInfo["direction"]])]
					
	def addAllShrines(self, TPtr, room, boxSize):
		#Create shrines.
		for square in room.spawnableTiles:
			majorNodeType = self.getMajorNodeType((square[0], square[1]))
			if majorNodeType == "shrine":
				godInfo = self.majorNodes[(square[0], square[1])]
				self.addShrine(TPtr, room, boxSize, square, godInfo)
				
	def addShrine(self, TPtr, room, boxSize, square, godInfo):
		coordTarg = dungeonGridToCoords([square[0], square[1]])
		if godInfo["god"] == "Nature":
			coordTarg = [coordTarg[0] - 1, coordTarg[1] - 2]
			for x in range(3):
				for y in range(4):
					cPos = (coordTarg[0] + x, coordTarg[1] + y)
					solid = False
					if y >= 2:
						solid = True
					layer = 2
					if y >= 3:
						layer = 0
					room.decorObjects += [Traps.Shrine(cPos, room.floor, 0 + x, 0 + y, layer, solid)]
			for x in range(1, (boxSize[0] + 1)):
				for y in range(1, (boxSize[1] + 1)):
					cPos = (square[0] * (boxSize[0] + 1) + x, square[1] * (boxSize[1] + 1) + y)
					if TPtr.getAtCoord(cPos) not in [1]:
						TPtr.setTile(cPos, ["0", 3, 0])
			for x in range(2, (boxSize[0])):
				for y in range(2, (boxSize[1])):
					cPos = (square[0] * (boxSize[0] + 1) + x, square[1] * (boxSize[1] + 1) + y)
					if TPtr.getAtCoord(cPos) not in [1]:
						TPtr.setTile(cPos, ["0", 5, 0])
		elif godInfo["god"] == "Water":
			coordTarg = [coordTarg[0], coordTarg[1] - 1]
			for x in range(1):
				for y in range(2):
					cPos = (coordTarg[0] + x, coordTarg[1] + y)
					solid = False
					if y >= 1:
						solid = True
					layer = 2
					if y >= 1:
						layer = 0
					room.decorObjects += [Traps.Shrine(cPos, room.floor, 3 + x, 0 + y, layer, solid)]
			for x in range(-2, 3):
				for y in range(-2, 4):
					cPos = (coordTarg[0] + x, coordTarg[1] + y)
					if TPtr.getAtCoord(cPos) not in [1]:
						TPtr.setTile(cPos, ["1", 2, 0])
		elif godInfo["god"] == "Death":
			coordTarg = [coordTarg[0], coordTarg[1]]
			for p in [[-1, -1], [-2, -1], [-1, -2],   [1, -1], [1, -2], [2, -1],    [1, 1], [1, 2], [2, 1],    [-1, 1], [-1, 2], [-2, 1]]:
				cPos = (coordTarg[0] + p[0], coordTarg[1] + p[1])
				solid = True
				layer = 0
				room.decorObjects += [Traps.Shrine(cPos, room.floor, 0, 4, layer, solid)]
				TPtr.setTile(cPos, ["2", 0, 0])
		
	def drawRoads(self, TPtr, room, boxSize):
		doors = []
		for p in room.spawnableTiles:
			road = self.roadGrid.getTile(p)
			if road:
				start = dungeonGridToCoords(p)
				dirs = getDirectionList(road)
				tileset = self.getTilesetAt(p, False)
				for dir in dirs:
					curr = start
					while (p[0] * (DUNGEONBOXSIZE[0] + 1) <= curr[0] <= (p[0] + 1) * (DUNGEONBOXSIZE[0] + 1) and
								p[1] * (DUNGEONBOXSIZE[1] + 1) <= curr[1] <= (p[1] + 1) * (DUNGEONBOXSIZE[1] + 1)):
						TPtr.setTile(curr, [tileset, 3, 0])
						curr = [curr[0] + dir[0], curr[1] + dir[1]]
		
class DungeonPiece:
	def __init__(self, streamPos, fileName, dungeon, isRoom=False, forcePieceGrid=None):#pieceGrid, pieceWalls):
		self.isRoom = isRoom
		if GENERATEMAZEMODE and not forcePieceGrid is None:
			self.grid = forcePieceGrid
			self.walls = []
			self.calculateWalls()
		else:
			self.grid = []
			self.walls = []
			self.fileName = fileName
			self.loadFromFile(fileName, isRoom)
		#print fileName
		#print self.grid
		#self.calculateWalls()
						
	def loadFromFile(self, fileName, isRoom=False):
		if fileName == "OnePiece.txt":
			path = os.path.join("Data", "DungeonPieces", fileName)
		elif isRoom:
			path = os.path.join("Data", "DungeonPieces", "Rooms", fileName)
		else:
			path = os.path.join("Data", "DungeonPieces", "Hallways", fileName)
		if os.path.exists(path):
			fileIn = open(path)
			self.grid = []
			line = fileIn.readline()
			while line:
				self.grid += [[]]
				l = line.split()
				for p in l:
					self.grid[len(self.grid) - 1] += [int(p)]
				line = fileIn.readline()
			self.calculateWalls()
		else:
			print "ERROR: DUNGEONPIECE DOES NOT EXIST:", fileName
				
	def calculateWalls(self):
		self.walls = []
		for y in range(len(self.grid)):
			self.walls += [[]]
			for x in range(len(self.grid[y])):
				self.walls[y] += [0]
				if self.getGrid((x, y)) == 0:
					if self.getGrid((x, y + 1)) == 1:
						self.walls[y][x] |= BOTWALL
					if self.getGrid((x, y - 1)) == 1:
						self.walls[y][x] |= TOPWALL
					if self.getGrid((x + 1, y)) == 1:
						self.walls[y][x] |= RIGHTWALL
					if self.getGrid((x - 1, y)) == 1:
						self.walls[y][x] |= LEFTWALL
				else:
					self.walls[y][x] = 0
		
	def getWidth(self):
		return len(self.grid[0])
		
	def getHeight(self):
		return len(self.grid)
		
	def getGrid(self, coord):
		if 0 <= coord[1] < len(self.grid) and 0 <= coord[0] < len(self.grid[coord[1]]):
			return self.grid[coord[1]][coord[0]]
		return 1
		
	def getWall(self, coord):
		if 0 <= coord[1] < len(self.walls) and 0 <= coord[0] < len(self.walls[coord[1]]):
			return self.walls[coord[1]][coord[0]]
		return 1
	
	def rotateOnce(self, recalcWalls = True):
		if recalcWalls:
			self.makeSquare()
		rot2(self.grid)
		if recalcWalls:
			self.trimExtra()
			self.calculateWalls()
	
	def randomlyRotate(self):
		self.makeSquare()
		for i in range(random.randint(0, 3)):
			self.rotateOnce(False)
		self.trimExtra()
		self.calculateWalls()
	
	def makeSquare(self):
		if self.getWidth() > self.getHeight():
			for i in range(self.getWidth() - self.getHeight()):
				self.grid += [[]]
				self.grid[len(self.grid) - 1] += [1 for k in range(self.getWidth())]
		elif self.getHeight() > self.getWidth():
			for i in range(self.getHeight() - self.getWidth()):
				for j in range(self.getHeight()):
					self.grid[j] += [1]
	
	def trimExtra(self):
		#Trim the bottom
		extraHeight = True
		while extraHeight and self.getHeight():
			for x in range(self.getWidth()):
				if self.getGrid((x, self.getHeight() - 1)) == 0:
					extraHeight = False
			if extraHeight:
				del self.grid[len(self.grid) - 1]
				
		#Trim the top
		extraHeight = True
		while extraHeight and self.getHeight():
			for x in range(self.getWidth()):
				if self.getGrid((x, 0)) == 0:
					extraHeight = False
			if extraHeight:
				del self.grid[0]
				
		#Trim the left
		extraWidth = True
		while extraWidth and self.getWidth():
			for y in range(self.getHeight()):
				if self.getGrid((0, y)) == 0:
					extraWidth = False
			if extraWidth:
				for y in range(self.getHeight()):
					del self.grid[y][0]
					
		#Trim the right
		extraWidth = True
		while extraWidth and self.getWidth():
			for y in range(self.getHeight()):
				if self.getGrid((self.getWidth() - 1, y)) == 0:
					extraWidth = False
			w = self.getWidth()
			if extraWidth:
				for y in range(self.getHeight()):
					del self.grid[y][w - 1]
					
class DungeonRoom:
	def __init__(self, topLeft, piece, initialTile, floor, isRoom=False, isStairRoom=False, forceEmpty=False):
		self.isStairRoom = isStairRoom or initialTile or random.random() <= STAIRCHANCE
		self.isRoom = isRoom
		self.isBossRoom = False
		self.encounterInitialized = False
		self.piece = piece
		self.pos = topLeft
		self.timeToSleep = ROOMSLEEPDELAY
		self.floor = floor
		self.spawnableTiles = []
		self.lastSpawn = 0
		self.forceEmpty = forceEmpty
		dunGrid = GetDungeonGrid(self.floor)
		self.climateTypes = None
		for x in range(self.piece.getWidth()):
			for y in range(self.piece.getHeight()):
				if self.piece.getGrid((x, y)) == 0 and \
						0 <= topLeft[0] + x < dunGrid.getWidth() and \
						0 <= topLeft[1] + y < dunGrid.getHeight():
					newTile = (topLeft[0] + x, topLeft[1] + y)
					self.spawnableTiles += [newTile]
		
		self.decorations = []
		for x in range(len(self.spawnableTiles) / 3):
			self.decorations += [dungeonGridToCoords(random.choice(self.spawnableTiles))]
		total = 0
		self.units = []
		self.traps = []
		self.decorObjects = []
		self.neighbours = []
			
	def getUnits(self):
		return [k for k in self.units]
			
	def allUnitsDead(self):
		for u in self.units:
			if not u.isDead():
				return False
		return True
			
	def pickEnemyGroup(self, maxSize, climateType):
		if self.floor not in enemyList:
			loadEnemyList(self.floor)
		if enemyList[self.floor]:
			validEnemies = []
			for enemyGroup in enemyList[self.floor]:
				if enemyGroup.groupSize <= maxSize and enemyGroup.isBoss == self.isBossRoom and str(climateType) in enemyGroup.climateTypes:
					validEnemies += [[enemyGroup.chance, enemyGroup]]
			if validEnemies:
				normalize(validEnemies)
				return randFromNormalizedList(validEnemies)
		return None
		
	def createUnitGroup(self, group, tileToSpawnIn = []):
		toSpawn = group.enemyList
		for unitToSpawn in toSpawn:
			numToSpawn = random.randint(unitToSpawn.min, unitToSpawn.max + 1)
			for i in range(numToSpawn):
				spawnPos = self.getRandomPosition(tileToSpawnIn)
				unit = PTRS["UNITS"].createEnemyUnit(spawnPos, self.floor, self, unitToSpawn.name)
				unit.sleep()
				self.units += [unit]
		return group.groupSize
		
	def getClimateType(self):
		if self.climateTypes == None:
			self.climateTypes = []
			for s in self.spawnableTiles:
				self.climateTypes += [GetDungeonGrid(self.floor).climateGrid.getTile(s)]
		return random.choice(self.climateTypes)
				
	def initializeUnits(self):
		if self.isBossRoom:
			climateType = self.getClimateType()
			enemyGroup = self.pickEnemyGroup(len(self.spawnableTiles), climateType)
			if enemyGroup:
				self.createUnitGroup(enemyGroup)
		else:
			climateType = self.getClimateType()
			sizeLeft = len(self.spawnableTiles)
			if sizeLeft > 5:
				sizeLeft = 5 + (sizeLeft - 5) / 3.0
			enemyGroup = self.pickEnemyGroup(sizeLeft, climateType)
			while enemyGroup:
				self.createUnitGroup(enemyGroup)
				sizeLeft -= enemyGroup.groupSize
				enemyGroup = self.pickEnemyGroup(sizeLeft, climateType)
				
	def initializeTraps(self):
		#TODO: Remove treasure / traps / stairs when reloading.
		if self.isStairRoom:
			pos = self.getRandomPosition()
			coords = posToCoords(pos)
			if GetTerrain(self.floor).getAtCoord(coords) != 1 and coords not in GetTerrain(self.floor).traps:
				directions = []
				if self.floor > 1:
					directions += [Traps.Directions.UP]
				if self.floor < NUMFLOORS:
					directions += [Traps.Directions.DOWN]
				if directions:
					direction = random.choice(directions)
					self.traps += [Traps.createTrap(coords, PTRS["TRAPTYPES"].STAIRS, self.floor, [direction])]
				
		if random.random() <= TREASURECHANCE:
			pos = self.getRandomPosition()
			self.traps += [Traps.createTrap(posToCoords(pos), PTRS["TRAPTYPES"].TREASURE, self.floor, ["-d", self, "-t", random.randint(0, 2)])]
			
		if random.random() <= TRAPCHANCE:
			for i in range(random.randint(5, 10)):
				toDo = 1
				if random.random() <= 0.2:
					toDo = 2
				pos = self.getRandomPosition()
				for x in range(toDo):
					for y in range(toDo):
						coords = posToCoords(pos)
						coords = (coords[0] + x, coords[1] + y)
						if GetTerrain(self.floor).getAtCoord(coords) != 1 and coords not in GetTerrain(self.floor).traps:
							self.traps += [Traps.createTrap(coords, PTRS["TRAPTYPES"].FLOORSPIKETRAP, self.floor, ["-d", self, "-t", random.randint(0, 2)])]
		
	def initializeEncounter(self):
		self.encounterInitialized = True
		self.units = []		
		self.traps = []
		self.decorObjects = []
		self.lastSpawn = int(time.time())
		if not self.spawnableTiles or self.forceEmpty:
			return
			
		self.initializeUnits()
		self.initializeTraps()
							
	def treasureCollected(self, chestType, unit):
		#unit = random.choice(PTRS["UNITS"].getPlayers())
		unit.giveTreasure(Equipment.getRandomTreasure("F" + str(self.floor) + "Chest" + str(chestType)))
			
	def getRandomPosition(self, selectFrom = []):
		if selectFrom:
			randGridPos = random.choice(selectFrom)
		else:
			randGridPos = random.choice(self.spawnableTiles)
		randTile = [random.randint(randGridPos[0] * (DUNGEONBOXSIZE[0] + 1) + 1, (randGridPos[0] + 1) * (DUNGEONBOXSIZE[0] + 1) - 1),
								 random.randint(randGridPos[1] * (DUNGEONBOXSIZE[1] + 1) + 1, (randGridPos[1] + 1) * (DUNGEONBOXSIZE[1] + 1) - 1)]
		randPos = (randTile[0] * TILESIZE[0] + random.randint(1, TILESIZE[0] - 1), 
							 randTile[1] * TILESIZE[1] + random.randint(1, TILESIZE[1] - 1))
		return randPos
			
	def spawnEncounter(self):
		if not self.encounterInitialized and not self.forceEmpty:
			self.initializeEncounter()
		if not self.forceEmpty:
			for u in self.units:
				u.wakeUp()
				PTRS["UNITS"].wakeUpUnit(u)
			
		for t in self.traps:
			t.wakeUp()
			GetTerrain(self.floor).addTrapTriggerSource(t.source, self.floor)
			GetTerrain(self.floor).addTrap(t)
		
		for d in self.decorObjects:
			GetTerrain(self.floor).addTrap(d)
		
		#return (int((coords[0] - 1) / (DUNGEONBOXSIZE[0] + 1)), int((coords[1] - 1) / (DUNGEONBOXSIZE[1] + 1)))
		
	def update(self):
		self.timeToSleep -= 1
		if self.timeToSleep <= 0:
			self.sleep()
			return False
		return True
		
	def wakeUp(self, recurse=True):
		if self.timeToSleep <= 0:
			self.spawnEncounter()
			GetDungeonGrid(self.floor).roomWakingUp(self)
		else:
			pass
		self.timeToSleep = ROOMSLEEPDELAY
		
	def sleep(self):
		for u in self.units:
			u.sleep()
		for t in self.traps:
			t.sleep()
			GetTerrain(self.floor).removeTrapDestination(t.source, t.source)
		for d in self.decorObjects:
			GetTerrain(self.floor).removeTrapDestination(d.source, d.source)
		GetDungeonGrid(self.floor).roomGoingToSleep(self)
		
	def readyToSleep(self):
		return self.timeToSleep <= 0

pieces = [file for file in os.listdir(os.path.join("Data", "DungeonPieces")) if file[len(file) - 3:] == ".dp"]
rooms = [file for file in os.listdir(os.path.join("Data", "DungeonPieces", "Rooms")) if file[len(file) - 3:] == ".dp"]
hallways = [file for file in os.listdir(os.path.join("Data", "DungeonPieces", "Hallways")) if file[len(file) - 3:] == ".dp"]
loadedPieces = {}
loadedRooms = {}
loadedHallways = {}
def getDungeonPiece(streamPos, dungeon, number, isRoom=False):
	if isRoom:
		map = loadedRooms
		list = rooms
	else:
		map = loadedHallways
		list = hallways
	if not 0 <= number < len(list):
		number = 0
	if number not in map:
		map[number] = DungeonPiece(None, list[number], dungeon, isRoom)	
	return map[number]
	
def getRandomDungeonPiece(dungeon, room=False):
	if room:
		toRet = getDungeonPiece(None, random.randint(0, len(rooms) - 1), room)
	else:
		toRet = getDungeonPiece(None, random.randint(0, len(hallways) - 1), room)
	toRet.randomlyRotate()
	return toRet
	
def addPosToFittedPiece(grid, pos, streamPos):
	addPos = [pos[0] - streamPos[0], pos[1] - streamPos[1]]
	while addPos[1] < 0:
		newRow = [[1] * len(grid[0])]
		grid = newRow + grid
		streamPos[1] -= 1
		addPos = [pos[0] - streamPos[0], pos[1] - streamPos[1]]
		
	while addPos[0] < 0:
		for i in range(len(grid)):
			grid[i] = [1] + grid[i]
		streamPos[0] -= 1
		addPos = [pos[0] - streamPos[0], pos[1] - streamPos[1]]
		
	while addPos[1] >= len(grid):
		grid += [[1] * len(grid[0])]
	
	while addPos[0] >= len(grid[addPos[1]]):
		for i in range(len(grid)):
			grid[i] = grid[i] + [1]

	grid[addPos[1]][addPos[0]] = 0
	return grid
	
def getFittedDungeonPiece(dungeon, streamPos, maze, currentGrid):
	pos = [streamPos[0], streamPos[1]]
	isRoom = mazeGen.getTile(maze, pos) == mazeGen.ROOM
	sp = [streamPos[0], streamPos[1]]
	grid = [[0]]
	openSet = [(streamPos[0], streamPos[1])]
	addedSet = []
	while openSet and (len(addedSet) < 5 or isRoom):
		index = random.random()
		index = index**(e**0)
		index = int(index * len(openSet))
		selection = openSet[index]
		del openSet[index]
		grid = addPosToFittedPiece(grid, selection, sp)
		for dir in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
			checkPos = (selection[0] + dir[0], selection[1] + dir[1])
			if isRoom:
				if mazeGen.getTile(maze, checkPos) in [mazeGen.ROOM] and \
				 mazeGen.getTile(currentGrid, checkPos) not in [0, mazeGen.WALL] and \
				 dungeon.getRoom(checkPos) == None and \
				 checkPos not in addedSet:
					openSet += [checkPos]
			else:
				if mazeGen.getTile(maze, checkPos) in [mazeGen.HALLWAY] and \
				 mazeGen.getTile(currentGrid, checkPos) not in [0, mazeGen.WALL] and \
				 dungeon.getRoom(checkPos) == None and \
				 checkPos not in addedSet:
					openSet += [checkPos]
		addedSet += [selection]
		grid = addPosToFittedPiece(grid, selection, sp)
	
	piece = DungeonPiece(sp, '', dungeon, isRoom, grid)
	return sp, piece
		
enemyList = {}
enemyGroups = {}
def loadEnemyList(level):
	fileIn = open(os.path.join("Data", "Enemies", str(level), "EnemyList.txt"))
	enemyList[level] = []
	for line in fileIn:
		if line[0] != "#":
			#line = line.strip().split()
			#enemyList[level] += [[line[0], line[1], float(line[2]), float(line[3])]]
			enemyList[level] += [EnemyGroup(line)]
	fileIn.close()
	
class EnemyGroup:
	def __init__(self, line):
		line = line.strip().split()
		self.groupName = line[0]
		self.climateTypes = line[1]
		self.chance = float(line[2])
		self.groupSize = float(line[3])
		self.isBoss = (line[4] == "1")
		self.enemyList = []
		on = 5
		while on + 1 < len(line):
			self.enemyList += [EnemySpawnInfo(line[on], line[on + 1])]
			on += 2
			
class EnemySpawnInfo:
	def __init__(self, rangeInput, nameInput):
		range = rangeInput.split(",")
		self.min = int(range[0])
		self.max = int(range[1])
		self.name = nameInput