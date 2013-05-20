FULLSCREEN = 0
NUMPLAYERS = 1

import math, pygame, os, random, sys, pickle
os.environ['SDL_VIDEO_WINDOW_POS'] = str(3) + "," + str(29)
from pygame.locals import *
if not pygame.font.get_init():
	pygame.font.init()
DEBUGMODE = 0
TOOLTIPS = {}
CHARPICTURES = {}
PROJECTILEPICTURES = {}
ICONS = {}
SCREENSIZE = [800, 600]
EDITORSCREENSIZE = [1000, 700]
TILESIZE = [20, 20]
NUMABILS = 2
ICONSIZE = 55
MINFPS = 1000 / 30
PTRS = {"FRAME":0}
FOGOFWAR = False
RESPAWNTIME = 50
DUNGEONBOXSIZE = (7, 7)
STREAMSTARTPOS = (25, 25)#(20, 20)
DUNGEONSIZE = (50, 50)#(40, 40)
WATERSLOWDOWN = 0.5
AUTOSAVEDELAY = 500
RIGHTWALL = 1
BOTWALL = 2
LEFTWALL = 4
TOPWALL = 8
DELTAHEALRATE = 0.01
DELTADAMAGERATE = 0.01
PLAYERFILES = [None, None]
HITDISPLAYTIME = 200
LOADBYPROXIMITY = False #Whether or not an adjacent room should load when a unit is standing near the door to it
DRAWTARGETTINGCIRCLE = False
NUMFLOORS = 2

ROOMRESPAWNTIME = 600

STUNTIME = 15

ALLDOORSMODE = False
FORCERELOAD = True

INVENTORYSLOTS = 3 * 13
EQUIPMENTSLOTS = 12
ITEMSIZE = 24

ABILITYSLOTS = 5
ABILITYDISPLAYSLOTS = 36

DOORHOLDTIME = 200

EXPERIENCECOLOUR = [196, 161, 0]
DARKEXPERIENCECOLOUR = [int(196 * 0.5), int(161*0.5), 0]

AUTOATTACK = False

#0 - Grasslands, 1 - Wetlands, 2 - Darklands
#0 - Grass, 1 - Wall, 2 - Water, 3 - Path, 4 - Lava, 5 - Regular Decoration, 6 - Slowing Decoration
TERRAINSPEEDMODS = [[1, 1, 0.6, 1.2, 0.3, 1, 0.8],
										[0.6, 1, 0.6, 1.2, 0.3, 1, 0.8],
										[1, 1, 0.6, 1.2, 0.3, 1, 0.8]]

gridsize = 20

PTRS["DRAWDEBUG"] = False
PTRS["EDITORMODE"] = False

GRAVITY = 1.0
JUMPSPEED = -10
MAXFALLSPEED = 18
DEFAULTSCANTIME = 100
FRICTION = 0.8
SPEEDTHRESHOLD = 0.01
MINRUNSPEED = 1
MAXRUNSPEED = 5
AIRCONTROL = 0.4
ACCELERATION = 0.7
STARTGOLD = 200
EFFECTPICS = {"Exclamation":pygame.image.load(os.path.join("Data", "Pics", "Effects", "Exclamation.png"))}
EFFECTPICS["Exclamation"].set_colorkey([255, 255, 255])
ABILITYICONS = {"BattleFrame":pygame.image.load(os.path.join("Data", "Pics", "Abilities", "BattleFrame.png"))}
ABILITYICONS ["SelectedFrame"] = pygame.image.load(os.path.join("Data", "Pics", "Abilities", "SelectedFrame.png"))
ITEMICONS = {}
for file in os.listdir(os.path.join("Data", "Pics", "Equipment")):
	if file not in ["EmptySlot"] and file[len(file) - 4:] == ".png":
		ITEMICONS[file[:len(file) - 4]] = pygame.image.load(os.path.join("Data", "Pics", "Equipment", file))

#units = None
#players = None
#effects = None
#terrain = None
#projectiles = None
#backgroundPic = None

