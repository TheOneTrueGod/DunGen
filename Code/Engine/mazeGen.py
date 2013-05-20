import random, pygame
from math import e
branchrate = 0 # between -10 and 10
#random.seed(11)
#Create weighted random number
#pos = random.random()
#pos = pos**(e**-branchrate)

UNSEEN = "?"
HALLWAY = "."
TOCHECK = ","
WALL = "#"
ROOM = "A"
CONNECTEDROOM = "B"
NOTHING = "."

def carve(pos, maze):
	toReturn = []
	if isAdjacentToRoom(pos, maze, CONNECTEDROOM):
		maze[pos[1]][pos[0]] = WALL
		return []
	adjacentRoom = isAdjacentToRoom(pos, maze)
	if not adjacentRoom:
		for offset in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
			if shouldAddToOpenSet([pos[0] + offset[0], pos[1] + offset[1]], maze):
				toReturn += [[pos[0] + offset[0], pos[1] + offset[1]]]
	else:
		maze[adjacentRoom[1]][adjacentRoom[0]] = CONNECTEDROOM
		for offsetX in [-2, -1, 0, 1, 2]:
			for offsetY in [-2, -1, 0, 1, 2]:
				curPos = [pos[0] + offsetX, pos[1] + offsetY]
				if isInBounds(curPos, maze) and maze[curPos[1]][curPos[0]] == ROOM:
					maze[curPos[1]][curPos[0]] = CONNECTEDROOM
	maze[pos[1]][pos[0]] = HALLWAY
	random.shuffle(toReturn)
	return toReturn
	
def isAdjacentToRoom(pos, maze, roomTile = ROOM):
	for offset in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
		curPos = [pos[0] + offset[0], pos[1] + offset[1]]
		if isInBounds(curPos, maze) and maze[curPos[1]][curPos[0]] == roomTile:
			return curPos
	return []
	
def shouldAddToOpenSet(pos, maze):
	if not isInBounds(pos, maze):
		return False
		
	if maze[pos[1]][pos[0]] != UNSEEN:
		return False
		
	if isAdjacentToRoom(pos, maze, CONNECTEDROOM):
		return
	maze[pos[1]][pos[0]] = TOCHECK
	return True
	
def canCarve(pos, maze, checkDiagonals = True):
	edges = []
	for offset in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
		curPos = [pos[0] + offset[0], pos[1] + offset[1]]
		if isInBounds(curPos, maze) and maze[curPos[1]][curPos[0]] == HALLWAY:
			edges += [offset]
				
	if len(edges) > 1:
		return False
		
	if checkDiagonals and len(edges) >= 1:
		toCheck = []
		if edges[0][0]:
			toCheck = [[-edges[0][0], -1], [-edges[0][0], 1]]
		else:
			toCheck = [[-1, -edges[0][1]], [1, -edges[0][1]]]
		for offset in toCheck:
			curPos = [pos[0] + offset[0], pos[1] + offset[1]]
			if isInBounds(curPos, maze) and maze[curPos[1]][curPos[0]] == HALLWAY:
				return False
			
	return True
	
def cleanMaze(maze):
	for row in range(len(maze)):
		for col in range(len(maze[row])):
			if maze[row][col] == UNSEEN:
				maze[row][col] = WALL
			if maze[row][col] == CONNECTEDROOM:
				maze[row][col] = ROOM
			#if maze[row][col] in [ROOM, HALLWAY]:
				#maze[row][col] = HALLWAY
			
def isInBounds(pos, maze):
	return 0 <= pos[1] < len(maze) and 0 <= pos[0] < len(maze[pos[1]])

def createMaze(seeds, maze):
	openSet = seeds
	while openSet:
		pos = random.random()
		pos = pos**(e**-branchrate)
		pos = int(pos * len(openSet))
		selection = openSet[pos]
		del openSet[pos]
		if canCarve(selection, maze):
			openSet += carve(selection, maze)
		else:
			maze[selection[1]][selection[0]] = WALL
	cleanMaze(maze)
	
def createGrid(sizeX, sizeY):
	maze = []
	for y in range(sizeY):
		maze += [[]]
		for x in range(sizeX):
			maze[y] += [UNSEEN]
	return maze
	
def trimLeaves(maze, pos):
	if isInBounds(pos, maze) and maze[pos[1]][pos[0]] == HALLWAY and isLeaf(maze, pos):
		maze[pos[1]][pos[0]] = WALL
		for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
			nPos = [pos[0] + off[0], pos[1] + off[1]]
			trimLeaves(maze, nPos)
			
def trimDeadEnds(maze):
	sizeY = len(maze)
	sizeX = len(maze[0])
	for x in range(sizeX):
		for y in range(sizeY):
			trimLeaves(maze, [x, y])
			
