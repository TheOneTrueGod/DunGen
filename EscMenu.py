from Globals import *
import Code.Units.Guilds as Guilds, Code.Units.Equipment as Equipment
import pygame

#################
###  General  ###
#################
def drawGlobalMenu(units, cams, currState):
	on = 0
	for c in cams:
		text = ["Inventory", "Abilities", "Guilds", "Gods", "Blank"]
		for i in range(len(text)):
			drawTextBox(c.getSurface(), [15 + 75 * i, 20], [70, 25], text[i], True, bckClr = [0 + 255 * (currState[on] == i + 1)] * 3, txtClr = [255 - 255 * (currState[on] == i + 1)] * 3)
		on += 1
				
def globalMenuCheckCurrStateInput(mPos, currState):
	for i in range(5):
		if buttonHit(mPos, [[15 + 75 * i, 20], [70, 25]]):
			return i + 1
	return currState
########################
###  Equipment Menu  ###
########################
equipmentPositions = [[0, 60], [0, 310], [10, 100]]	
equipmentBorder = pygame.image.load(os.path.join("Data", "Pics", "Equipment", "EmptySlot.png"))
def drawEquipmentMenu(character, cam, hoveringEquip):
	topLeft = equipmentPositions[0]
	on = 0
	for item in character.getEquippedItems():
		if item:
			iconPos = item.getImage()
		else:
			iconPos = Equipment.EmptyPics[on]
		pos = [topLeft[0] + 8 + on % 13 * 30, topLeft[1] + on / 13 * 30]
		cam.getSurface().blit(equipmentBorder, pos)
		if iconPos:
			drawItemIcon(cam.getSurface(), pos, iconPos)
		on += 1
		
	topLeft = equipmentPositions[1]
	on = 0
	for item in character.getInventoryList():
		if item:
			iconPos = item.getImage()
		else:
			iconPos = None
		pos = [topLeft[0] + 8 + on % 13 * 30, topLeft[1] + on / 13 * 30]
		cam.getSurface().blit(equipmentBorder, pos)
		if iconPos:
			drawItemIcon(cam.getSurface(), pos, iconPos)
		on += 1
		
	if hoveringEquip:
		string = ""
		if hoveringEquip[0] == 1:
			item = character.getEquippedItem(hoveringEquip[1])
			if item:
				string = item.getDescription()
		else:
			item = character.getInventoryItem(hoveringEquip[1])
			if item:
				string = item.getDescription()
		drawTextBox(cam.getSurface(), equipmentPositions[2], [380, 200], string, True)
		
def getInventoryItemNum(mPos, cam):
	pos = [mPos[0] - cam.getScreenPosition()[0], mPos[1] - cam.getScreenPosition()[1]]
	if 0 < pos[0] <= 400 - 5 and equipmentPositions[1][1] < pos[1] - 3 < equipmentPositions[1][1] + 90:
		itemNum = (pos[0] - equipmentPositions[1][0] - 5) / 30 + (pos[1] - equipmentPositions[1][1] + 3) / 30 * 13
		return itemNum
	return -1
	
def getEquippedItemNum(mPos, cam):
	pos = [mPos[0] - cam.getScreenPosition()[0], mPos[1] - cam.getScreenPosition()[1]]
	if 0 < pos[0] <= 400 - 5 and equipmentPositions[0][1] < pos[1] - 3 < equipmentPositions[0][1] + 30:
		itemNum = (pos[0] - equipmentPositions[0][0] - 5) / 30 + (pos[1] - equipmentPositions[0][1] + 3) / 30 * 13
		return itemNum
	return -1
		
def handleEquipmentEvent(ev, character, cam, hoveringEquip):
	if ev.type == MOUSEBUTTONDOWN:
		itemNum = getInventoryItemNum(ev.pos, cam)
		if itemNum != -1:
			character.equipItem(itemNum)
		itemNum = getEquippedItemNum(ev.pos, cam)
		if itemNum != -1:
			character.unequipItem(itemNum)
	elif ev.type == MOUSEMOTION:
		itemNum = getInventoryItemNum(ev.pos, cam)
		if character.getInventoryItem(itemNum) != None:
			return [0, itemNum]
		itemNum = getEquippedItemNum(ev.pos, cam)
		if character.getEquippedItem(itemNum) != None:
			return [1, itemNum]
	return hoveringEquip
