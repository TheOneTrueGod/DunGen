print "Loading Pygame."
import pygame
print "Pygame Loaded.  Initializing."
pygame.init()
print "Pygame Initialized."
import Game, os, Units
from Globals import *

def PlayGame(fileNum):
	MG = Game.MainGame()
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

_done = False
fullscreen = 0
if FULLSCREEN == 1:
	fullscreen = pygame.FULLSCREEN
PTRS["SURFACE"] = pygame.display.set_mode(SCREENSIZE, fullscreen)
PTRS["SURFACE"].fill([0] * 3)
selected = -1
startWith = -1
while not _done:
	for ev in pygame.event.get():
		if ev.type == QUIT:
			_done = True
			sys.exit()
		elif ev.type == MOUSEBUTTONDOWN:
			for i in range(3):
				if 310 < ev.pos[0] < 510 and 110 + 110 * i < ev.pos[1] < 110 + 110 * i + 100:
					if selected == i:
						startWith = i
					else:
						selected = i
	if startWith != 0:
		PlayGame(startWith)
	for i in range(3):
		clr = [255] * 3
		if i == selected:
			clr = [255, 255, 0]
		pygame.draw.rect(PTRS["SURFACE"], clr, [310, 110 + 110 * i, 200, 100], 1)
	pygame.display.update()
	PTRS["SURFACE"].fill([0] * 3)