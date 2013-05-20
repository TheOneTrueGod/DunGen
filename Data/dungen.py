import pygame, os, random, math
from pygame.locals import *
pygame.init()
def normalize(list, inverse=False):
	total = 0
	for element in list:
		total += element[0]
	for element in list:
		element[0] = element[0] / float(total)
		if inverse:
			element[0] = 1 - element[0]
			
def randFromNormalizedList(list):
	randNum = random.random()
	curr = 0
	while randNum > list[curr][0] and curr < len(list) - 1:
		randNum -= list[curr][0]
		curr += 1
		
	assert(0 <= curr < len(list))
	return list[curr][1]
		
def dist(a, b):
	return math.sqrt((a[0] - b[0]) **2 + (a[1] - b[1])**2)

UP = 1
RIGHT = 2
DOWN = 4
LEFT = 8
	
class ClimateStruct:
	def __init__(self, size=(50,50)):
		self.grid = []
		self.walls = []
		for i in range(size[1]):
			self.grid += [[1] * size[0]]
			self.walls += [[15] * size[0]]
			
		self.size = size
		self.connect([10, 10], LEFT)
			
	def getTile(self, pos):
		if 0 <= pos[1] < self.size[1] and 0 <= pos[0] < self.size[0]:
			return self.grid[pos[1]][pos[0]]
		return 0
		
	def getWall(self, pos):
		if 0 <= pos[1] < self.size[1] and 0 <= pos[0] < self.size[0]:
			return self.walls[pos[1]][pos[0]]
		return 15
		
	def connect(self, pos, direction):
		self.walls[pos[1]][pos[0]] = self.walls[pos[1]][pos[0]] ^ direction
		p = pos[0] - int((direction & LEFT) and True) + int((direction & RIGHT) and True), pos[1] - int((direction & UP) and True) + int((direction & DOWN) and True)
		dir = 0
		if direction & LEFT:
			dir += RIGHT
		if direction & DOWN:
			dir += UP
		if direction & UP:
			dir += DOWN
		if direction & RIGHT:
			dir += LEFT
		self.walls[p[1]][p[0]] ^= dir
		print self.walls[pos[1]][pos[0]]
		print self.walls[p[1]][p[0]]
			
	def iterate(self):
		return True
		
	def generate(self):
		doneCount = 0
		while doneCount <= 0:
			if self.iterate():
				doneCount += 1
			
	def __str__(self):
		result = ""
		y = 0
		for i in self.grid:
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
		

surface = pygame.display.set_mode([400, 400], 0)
def redraw():
	global surface
	pixelSize = 4
	c = ClimateStruct([20, 20])
	c.generate()
	surface.fill([0] * 3)
	for x in range(len(c.grid)):
		for y in range(len(c.grid[x])):
			if c.getTile((x, y)) == 0:
				clr = [0, 0, 0]
			else:
				clr = [255] * 3
			
			for i in range(pixelSize):
				for j in range(pixelSize):
					surface.set_at((30 + x * 2 * pixelSize + i, 30 + y * 2 * pixelSize + j), clr)
					
	for x in range(len(c.grid)):
		for y in range(len(c.grid[x])):
			for i in range(pixelSize):
				for j in range(pixelSize):
					if c.getWall((x, y)) & UP:
						clr = [100, 100, 100]
					else:
						clr = [0]*3
					surface.set_at((30 + (x * 2) * pixelSize + i, 30 + (y * 2 - 1) * pixelSize + j), clr)
						
					if c.getWall((x, y)) & RIGHT:
						clr = [100, 100, 100]
					else:
						clr = [0]*3
					surface.set_at((30 + (x * 2 + 1) * pixelSize + i, 30 + (y * 2) * pixelSize + j), clr)
						
			for i in range(pixelSize):
				for j in range(pixelSize):
					if c.getWall((x, y)) & DOWN:
						clr = [100, 100, 100]
					else:
						clr = [0]*3
					surface.set_at((30 + (x * 2 ) * pixelSize + i, 30 + (y * 2 + 1) * pixelSize + j), clr)
						
			for i in range(pixelSize):
				for j in range(pixelSize):
					if c.getWall((x, y)) & LEFT:
						clr = [100, 100, 100]
					else:
						clr = [0]*3
					surface.set_at((30 + (x * 2 - 1) * pixelSize + i, 30 + (y * 2) * pixelSize + j), clr)
	#getWall
			
	pygame.display.update()

redraw()
done = False
while not done:
	for ev in pygame.event.get():
		if ev.type == QUIT:
			done = True
		elif ev.type == KEYDOWN:
			if ev.key == K_ESCAPE:
				done = True
			elif ev.key == K_SPACE:
				redraw()
			
	