######################
###  Ability Menu  ###
######################
abilityPositions = [[5, 60], [5, 220], [10, 110]]	
def drawAbilityMenu(character, cam, hoveringAbil):
	if character:
		on = 0
		for abil in character.getLearnedAbilities():
			if abil:
				pos = (15 + abilityPositions[1][0] + on % 8 * 45, abilityPositions[1][1] + on / 8 * 45)
				drawAbilIcon(cam.getSurface(), pos, abil.icon, "BattleFrame")
			on += 1
		#Setup the 'equipped' ability slots
		for slot in range(ABILITYSLOTS):
			pos = (15 + abilityPositions[0][0] + slot % 8 * 45, abilityPositions[0][1] + slot / 8 * 45)
			abil = character.getSelectedAbil(slot)
			icon = None
			if abil:
				icon = abil.icon
			drawAbilIcon(cam.getSurface(), pos, icon, "BattleFrame")
			
	if hoveringAbil:
		string = hoveringAbil[1].getDescription(hoveringAbil[1])
		drawTextBox(cam.getSurface(), abilityPositions[2], [380, 100], string, True)
	
def getLearnedAbilNum(mPos, cam):
	pos = [mPos[0] - cam.getScreenPosition()[0], mPos[1] - cam.getScreenPosition()[1]]
	if abilityPositions[1][0] < pos[0] - 13 <= abilityPositions[1][0] + 45 * 8 - 1 and abilityPositions[1][1] < pos[1] + 2 < abilityPositions[1][1] + 45*5:
		abilNum = (pos[0] - 13 - abilityPositions[1][0]) / 45 + (pos[1] - abilityPositions[1][1] + 2) / 45 * 8
		return abilNum
	return -1
	
def getEquippedAbilNum(mPos, cam):
	pos = [mPos[0] - cam.getScreenPosition()[0], mPos[1] - cam.getScreenPosition()[1]]
	if abilityPositions[0][0] < pos[0] - 13 <= 400 and abilityPositions[0][1] < pos[1] + 2 < abilityPositions[0][1] + 45:
		abilNum = (pos[0] - 13 - abilityPositions[0][0]) / 45 + (pos[1] - abilityPositions[0][1] + 2) / 45 * 13
		return abilNum
	return -1
	
def handleAbilityEvent(ev, character, cam, hoveringAbil):
	if ev.type == MOUSEBUTTONDOWN:
		abilNum = getLearnedAbilNum(ev.pos, cam)
		if abilNum != -1:
			character.equipAbil(abilNum)
		abilNum = getEquippedAbilNum(ev.pos, cam)
		if abilNum != -1:
			character.unEquipAbil(abilNum)
	elif ev.type == MOUSEMOTION:
		abilNum = getLearnedAbilNum(ev.pos, cam)
		if character.getLearnedAbil(abilNum) != None:
			return [0, character.getLearnedAbil(abilNum)]
		abilNum = getEquippedAbilNum(ev.pos, cam)
		if character.getEquippedAbil(abilNum) != None:
			return [1, character.getEquippedAbil(abilNum)]
	return hoveringAbil
