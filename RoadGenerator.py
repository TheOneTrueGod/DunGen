import random
from Globals import normalize, randFromNormalizedList, dist, raytrace

class RoadStruct:
	RoadTurnChance = 0.2
	MaxRoadDistance = 50
	MaxRoadsPerNode = 1
	RoadDirections = [[0, -1], [1, 0], [0, 1], [-1, 0]]
	def __init__(self, size=(20,20)):
		self.tiles = []
		for i in range(size[1]):
			self.tiles += [[0] * size[0]]
		self.size = size
		self.majorNodes = []
			
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
		xSpots = 5
		ySpots = 5
		for x in range(xSpots):
			for y in range(ySpots):
				p = [random.randint(x * (self.size[0] - 1) / xSpots, (x + 1) * (self.size[0] - 1) / xSpots), 
						 random.randint(y * (self.size[1] - 1) / ySpots, (y + 1) * (self.size[1] - 1) / ySpots)]
				self.majorNodes += [[p, 0]]
		self.majorNodes = [[[5, 5], 0], [[15, 5], 0]]
		random.shuffle(self.majorNodes)
		for p in self.majorNodes:
			drewOne = False
			for p2 in self.majorNodes:
				if p is not p2 and p2[1] < self.MaxRoadsPerNode and p[1] < self.MaxRoadsPerNode and dist(p[0], p2[0]) <= self.MaxRoadDistance:
					drewOne = True
					prev = p[0]
					p[1] += 1
					p2[1] += 1
					for square in raytrace(p[0], p2[0]):
						dirs = (square[1] < prev[1]) * 1 + (square[0] > prev[0]) * 2 + (square[1] > prev[1]) * 4 + (square[0] < prev[0]) * 8
						self.tiles[prev[1]][prev[0]] = self.tiles[prev[1]][prev[0]] | dirs
						dirs = (square[1] > prev[1]) * 1 + (square[0] < prev[0]) * 2 + (square[1] < prev[1]) * 4 + (square[0] > prev[0]) * 8
						self.tiles[square[1]][square[0]] = self.tiles[square[1]][square[0]] | dirs
						prev = square
					dirs = (p2[0][1] < prev[1]) * 1 + (p2[0][0] > prev[0]) * 2 + (p2[0][1] > prev[1]) * 4 + (p2[0][0] < prev[0]) * 8
					self.tiles[p2[0][1]][p2[0][0]] = self.tiles[p2[0][1]][p2[0][0]] | dirs
			
	def __str__(self):
		result = ""
		for i in self.tiles:
			for j in i:
				result += hex(j)[2]
			result += "\n"
		return result
		
c = RoadStruct()
c.generate()