FONTS = {"TEXTBOXFONT":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),12),
				 "GUILDNAMEFONT":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"), 14),
				 "EFFECTFONT" :pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),14),
				 "EFFECTFONTSMALL":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),10),
				 "EFFECTFONTLARGE":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),20),
				 "HPBARFONT":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),9),
				 "GODMENUFONT":pygame.font.Font(os.path.join("Data", "Fonts", "MainFont.ttf"),18)}

ScanTimeLookup = {0:1, 1:20, 2:40, 3:60, 4:80, 5:100, 6:150, 7:200, 8:400, 9:1000}

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	return type('Enum', (), enums)
	
itemTypes = enum('KEY', 'RKEY', 'BKEY', 'WKEY',  'OKEY', 'COIN', 'DEFEND')
enemyTypes = enum('UNKNOWN', 'ANIMAL', 'SLIME', 'UNDEAD', 'HUMANOID', 'ELEMENTAL')
damageTypes = enum(\
'UNTYPED', 'SLASH', 'PIERCE', 'BASH', 'ENERGY', 'FIRE', \
'ICE', 'LIGHT', 'DARK', 'POISON')
numDamageTypes = 10

def dist(a, b):
	return math.sqrt((a[0] - b[0]) **2 + (a[1] - b[1])**2)
	
def signOf(i):
	if i >= 0:
		return 1
	return -1;
	