####################
###  Guild Menu  ###
####################
guildTopLeftPos = (30, 80)
guildInfoSize = 80
def drawGuildMenu(character, cam, hoveringAbil):
	pos = [guildTopLeftPos[0], guildTopLeftPos[1]]
	for i in range(Guilds.GuildInfo.NumGuilds):
		cam.getSurface().blit(Guilds.GuildInfo.Pictures[i], pos)
		drawCenteredText(cam.getSurface(), (pos[0] + 25, pos[1] + 58), Guilds.GuildInfo.Names[i], [255] * 3, FONTS["GUILDNAMEFONT"])
		drawText(cam.getSurface(), (pos[0] + 25 + 45, pos[1] + 50), str(character.guilds.getLevel(i)), [255] * 3, FONTS["GUILDNAMEFONT"])
		
		starTopLeft = [pos[0] + 67, pos[1]]
		starsLeft = min(character.guilds.getLevel(i), 255)
		starOn = 0
		for modNum in [4*4*4, 4*4, 4, 1]:
			for j in range(int(starsLeft / modNum)):
				drawPos = [starTopLeft[0] + j * 5, starTopLeft[1]]
				cam.getSurface().blit(Guilds.GuildInfo.GuildStars.subsurface([(3 - starOn) * 13, 0], [13, 13]), drawPos)
			starTopLeft[1] += 12
			starsLeft = starsLeft % modNum
			starOn += 1
			
		rPos = [pos[0] + 55, pos[1]]
		rSize = [10, 50]
		expPct = character.guilds.getExperiencePct(i)
		pygame.draw.rect(cam.getSurface(), EXPERIENCECOLOUR, [[rPos[0], rPos[1] + rSize[1] - 1], [rSize[0], -int((rSize[1] - 2) * expPct)]])
		pygame.draw.rect(cam.getSurface(), [255] * 3, [rPos, rSize], 1) 
		
		infoTopLeft = [pos[0] + 92, pos[1]]
		drawText(cam.getSurface(), infoTopLeft, "Next Level: " + str(int(character.guilds.getExperienceToLevel(i))), [255] * 3, FONTS["TEXTBOXFONT"])
		infoTopLeft[1] += 15
		nextAbil = int(character.guilds.getNextAbility(i))
		if nextAbil == -1:
			nextAbil = "-"
		nextAbil = str(nextAbil)
		drawText(cam.getSurface(), infoTopLeft, "Next Ability: " + nextAbil, [255] * 3, FONTS["TEXTBOXFONT"])
		
		if i == character.guilds.getActiveGuildIndex():
			pygame.draw.rect(cam.getSurface(), [255, 255, 0], [[pos[0] - 30 / 2, pos[1] - 10], [400 - 30, 80]], 1)
		
		pos = (pos[0], pos[1] + guildInfoSize)
	
def handleGuildEvent(ev, character, cam, hoveringGuild):
	if ev.type == MOUSEBUTTONDOWN:
		pos = [ev.pos[0] - cam.getScreenPosition()[0], ev.pos[1] - cam.getScreenPosition()[1]]
		if 0 <= pos[0] <= 400:
			guildNum = (pos[1] - guildTopLeftPos[1] + 10) / guildInfoSize
			character.guilds.setGuild(guildNum)
		
###################
###  Gods Menu  ###
###################
godPics = pygame.image.load(os.path.join("Data", "Pics", "Gods", "godPics.png"))
worshipEffect = pygame.image.load(os.path.join("Data", "Pics", "Gods", "worshipEffect.png"))
def drawGodMenu(character, cam, hoveringAbil):
	barHeight = 20
	barWidth = 200
	barPos = [80, 60]
	centerWidth = 10
	fieldHeight = 90
	on = 0
	for god in character.favour.gods:
		posOffset = 0
		cam.getSurface().blit(godPics.subsurface([[64 * god.Image[0], 63 * god.Image[1]], [64, 63]]), [10, barPos[1] + on * fieldHeight])
		drawCenteredText(cam.getSurface(), [10 + 63 / 2, barPos[1] + on * fieldHeight + 64 + 5], god.DisplayName, [255] * 3, FONTS["GODMENUFONT"])
		favLev = god.getFavourLevel()
		if favLev == 0:
			width = -barWidth / 2 + 1
		elif favLev == len(god.FavourLevels):
			width = barWidth / 2 - 1
		else:
			currFavour = god.favour - god.FavourLevels[favLev - 1]
			width = (currFavour / float(god.FavourLevels[favLev] - god.FavourLevels[favLev - 1]) * 2 - 1) * (barWidth / 2 - 1 - centerWidth / 2 - 1)
			posOffset = signOf(width) * centerWidth / 2 - 1
		barClr = god.getFavourColour()
		
		pygame.draw.rect(cam.getSurface(), barClr, [[barPos[0] + barWidth / 2 + posOffset, barPos[1] + on * fieldHeight + 63 / 2 - barHeight / 2], [width, barHeight]])
		pygame.draw.rect(cam.getSurface(), barClr, [[barPos[0] + barWidth / 2 - centerWidth / 2, barPos[1] + on * fieldHeight + 63 / 2 - barHeight / 2], [centerWidth, barHeight]])
		pygame.draw.rect(cam.getSurface(), [255] * 3, [[barPos[0], barPos[1] + on * fieldHeight + 63 / 2 - barHeight / 2], [barWidth, barHeight]], 1)
		drawCenteredText(cam.getSurface(), [barPos[0] + barWidth / 2, barPos[1] + on * fieldHeight + 63 / 2], god.getFavourName(favLev), [255] * 3, FONTS["GODMENUFONT"])
		
		if god.beingWorshipped:
			imSize = 192 / 2
			cam.getSurface().blit(worshipEffect.subsurface([[int(god.worshipFrame) % 5 * imSize, int(god.worshipFrame / 5) * imSize], [imSize, imSize]]), [10 - 17, barPos[1] + on * fieldHeight - 17])
			god.worshipFrame += 0.5
			god.worshipFrame %= 40
		on += 1
	
