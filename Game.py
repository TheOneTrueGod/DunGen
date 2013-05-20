import pygame
import sys, math, Globals, pickle
import Code.Units.Projectiles as Projectiles, Code.Units.Equipment as Equipment, Code.Units.Guilds as Guilds
import Units as Units
import Code.Engine.Effects as Effects, Code.Engine.Terrain as Terrain, Code.Engine.Traps as Traps
from pygame.locals import *
from Globals import *
from Code.Engine.DungeonGenerator import *
import EscMenu
class Camera:
	def __init__(self, dimensions = [400, 600], cameraNum = 1):
		self.top = 0
		self.left = 0
		self.width = dimensions[0]
		self.height = dimensions[1]
		self.surface = pygame.Surface([self.width, self.height])
		self.cameraNum = cameraNum
		self.floor = 1
		self.shakeTime = 0
		self.shakeAmount = 0
		self.shakeStart = 1
		self.shakeTop = 0
		self.shakeLeft = 0
		
	def shake(self, magnitude, time):
		if time > self.shakeTime or magnitude > self.shakeAmount:
			self.shakeStart = time
			self.shakeTime = time
			self.shakeAmount = magnitude
		
	def getScreenPosition(self):
		if self.cameraNum == 1:
			return [0, 0]
		return [400, 0]
		
	def getNum(self):
		return self.cameraNum
		
	def update(self):
		if self.shakeTime > 1:
			self.shakeTime -= 1
			mod = (self.shakeTime / self.shakeStart) * 0.5 + 0.5
			self.shakeTop = random.uniform(-self.shakeAmount * mod, self.shakeAmount * mod)
			self.shakeLeft = random.uniform(-self.shakeAmount * mod, self.shakeAmount * mod)
		else:
			self.shakeTime = 0
			self.shakeTop = 0
			self.shakeLeft = 0
		
	def setPos(self, pos, floor):
		self.left = pos[0] - self.width / 2
		self.top = pos[1] - self.height / 2
		self.floor = floor
	
	def getSurface(self):
		return self.surface
	
	def Top(self):
		return self.top + self.shakeTop
	
	def Left(self):
		return self.left + self.shakeLeft
		
	def Width(self):
		return self.width
		
	def Height(self):
		return self.height
		
	def Right(self):
		return self.left + self.width
		
	def Bottom(self):
		return self.top + self.height
		
