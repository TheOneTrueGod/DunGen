#!/usr/bin/env python
'''Generate a perfect maze, that is a maze with
		* all included points connected (no isolated passages) and
		* no loops (only one path between any two points).
The size and branching factor of the maze can be adjusted.

Coding by d.factorial [at] gmail.com.
'''
import random

#the dimensions of the maze

xwide, yhigh = 40, 20

#the grid of the maze
#each cell of the maze is one of the following:
		# '#' is wall
		# '.' is empty space
		# ',' is exposed but undetermined
		# '?' is unexposed and undetermined

#list of coordinates of exposed but undetermined cells.
frontier = []

def carve(y, x, maze):
		'''Make the cell at y,x a space.
		
		Update the fronteer and maze accordingly.
		Note: this does not remove the current cell from frontier, it only adds new cells.
		'''
		extra = []
		maze[y][x] = '.'
		if x > 0:
				if maze[y][x-1] == '?':
						maze[y][x-1] = ','
						extra.append((y,x-1))
		if x < xwide - 1:
				if maze[y][x+1] == '?':
						maze[y][x+1] = ','
						extra.append((y,x+1))
		if y > 0:
				if maze[y-1][x] == '?':
						maze[y-1][x] = ','
						extra.append((y-1,x))
		if y < yhigh - 1:
				if maze[y+1][x] == '?':
						maze[y+1][x] = ','
						extra.append((y+1,x))
		random.shuffle(extra)
		frontier.extend(extra)

def harden(y, x, maze):
		'''Make the cell at y,x a wall.
		'''
		maze[y][x] = '#'

def isWalkable(maze, pos):
	return getTile(maze, pos) == "." #or "A" <= getTile(maze, pos) <= "Z"

def checkForDoor(maze, pos):
	getAdjacentCount(maze, pos, "", countLetters = True):
	
def check(y, x, maze, nodiagonals = False):
		'''Test the cell at y,x: can this cell become a space?
		
		True indicates it should become a space,
		False indicates it should become a wall.
		'''
		if not checkForDoor(maze, [x, y]):
			return False
			
		edgestate = 0
		if isWalkable(maze, [x-1, y]):
			edgestate += 1
		if isWalkable(maze, [x+1, y]):
			edgestate += 2
		if isWalkable(maze, [x, y-1]):
			edgestate += 4
		if isWalkable(maze, [x, y+1]):
			edgestate += 8
		
		if nodiagonals:
				#if this would make a diagonal connecition, forbid it
						#the following steps make the test a bit more complicated and are not necessary,
						#but without them the mazes don't look as good
				if edgestate == 1:
					if isWalkable(maze, [x+1, y-1]):
						return False
					if isWalkable(maze, [x+1, y+1]):
						return False
					return True
				elif edgestate == 2:
					if isWalkable(maze, [x-1, y-1]):
						return False
					if isWalkable(maze, [x-1, y+1]):
						return False
					return True
				elif edgestate == 4:
					if isWalkable(maze, [x-1, y+1]):
						return False
					if isWalkable(maze, [x+1, y+1]):
						return False
					return True
				elif edgestate == 8:
					if isWalkable(maze, [x-1, y-1]):
						return False
					if isWalkable(maze, [x+1, y-1]):
						return False
					return True
				return False
		else:
				#diagonal walls are permitted
				if	[1,2,4,8].count(edgestate):
						return True
				return False
		