def isInt(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
		
def isFloat(s):
	try:
		float(s)
		return True
	except ValueError:
		return False
	
def drawTextBox(surface, pos, size, text, drawBorder, bckClr = [0, 0, 0], txtClr = [255, 255, 255]):
	textSpacing = 5
	if drawBorder:
		pygame.draw.rect(surface, bckClr, (pos,size))
		pygame.draw.rect(surface, txtClr, (pos[0], pos[1],size[0], size[1]),2)
	currPos = [pos[0] + 6,pos[1] + 6]
	for lines in text.split("\n"):
		currText = lines.split(" ")
		for i in currText:
			if currPos[1] < pos[1] + size[1]:
				if i.find('\n') != -1:
					toDraw = FONTS["TEXTBOXFONT"].render(i[:i.find('\n')], False, txtClr)
				else:
					toDraw = FONTS["TEXTBOXFONT"].render(i, False, txtClr)
				if currPos[0] + toDraw.get_width() - pos[0] + textSpacing > size[0]:
					currPos[0] = pos[0] + 6
					currPos[1] = currPos[1] + 12
				surface.blit(toDraw,(currPos))
				currPos[0] += toDraw.get_width() + textSpacing
		currPos[0] = pos[0] + 6
		currPos[1] = currPos[1] + 12
		
def drawCenteredText(surface, pos, text, textClr, fontType):
	toDraw = fontType.render(text, False, textClr)
	surface.blit(toDraw, (pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2))
	
def drawText(surface, pos, text, textClr, fontType):
	toDraw = fontType.render(text, False, textClr)
	surface.blit(toDraw, pos)
		
def raytrace(start, end):
	g = gridsize
	dx = abs(end[0] - start[0])
	dy = abs(end[1] - start[1])
	x = start[0]
	y = start[1]
	n = 1 + int(dx) + int(dy)
	if end[0] > start[0]:
		x_inc = 1
	else:
		x_inc = -1
	if (end[1] > start[1]):
		y_inc = 1
	else:
		y_inc = -1
	error = dx - dy
	dx *= 2
	dy *= 2

	toRet = []
	while n > 0:
		n -= 1
		toRet += [[x, y]]

		if (error > 0):
			x += x_inc
			error -= dy
		else:
			y += y_inc
			error += dx
	return toRet

def signOf(i):
	if i >= 0:
		return 1
	elif i < 0:
		return -1

def intOf(list):
	return [int(k) for k in list]
	
class Keys:
	def __init__(self):
		self.pressed = {}
		self.keysDown = {}
		self.keysUp = {}
		self.mousePos = [0, 0]
		self.mouseButtons = []

	def getMousePos(self):
		return self.mousePos
		
	def getMouseButtons(self):
		return self.mouseButtons
		
	def getMouseButtonsDown(self):
		return self.mouseDown
		
	def getMouseButtonsUp(self):
		return self.mouseUp
		
	def keyPressed(self, key):
		return key in self.pressed
		
	def keyDown(self, key):
		return key in self.keysDown
		
	def keyUp(self, key):
		return key in self.keysUp
		
	def getKeys(self):
		return self.pressed
		
	def flush(self):
		self.keysDown = {}
		self.keysUp = {}
		self.mouseDown = []
		self.mouseUp = []
	
	def handleEvent(self, ev):
		if ev.type == KEYDOWN:
			self.pressed[ev.key] = True
			self.keysDown[ev.key] = True
		elif ev.type == KEYUP:
			if ev.key in self.pressed:
				del self.pressed[ev.key]
			self.keysUp[ev.key] = True
		elif ev.type == MOUSEMOTION:
			self.mousePos = ev.pos
		elif ev.type == MOUSEBUTTONDOWN:
			self.mousePos = ev.pos
			self.mouseButtons += [ev.button]
			self.mouseDown += [ev.button]
		elif ev.type == MOUSEBUTTONUP:
			self.mousePos = ev.pos
			if ev.button in self.mouseButtons:
				self.mouseButtons.remove(ev.button)
			if ev.button in self.mouseUp:
				self.mouseUp.remove(ev.button)
PTRS["KEYS"] = Keys()

def getPlayerControls(playerNum, keyString):
	if keyString.upper() in ["BACKUP", "RESTORE", "RESTART", "MENUS", "SWITCH", "START"]:
		return {"BACKUP":K_b, "RESTORE":K_n, "RESTART":K_v, "MENUS":K_ESCAPE, "SWITCH":K_v, "START":K_SPACE}[keyString.upper()]
	elif playerNum == 1:
		return {"UP":K_w, "DOWN":K_s, "LEFT":K_a, "RIGHT":K_d, "SPECIALSWITCH":K_TAB}[keyString.upper()]
	elif playerNum == 2:
		return {"UP":K_UP, "DOWN":K_DOWN, "LEFT":K_LEFT, "RIGHT":K_RIGHT, "SPECIALSWITCH":K_o, "SPECIALATTACK":K_l, "TARGETSWITCH":K_SEMICOLON}[keyString.upper()]
	print "Error: keyString unknown: ", keyString
	return 0
	
PTRS["FOGOFWAR"] = pygame.Surface(SCREENSIZE)
PTRS["FOGOFWAR"].set_colorkey([255, 0, 255])
	
def getAngDiff(selfAng, targAng):
	angDiff = (targAng - selfAng)
	if angDiff < -math.pi:
		angDiff = math.pi * 2 + angDiff
	elif angDiff > math.pi:
		angDiff = angDiff - math.pi * 2
	return angDiff
	
def posToCoords(pos):
	return (int(pos[0] / TILESIZE[0]), int(pos[1] / TILESIZE[1]))
	
def coordsToPos(coords):
	return (int(coords[0] * TILESIZE[0] + TILESIZE[0] / 2), int(coords[1] * TILESIZE[1] + TILESIZE[1] / 2))
	
def dungeonGridToCoords(grid):
	return (int(grid[0] * (DUNGEONBOXSIZE[0] + 1) + (DUNGEONBOXSIZE[0] + 1) / 2), int(grid[1] * (DUNGEONBOXSIZE[1] + 1) + (DUNGEONBOXSIZE[1] + 1) / 2))

def posToDungeonGrid(pos):
	return (int((pos[0] / TILESIZE[0] - 1) / (DUNGEONBOXSIZE[0] + 1)), int((pos[1] / TILESIZE[1] - 1) / (DUNGEONBOXSIZE[1] + 1)))
	
def coordsToDungeonGrid(coords):
	return (int((coords[0] - 1) / (DUNGEONBOXSIZE[0] + 1)), int((coords[1] - 1) / (DUNGEONBOXSIZE[1] + 1)))

# 00 10 20
# 01 11 21
# 02 12 22
#->
# 02 01 00
# 12 11 10
# 22 21 20
#->
# 22 12 02
# 21 11 01
# 20 10 00
def rot2(a):
		n = len(a)
		c = (n+1) / 2
		f = n / 2
		for x in range(c):
			for y in range(f):
				a[x][y] = a[x][y] ^ a[n-1-y][x]
				a[n-1-y][x] = a[x][y] ^ a[n-1-y][x]
				a[x][y] = a[x][y] ^ a[n-1-y][x]
				a[n-1-y][x] = a[n-1-y][x] ^ a[n-1-x][n-1-y]
				a[n-1-x][n-1-y] = a[n-1-y][x] ^ a[n-1-x][n-1-y]
				a[n-1-y][x] = a[n-1-y][x] ^ a[n-1-x][n-1-y]
				a[n-1-x][n-1-y] = a[n-1-x][n-1-y]^a[y][n-1-x]
				a[y][n-1-x] = a[n-1-x][n-1-y]^a[y][n-1-x]
				a[n-1-x][n-1-y] = a[n-1-x][n-1-y]^a[y][n-1-x]
				
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
	
def readAllLinesInFile(path):
	toRet = []
	fileIn = open(path)
	for line in fileIn:
		if line[0] != "#":
			line = line.strip().split()
			toRet += [line]
	fileIn.close()
	return toRet
	
def inSameRoom(unit1, unit2):
	return unit1.floor == unit2.floor and GetDungeonGrid(unit1.floor).getRoom(posToDungeonGrid(unit1.getPos())) == GetDungeonGrid(unit2.floor).getRoom(posToDungeonGrid(unit2.getPos()))
	
def LoadDungeon(floor):
	if "DUNGEONGRID" not in PTRS:
		PTRS["DUNGEONGRID"] = {}
	if not FORCERELOAD and not "-r" in sys.argv and os.path.exists(os.path.join("Profiles", "Dungeons", "Floor"+str(floor)+".dng")):
		PTRS["DUNGEONGRID"][floor] = pickle.load(open(os.path.join("Profiles", "Dungeons", "Floor"+str(floor)+".dng")))
	else:
		from Code.Engine.DungeonGenerator import DungeonGrid
		PTRS["DUNGEONGRID"][floor] = DungeonGrid(DUNGEONSIZE, floor)
		
def GetDungeonGrid(floor):
	if "DUNGEONGRID" not in PTRS:
		PTRS["DUNGEONGRID"] = {}
	if floor in PTRS["DUNGEONGRID"]:
		return PTRS["DUNGEONGRID"][floor]
	LoadDungeon(floor)
	return PTRS["DUNGEONGRID"][floor]
	
def LoadTerrain(floor):
	if "TERRAIN" not in PTRS:
		PTRS["TERRAIN"] = {}
	from Code.Engine.Terrain import Terrain
	PTRS["TERRAIN"][floor] = Terrain(floor)
	PTRS["TERRAIN"][floor].initializeStreamedDungeon(floor)
	#if not FORCERELOAD and not "-r" in sys.argv and os.path.exists(os.path.join("Profiles", "Dungeons", "Terrain"+str(floor)+".png")):
	#	PTRS["TERRAIN"][floor].loadFromFile(floor)
	#else:
	#	PTRS["TERRAIN"][floor].initializeStreamedDungeon(floor)
		#[floor]
		
def GetTerrain(floor):
	#return PTRS["TERRAIN"]
	if "TERRAIN" not in PTRS:
		LoadTerrain(floor)
	if floor in PTRS["TERRAIN"]:
		return PTRS["TERRAIN"][floor]
	LoadTerrain(floor)
	return PTRS["TERRAIN"][floor]
	
def getDoorCoordinates(gridPos, boxSize, direction):
	return (gridPos[0] * (boxSize[0] + 1) + 1 + int(boxSize[0] / 2) + int(boxSize[0] / 2 + 1) * direction[0],
				 gridPos[1] * (boxSize[1] + 1) + 1 + int(boxSize[1] / 2) + int(boxSize[1] / 2 + 1) * direction[1])
				 
def getDirectionList(directionNumber):
	dirs = []
	if directionNumber & 1:
		dirs += [[0, -1]]
	if directionNumber & 2:
		dirs += [[1, 0]]
	if directionNumber & 4:
		dirs += [[0, 1]]
	if directionNumber & 8:
		dirs += [[-1, 0]]
	return dirs
	
def buttonHit(mousePos, butPos):
	if butPos[0][0] <= mousePos[0] <= butPos[0][0] + butPos[1][0] and butPos[0][1] <= mousePos[1] <= butPos[0][1] + butPos[1][1]:
		return True
	return False
	
def loadAbilIcon(icon):
	if icon not in ABILITYICONS:
		path = os.path.join("Data", "Pics", "Abilities", icon + ".png")
		if not os.path.exists(path):
			icon = "BattleFrame"
			print "ERROR: ABILITY ICON NOT FOUND:", icon
		else:
			ABILITYICONS[icon] = pygame.image.load(path)
			
def drawAbilIcon(surface, pos, icon, frameIcon, cooldownPct = 1):
	iconSize = 40
	iconPos = [0, 0]
	if type(icon) == type([]):
		iconPos = icon[1]
		icon = icon[0]
	if icon:
		loadAbilIcon(icon)
		if cooldownPct >= 1:
			surface.blit(ABILITYICONS[icon].subsurface([iconPos[0] * iconSize, iconPos[1] * iconSize, iconSize, iconSize]), pos)
		else:
			yVal = int(iconSize * (1 - cooldownPct))
			surface.blit(ABILITYICONS[icon].subsurface([iconPos[0] * iconSize, iconPos[1] * iconSize, iconSize, yVal]), pos)
			yVal += pos[1]
			pygame.draw.line(surface, [255, 0, 0], [pos[0], yVal], [pos[0] + iconSize, yVal])
	surface.blit(ABILITYICONS[frameIcon], pos)
			
def isOnscreen(centreScreen, targetPos):
	if centreScreen[0] - 240 <= targetPos[0] <= centreScreen[0] + 240 and \
		 centreScreen[1] - 340 <= targetPos[1] <= centreScreen[1] + 340:
		return True
	return False
	
def drawItemIcon(surface, position, iconPos, scale=1, rotation=0, alpha=1):
	surf = ITEMICONS[iconPos[0]].subsurface([iconPos[1][0] * ITEMSIZE, iconPos[1][1] * ITEMSIZE, ITEMSIZE, ITEMSIZE])
	if scale != 1:
		surf = pygame.transform.scale(surf, [int(ITEMSIZE * scale), int(ITEMSIZE * scale)])
	if rotation != 0:
		surf = pygame.transform.rotate(surf, 180 - rotation + 90)
	if alpha != 1:
		if scale == 1 and rotation == 0:
			surf = surf.copy()
		surf.set_alpha(int(alpha * 255))
		size = surf.get_size()
		try:
			for y in xrange(size[1]):
				for x in xrange(size[0]):
					r,g,b,a = surf.get_at((x,y))
					surf.set_at((x,y),(r,g,b,int(a*alpha)))
		except:
			print "EXCEPTION!"
	surface.blit(surf, position)
	
def loadProjectilePic(pic):
	path = os.path.join("Data", "Pics", "Projectiles", pic + ".PNG")
	if not os.path.exists(path):
		print "ERROR, file not found: '" + path + "'"
		if os.path.exists(os.path.join("Data", "Pics", "Projectiles", "None.PNG")):
			return loadProjectilePic("None")
	pic = pygame.image.load(path)
	pic.set_colorkey([255, 0, 255])
	height = pic.get_height()
	width = height
	frames = pic.get_width() / height
	toRet = []
	for x in xrange(frames):
		toRet += [pic.subsurface([x * width, 0, width, height])]
	
	return toRet

def drawProjectilePic(surface, pic, pos, frame, angle, alpha = 1):
	if type(pic) == type([]):
		global ITEMICONS
		posToDraw = [pos[0] - ITEMSIZE / 2, pos[1] - ITEMSIZE / 2]
		drawItemIcon(surface, posToDraw, pic, rotation=angle, alpha = alpha)
	else:
		global PROJECTILEPICTURES
		if pic in PROJECTILEPICTURES:
			toDraw = pygame.transform.rotate(PROJECTILEPICTURES[pic][frame], 180 - angle + 90)
			pos = [pos[0] - toDraw.get_width() / 2, pos[1] - toDraw.get_height() / 2]
			surface.blit(toDraw, pos)
		else:
			PROJECTILEPICTURES[pic] = loadProjectilePic(pic)
			drawProjectilePic(surface, pic, pos, frame, angle)