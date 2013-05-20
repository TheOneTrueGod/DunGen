import pygame, os
from pygame.locals import *
surface = pygame.display.set_mode((200, 200), 0)

def intOf(list):
	return [int(k) for k in list]

def loadEnemyList(level):
	fileIn = open(os.path.join("Data", "Enemies", str(level), "EnemyList.txt"))
	on = 0
	for line in fileIn:
		if line[0] != "#":
			line = line.strip().split()
			TL = intOf([line[1], line[3]])
			BR = intOf([line[2], line[4]])
			pos = [TL[0] + 100, TL[1] + 100]
			width = [BR[0] - TL[0], BR[1] - TL[1]]
			pygame.draw.rect(surface, [255 - on * 15, 255 - on * 15, 255 - on * 15], (pos, width))
			on += 1

loadEnemyList(1)
pygame.draw.circle(surface, [0, 0, 255], [2, 100], 2)
pygame.draw.circle(surface, [128, 64, 64], [198, 100], 2)

pygame.draw.circle(surface, [0, 255, 255], [100, 2], 2)
pygame.draw.circle(surface, [255, 0, 0], [100, 198], 2)
pygame.display.update()
done = False
while not done:
	for ev in pygame.event.get():
		if ev.type == KEYDOWN or ev.type == QUIT:
			done = True