class MainGame:
	def __init__(self):
		self.equipmentBorder = pygame.image.load(os.path.join("Data", "Pics", "Equipment", "EmptySlot.png"))
		
	def getLocalMousePos(self, mPos, camera):
		toRet = (int(min(mPos[0] + camera.Left(), PTRS["TERRAIN"].getWorldSize()[0] - 1) / TILESIZE[0]), 
						 int(min(mPos[1] + camera.Top(), PTRS["TERRAIN"].getWorldSize()[1] - 1) / TILESIZE[1]))
		return toRet
		
	def streamQueuedPieces(self):
		for u in PTRS["UNITS"].getPlayers():
			GetDungeonGrid(u.floor).streamQueuedPieces()
		
	def update(self, cams):
		PTRS["BULLETS"].update()
		PTRS["EFFECTS"].update()
		PTRS["UNITS"].update(cams)
		for c in cams:
			c.update()
		floorsDone = {}
		for u in PTRS["UNITS"].getPlayers():
			if u.floor not in floorsDone:
				floorsDone[u.floor] = True
				GetDungeonGrid(u.floor).update()
				GetTerrain(u.floor).update()
		
	def drawStatusBar(self, unit, camera, currVal, actualVal, maxVal, barRect, realColour, risingColour, droppingColour):
		#Curr, Actual
		currPct = actualVal / float(maxVal)
		actualPct = currVal / float(maxVal)
		realAmt = min(max(int(barRect[1][0] * actualPct), 1), barRect[1][0])
		targAmt = min(max(int(barRect[1][0] * currPct), 1), barRect[1][0])
		if actualVal > currVal:
			pygame.draw.rect(camera.getSurface(), risingColour, [barRect[0], [targAmt, barRect[1][1]]]) #Bright green 'target' amount
			if currVal > 0:
				pygame.draw.rect(camera.getSurface(), realColour, [barRect[0], [realAmt, barRect[1][1]]]) #Bright red 'real' amount
		elif actualVal < currVal:
			pygame.draw.rect(camera.getSurface(), droppingColour, [barRect[0], [realAmt, barRect[1][1]]]) #Dark red 'dropping amount'
			if actualVal > 0:
				pygame.draw.rect(camera.getSurface(), realColour, [barRect[0], [targAmt, barRect[1][1]]]) # Bright red 'real' amount
		else:
			pygame.draw.rect(camera.getSurface(), realColour, [barRect[0], [realAmt, barRect[1][1]]]) #Bright red health
		
		pygame.draw.rect(camera.getSurface(), [255] * 3, barRect, 1)
		
		drawCenteredText(camera.getSurface(), 
						(barRect[0][0] + barRect[1][0] / 2, 
						 barRect[0][1] + barRect[1][1] / 2), 
					str(int(currVal)) + "/" + str(int(maxVal)), [255] * 3, FONTS["HPBARFONT"])
		
	def drawHUD(self, unitOn, camera):
		HEALTHSIZE = 100
		unit = PTRS["UNITS"].alliedUnits[unitOn]
		if unit:
			if unit.getTargetHealth() > 0 or unit.getHealth() > 0:
				healthBarRect = [[10, camera.Height() - 20], [HEALTHSIZE, 12]]
				expBarRect = [[10, camera.Height() - 40], [HEALTHSIZE, 12]]
				self.drawStatusBar(unit, camera, unit.getHealth(), unit.getTargetHealth(), unit.getMaxHealth(), healthBarRect,
																				[255, 0, 0], [0, 255, 0], [155, 0, 0])
				self.drawStatusBar(unit, camera, unit.guilds.getActiveGuild().experience, unit.guilds.getActiveGuild().targetExperience,
																				unit.guilds.getActiveGuild().getExperienceRequirement(), expBarRect,
																				EXPERIENCECOLOUR, DARKEXPERIENCECOLOUR, [255, 255, 255])

			for i in range(ABILITYSLOTS):
				abil = unit.getSelectedAbil(i)
				if abil:
					icon = abil.icon
					if i == unit.selectedAbil:
						frameIcon = "SelectedFrame"
					else:
						frameIcon = "BattleFrame"
					
					pos = (5 + i * 45, 5)
					if abil.cooldown[0] > 0:
						drawAbilIcon(camera.getSurface(), pos, icon, frameIcon, abil.cooldown[0] / float(abil.cooldown[1]))
					else:
						drawAbilIcon(camera.getSurface(), pos, icon, frameIcon)
			
			if unit.lastHitTargets:
				on = len(unit.lastHitTargets)
				done = 0
				for u in unit.lastHitTargets:
					if not u.isTrainingDummy():
						pos = [camera.Width() - HEALTHSIZE - 10, camera.Height() - 20 - done * 15]
						hPct = u.getHealth() / float(u.getMaxHealth())
						hAmt = min(max(int(HEALTHSIZE * hPct), 1), HEALTHSIZE)
						clr = [150, 0, 0]
						if u == unit.target:
							clr = [255, 0, 0]
						pygame.draw.rect(camera.getSurface(), clr, [pos, [hAmt, 10]]) #Bright red health
						pygame.draw.rect(camera.getSurface(), [255] * 3, [pos, [HEALTHSIZE, 10]], 1)
						if unit.team == 1:
							Units.drawEnemyPic(camera.getSurface(), u.picture, [pos[0] - 15, pos[1]], int(u.animationFrames[int(u.frame)]))
						on -= 1
						done += 1
						if done > 5:
							break
					
		
	def drawMe(self, started, cams, currFps):
		on = 0
		for c in cams:
			if PTRS["UNITS"].alliedUnits[on]:
				GetTerrain(PTRS["UNITS"].alliedUnits[on].floor).drawMe(c)
				GetTerrain(PTRS["UNITS"].alliedUnits[on].floor).drawTraps(c, 0)
				PTRS["EFFECTS"].drawMe(c, 0)
				PTRS["EFFECTS"].drawMe(c, 1)
				PTRS["BULLETS"].drawMe(c)
				GetTerrain(PTRS["UNITS"].alliedUnits[on].floor).drawTraps(c, 1)
				PTRS["UNITS"].drawMe(c, started)
				GetTerrain(PTRS["UNITS"].alliedUnits[on].floor).drawTraps(c, 2)
				PTRS["EFFECTS"].drawMe(c, 2)
				self.drawHUD(on, c)
				pygame.draw.rect(c.getSurface(), [255] * 3, ((0, 0), (c.Width(), c.Height())), 1)
				drawCenteredText(c.getSurface(), [200, 20], str(currFps), [255] * 3, FONTS["TEXTBOXFONT"])
				PTRS["SURFACE"].blit(c.getSurface(), (400 * on, 0))
			on += 1
		if FOGOFWAR:
			PTRS["SURFACE"].blit(PTRS["FOGOFWAR"], (0, 0))
		
		pygame.display.update()
		PTRS["SURFACE"].fill([0] * 3)
		if FOGOFWAR:
			PTRS["FOGOFWAR"].fill([0] * 3)
		for c in cams:
			c.getSurface().fill([0] * 3)
				
	def playStreamingGame(self, units):
		from Code.Units.Stats import loadAllEnemies
		loadAllEnemies(1)
		units[0].targetHealth = units[0].maxHealth
		if NUMPLAYERS == 2:
			units[1].targetHealth = units[1].maxHealth
		LoadDungeon(1)
		isOver = False
		#piece = getRandomDungeonPiece()
		#pos = dungeonGrid.findRandomSpotForPiece(piece)
		#if pos:
		#	dungeonGrid.placePieceAt(pos, piece)
		#	PTRS["TERRAIN"].streamDungeonGrid(dungeonGrid, (pos, (pos[0] + piece.getWidth(), pos[1] + piece.getHeight())), DUNGEONBOXSIZE)
		
		PTRS["UNITS"].setUnits(units)
		PTRS["SURFACE"].fill([0] * 3)
		pygame.display.update()
		gamestate = {"done":False}
		backupFrame = 0
		selected = range(NUMPLAYERS)
		lastTime = 0
		lastSave = AUTOSAVEDELAY
		secondTimer = 0
		frameCount = 0
		currFps = 0
		if NUMPLAYERS == 1:
			cams = [Camera((800, 600), 1)]
		elif NUMPLAYERS == 2:
			cams = [Camera((400, 600), 1), Camera((400, 600), 2)]
		for i in range(min(NUMPLAYERS, len(selected))):
			PTRS["UNITS"].selectUnit(selected[i], i + 1)
		PTRS["UNITS"].startBattle(selected)
		PTRS["UNITS"].save()
		while not gamestate["done"]:
			for ev in pygame.event.get():
				if ev.type == QUIT:
					PTRS["UNITS"].save()
					pygame.display.quit()
					return "QUIT"
				elif ev.type in [KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP]:
					PTRS["KEYS"].handleEvent(ev)
				if ev.type == KEYDOWN:
					#alt-f4
					if ev.mod == 256 and ev.key == 285:
						return "QUIT"
					if ev.key == getPlayerControls(0, "MENUS"):
						result = EscMenu.showMenus(units, cams)
						if result == "QUIT":
							PTRS["UNITS"].save()
							pygame.display.quit()
							return "QUIT"
							
			if pygame.time.get_ticks() - secondTimer > 1000:
				currFps = frameCount
				secondTimer = pygame.time.get_ticks()
				frameCount = 0
					
			time = pygame.time.get_ticks()
			if time - lastTime > MINFPS:
				frameCount += 1
				lastSave -= 1
				if lastSave <= 0:
					lastSave = AUTOSAVEDELAY
					#PTRS["UNITS"].save()
				lastTime = time
				self.streamQueuedPieces()
				self.update(cams)
				for i in range(NUMPLAYERS):
					PTRS["UNITS"].readjustCamera(cams[i], i)
				self.drawMe(True, cams, currFps)
				PTRS["FRAME"] += 1
				PTRS["KEYS"].flush()
		pygame.display.quit()
		

if "Game.py" in sys.argv[0]:
	fullscreen = 0
	if FULLSCREEN == 1:
		fullscreen = pygame.FULLSCREEN
	PTRS["SURFACE"] = pygame.display.set_mode(SCREENSIZE, fullscreen)
	PLAYERFILES[0] = os.path.join("Profiles", "asdf.prof")
	PLAYERFILES[1] = os.path.join("Profiles", "asdf2.prof")
	MG = MainGame()
	if FORCERELOAD or "-r" in sys.argv:
		units = [Units.PlayerUnit("asdf", 1)]
		if NUMPLAYERS == 2:
			units += [Units.PlayerUnit("asdf2", 1)]
		MG.playStreamingGame(units)
	else:
		units = [pickle.load(open(os.path.join("Profiles", "asdf.prof")))]
		if NUMPLAYERS == 2:
			units += [pickle.load(open(os.path.join("Profiles", "asdf2.prof")))]
		MG.playStreamingGame(units)