def handleGodEvent(ev, character, cam, hoveringGuild):
	if ev.type == KEYDOWN:
		if ev.key == K_LEFT:
			for god in character.favour.gods:
				god.favour -= 10
		elif ev.key == K_RIGHT:
			for god in character.favour.gods:
				god.favour += 10
	elif ev.type == MOUSEBUTTONDOWN:
		pos = [ev.pos[0] - cam.getScreenPosition()[0], ev.pos[1] - cam.getScreenPosition()[1]]
		if 0 <= pos[0] <= 400:
			godIndex = (pos[1] - 60) / 90
			if 0 <= godIndex < len(character.favour.gods):
				g = character.favour.gods[godIndex]
				g.beingWorshipped = not g.beingWorshipped
				g.worshipFrame = 0
	
###################
###  Main Loop  ###
###################
def showMenus(units, cams):
	currState = [4, 1]
	hovering = [None] * 2
	eventFunctions = [handleEquipmentEvent, handleAbilityEvent, handleGuildEvent, handleGodEvent]
	drawFunctions = [drawEquipmentMenu, drawAbilityMenu, drawGuildMenu, drawGodMenu]
	
	_done = False
	while not _done:
		for ev in pygame.event.get():
			if ev.type == QUIT:
				return "QUIT"
			if ev.type == KEYDOWN:
				if ev.key == getPlayerControls(0, "MENUS"):
					return "Okay"
			elif ev.type == MOUSEBUTTONDOWN:
				for on in range(2):
					lastState = currState[on]
					currState[on] = globalMenuCheckCurrStateInput([ev.pos[0] - 400 * on, ev.pos[1]], currState[on])
					if currState[on] != lastState:
						hovering[on] = None
			for on in range(NUMPLAYERS):
				if 0 <= currState[on] - 1 < len(eventFunctions):
					hovering[on] = eventFunctions[currState[on] - 1](ev, PTRS["UNITS"].alliedUnits[on], cams[on], hovering[on])
					
		drawGlobalMenu(units, cams, currState)
		
		on = 0
		for c in cams:
			PTRS["UNITS"].alliedUnits[on].guilds.moveTick()
			if PTRS["UNITS"].alliedUnits[on]:
				if 0 <= currState[on] - 1 < len(drawFunctions):
					drawFunctions[currState[on] - 1](PTRS["UNITS"].alliedUnits[on], c, hovering[on])
					
				PTRS["SURFACE"].blit(c.getSurface(), (400 * on, 0))
			on += 1
		pygame.draw.line(PTRS["SURFACE"], [255] * 3, [400, 0], [400, 600])
			
		pygame.display.update()
		for c in cams:
			c.getSurface().fill([0] * 3)
			