def transformToBraidMaze(maze):
	sizeY = len(maze)
	sizeX = len(maze[0])
	for x in range(sizeX):
		for y in range(sizeY):
			if isLeaf(maze, [x, y]):
				directionsToOpen = [[-1, 0], [1, 0], [0, 1], [0, -1]]
				openedSide = False
				while directionsToOpen and not openedSide:
					index = random.randint(0, len(directionsToOpen) - 1)
					newY = y + directionsToOpen[index][1]
					newX = x + directionsToOpen[index][0]
					if 0 <= newY < len(maze) and \
						 0 <= newX < len(maze[0]):
						if maze[newY][newX] == WALL and getAdjacentCount(maze, [newX, newY], HALLWAY) == 2:
							validTile = True
							for dir in [[-1, -1], [-1, 1], [1, -1], [1, 1]]:
								if getTile(maze, [newX + dir[0], newY + dir[1]]) == HALLWAY and \
									 getTile(maze, [newX + dir[0], newY + 0]) != HALLWAY and \
									 getTile(maze, [newX + 0, newY + dir[1]]) != HALLWAY:
									validTile = False
							if validTile:
								maze[newY][newX] = HALLWAY
								openedSide = True
					del directionsToOpen[index]
				
			
def isLeaf(maze, pos):
	if getAdjacentCount(maze, pos, WALL) >= 3:
		return True
	return False
	
def getAdjacentCount(maze, pos, tile, countLetters = False):
	count = 0
	for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
		nPos = [pos[0] + off[0], pos[1] + off[1]]
		if countLetters:
			if "A" <= getTile(maze, nPos) <= "Z":
				count += 1
		if getTile(maze, nPos) == tile:
			count += 1
	return count
	
def getTile(maze, pos):
	if (0 <= pos[0] < len(maze[0]) and 0 <= pos[1] < len(maze)):
		return maze[pos[1]][pos[0]]
	return WALL
	
def addRoom(startX, startY, sizeX, sizeY, maze):
	tiles = []
	for y in range(startY, startY + sizeY):
		for x in range(startX, startX + sizeX):
			if isInBounds([x, y], maze):
				maze[y][x] = ROOM
				tiles += [(x, y)]
	return tiles
		
def printMaze(maze, starsAt = []):
	s = ""
	y = 0
	for row in maze:
		x = 0
		for tile in row:
			if (x, y) in starsAt:
				s += "*"
			else:
				s += str(tile)
			x += 1
		y += 1
		s += "\n"
	print s

	
def addPosToFittedPiece(grid, pos, streamPos):
	addPos = [pos[0] - streamPos[0], pos[1] - streamPos[1]]
	print "--- begin ---"
	print "addPos:", addPos
	print "oldGrid:"
	printMaze(grid)
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
	print "newGrid:"
	printMaze(grid)
	print "final addPos:", addPos
	grid[addPos[1]][addPos[0]] = 0
	print "finalGrid:"
	printMaze(grid)
	print "--- end ---"
	return grid
	
def getFittedDungeonPiece(dungeon, streamPos, maze, currentGrid):
	pos = [streamPos[0], streamPos[1]]
	sp = [streamPos[0], streamPos[1]]
	#grid = [[0]]
	grid = [[1]]
	for dir in [[0, 0], [0, -1], [-1, 0], [1, 0], [0, 1]]:
		grid = addPosToFittedPiece(grid, [dir[0], dir[1]], sp)
	print "final StreamPos:", sp

	
if __name__ == "__main__" and False:
	maze = createGrid(60, 60)
	sectorsToGenerate = 5
	sectorSizeY = len(maze) / float(sectorsToGenerate)
	sectorSizeX = len(maze[0]) / float(sectorsToGenerate)
	for x in range(sectorsToGenerate):
		for y in range(sectorsToGenerate):
			if (x != 0 or y != 0) and (x != sectorsToGenerate - 1 or y != sectorsToGenerate - 1) and (x != 0 or y != sectorsToGenerate - 1) and (x != sectorsToGenerate - 1 or y != 0):
				offsetX = 2
				offsetY = 2
				curPos = [sectorSizeX * x + offsetX, sectorSizeY * y + offsetY]
				size = [sectorSizeX - offsetX - 2, sectorSizeY - offsetY - 2]
				addRoom(curPos[0], curPos[1], size[0], size[1], maze)
	createMaze([[0, 0], [0, 59], [59, 0], [59, 59]], maze)
	printMaze(maze)
elif __name__ == "__main__":
	getFittedDungeonPiece(None, [0, 0], [], [])