#parameter branchrate:
#zero is unbiased, positive will make branches more frequent, negative will cause long passages
#this controls the position in the list chosen: positive makes the start of the list more likely,
#negative makes the end of the list more likely
#large negative values make the original point obvious
#try values between -10, 10
def generateMaze(branchrate=0):
	maze = []
	for y in range(yhigh):
		row = []
		for x in range(xwide):
			row.append('?')
		maze.append(row)
	addRooms(maze, 3, 3)
	#choose a original point at random and carve it out.
	xchoice = random.randint(0, xwide-1)
	ychoice = random.randint(0, yhigh-1)
	while getTile(maze, [xchoice, ychoice]) != "?":
		xchoice = random.randint(0, xwide-1)
		ychoice = random.randint(0, yhigh-1)
	carve(ychoice,xchoice, maze)

	from math import e

	while(len(frontier)):
		#select a random edge
		pos = random.random()
		pos = pos**(e**-branchrate)
		choice = frontier[int(pos*len(frontier))]
		if check(choice[0], choice[1], maze):
				carve(choice[0], choice[1], maze)
		else:
				harden(choice[0], choice[1], maze)
		frontier.remove(choice)
			
	#set unexposed cells to be walls
	for y in range(yhigh):
		for x in range(xwide):
			if maze[y][x] == '?':
				maze[y][x] = '#'
	return maze
	
def addRooms(maze, numX, numY):
	sizeY = len(maze)
	sizeX = len(maze[0])
	gridSizeY = sizeY / numY
	gridSizeX = sizeX / numX
	letterOn = ord("A")
	for xG in range(numX):
		for yG in range(numY):
			roomSizeX = random.randint(3, gridSizeX - 2)
			roomSizeY = random.randint(3, gridSizeY - 2)
			roomTop = random.randint(0, gridSizeY - roomSizeY - 2) + yG * gridSizeY
			roomLeft = random.randint(0, gridSizeX - roomSizeX - 2) + xG * gridSizeX
			for y in range(roomSizeY):
				for x in range(roomSizeX):
					yP = y + roomTop
					xP = x + roomLeft
					maze[yP][xP] = chr(letterOn)
			letterOn += 1
	return maze
	
def fillPath(maze, pos, charToFill, charToReplace):
	if not (0 <= pos[0] < len(maze[0]) and 0 <= pos[1] < len(maze)):
		return
	if maze[pos[1]][pos[0]] != charToFill:
		return
	maze[pos[1]][pos[0]] = charToReplace
	for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
		fillPath(maze, [pos[0] + off[0], pos[1] + off[1]], charToFill, charToReplace)
	
def trimLeaves(maze, pos):
	if getTile(maze, pos) == "." and isLeaf(maze, pos):
		maze[pos[1]][pos[0]] = "@"
		for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
			nPos = [pos[0] + off[0], pos[1] + off[1]]
			trimLeaves(maze, nPos)
	
def getTile(maze, pos):
	if (0 <= pos[0] < len(maze[0]) and 0 <= pos[1] < len(maze)):
		return maze[pos[1]][pos[0]]
	return "#"
	
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
	
def getAdjacentTiles(maze, pos):
	toRet = ""
	for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
		nPos = [pos[0] + off[0], pos[1] + off[1]]
		toRet += getTile(maze, nPos)
	return toRet
	
def isLeaf(maze, pos):
	if getAdjacentCount(maze, pos, "#") >= 3:
		return True
	return False
	
def trimDeadEnds(maze):
	sizeY = len(maze)
	sizeX = len(maze[0])
	for x in range(sizeX):
		for y in range(sizeY):
			trimLeaves(maze, [x, y])
				
	return maze
				
def printMaze(maze):
	#print the maze
	for y in range(yhigh):
		s = ''
		for x in range(xwide):
				s += maze[y][x]
		print s
	
def checkPath(maze, pos, lastPos):
	if not (0 <= pos[0] < len(maze[0]) and 0 <= pos[1] < len(maze)) or maze[pos[1]][pos[0]] == "#":
		return ""
		
	if "A" <= maze[pos[1]][pos[0]] <= "Z":
		return maze[pos[1]][pos[0]]
	
	toRet = ""
	for off in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
		nPos = [pos[0] + off[0], pos[1] + off[1]]
		if (0 <= nPos[0] != lastPos[0] or nPos[1] != lastPos[1]):
			result = checkPath(maze, nPos, pos)
			if result not in toRet:
				toRet += result
	return toRet
	
def removeExtraDoors(maze):
	pass
maze = generateMaze(10)
removeExtraDoors(maze)
trimDeadEnds(maze)
#checkPath(maze, [0, 0], [-10, -10])
printMaze(maze)