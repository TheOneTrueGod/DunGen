import pygame, random
from Globals import *
class EffectStruct:
	def __init__(self):
		self.effects = {0:[], 1:[], 2:[]}
		
	def addEffect(self, effect, layer = 2): #layer 2 - on top of everything. #layer 1 - behind projectiles. #layer 0 - behind units
		self.effects[layer] += [effect]
		
	def update(self):
		for effectLayer in self.effects:
			i = 0
			while i < len(self.effects[effectLayer]):
				self.effects[effectLayer][i].update()
				if self.effects[effectLayer][i].readyToDelete():
					del self.effects[effectLayer][i]
				else:
					i += 1
		
	def drawMe(self, camera, layer):
		for effect in self.effects[layer]:
			effect.drawMe(camera)
		
class Effect:
	def __init__(self):
		self.time = 0
		
	def update(self):
		self.time -= 1
		
	def readyToDelete(self):
		return True
		
	def drawMe(self, camera):
		return
		
class WeaponFadeEffect(Effect):
	def __init__(self, picture, pos, duration, angle):
		self.picture = picture
		self.pos = pos
		self.time = duration
		self.startTime = duration
		self.angle = angle
		
	def readyToDelete(self):
		return self.time <= 0
		
	def drawMe(self, camera):
		p = (self.pos[0] - camera.Left(), self.pos[1] - camera.Top())
		alpha = self.time / float(self.startTime)
		drawProjectilePic(camera.getSurface(), self.picture, p, 1, self.angle, alpha=alpha)
		
class FlashingSquare(Effect):
	def __init__(self, coord, floor, time):
		self.coord = coord
		self.floor = floor
		self.time = time
		self.midTime = self.time / 2
	
	def update(self):
		self.time -= 1
		
	def delete(self):
		self.time = -1
		
	def readyToDelete(self):
		return self.time <= 0
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		if True:
			pos = [self.coord[0] * TILESIZE[0] - camera.Left() + 1, self.coord[1] * TILESIZE[1] - camera.Top() + 1]
			
			temp_surf = pygame.Surface([TILESIZE[0] - 2, TILESIZE[1] - 2])
			alpha = int((1 - math.fabs(self.midTime - self.time) / float(self.midTime)) * 124)
			temp_surf.set_alpha(alpha)
			temp_surf.fill([255, 255, 0])
			
			camera.getSurface().blit(temp_surf, pos)		
		
class CircleEffect(Effect):
	def __init__(self, pos, floor, radius, time, clr = [255, 255, 122], startAlpha = 255):
		self.pos = pos
		self.floor = floor
		self.radius = radius
		self.time = time
		self.alpha = startAlpha
		self.clr = clr
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
	
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = (int(self.pos[0] - camera.Left()), int(self.pos[1] - camera.Top()))
		size = int(self.radius)
		alpha = int(self.alpha)
		camera.getSurface().blit(create_transparent_circle(self.clr, alpha, size), [pos[0] - size, pos[1] - size])
		
class DiminishingCircleEffect(CircleEffect):
	def __init__(self, pos, floor, radius, time):
		CircleEffect.__init__(self, pos, floor, radius, time)
		self.deltaRad = (radius / 2.0) / float(time)
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		
	def update(self):
		self.time -= 1
		self.radius -= self.deltaRad
		self.alpha -= self.deltaAlpha
		
class PictureEffect(Effect):
	def __init__(self, picture, pos, floor, time=60):
		self.pos = [pos[0], pos[1]]
		self.floor = floor
		self.time = time
		self.alpha = 255
		self.deltaY = random.uniform(-2.4, -1.6)
		self.picture = picture
		if self.picture not in EFFECTPICS and self.picture != None:
			path = os.path.join("Data", "Pics", "Effects", self.picture + ".png")
			if not os.path.exists(path):
				path = os.path.join("Data", "Pics", "Effects", "Exclamation.png")
				print "ERROR: EFFECT PIC NOT FOUND:", self.picture
			EFFECTPICS[self.picture] = pygame.image.load(path)
			EFFECTPICS[self.picture].set_colorkey([255, 0, 255])
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
		self.pos = [self.pos[0], self.pos[1] + self.deltaY]
		self.deltaY *= 0.9
	
	def drawMe(self, camera):
		if camera.floor != self.floor or self.picture == None:
			return
		if self.time > 20 or self.time % 5 not in [2, 3]:
			pos = (int(self.pos[0] - EFFECTPICS[self.picture].get_width() / 2 - camera.Left()), int(self.pos[1] - EFFECTPICS[self.picture].get_height() / 2 - camera.Top()))
			camera.getSurface().blit(EFFECTPICS[self.picture], pos)
			
class FadingBuffEffect(PictureEffect):
	def __init__(self, iconPos, pos, floor, time = 60):
		PictureEffect.__init__(self, "Debuffs", pos, floor, time)
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		self.deltaPos = [random.uniform(-0.3, 0.3), random.uniform(-0.4, -0.8)]
		self.iconPos = iconPos
		
	def update(self):
		self.time -= 1
		self.pos = [self.pos[0] + self.deltaPos[0], self.pos[1] + self.deltaPos[1]]
		self.alpha -= self.deltaAlpha
	
	def drawMe(self, camera):
		buffPicSize = 34
		pos = (int(self.pos[0] - camera.Left() - buffPicSize / 2), int(self.pos[1] - camera.Top() - buffPicSize / 2))
		alpha = int(self.alpha)
		toDraw = EFFECTPICS["Debuffs"].subsurface([[buffPicSize * self.iconPos[0], buffPicSize * self.iconPos[1]], [buffPicSize, buffPicSize]])
		toDraw.set_alpha(alpha)
		camera.getSurface().blit(pygame.transform.scale(toDraw, (17, 17)), pos)
	
class ItemCollectEffect(PictureEffect):
	def __init__(self, itemPos, unit, floor, time=10):
		PictureEffect.__init__(self, None, unit.getPos(), floor, time)
		self.itemPos = itemPos
		self.unit = unit
		self.angle = random.uniform(0, math.pi * 2)
		self.deltaD = 8
		self.dist = 0
		self.startTime = time
		
	def update(self):
		self.time -= 1
		self.dist += self.deltaD
		self.deltaD -= 0.4
		self.pos = [self.unit.getPos()[0] + math.cos(self.angle) * self.dist, 
								self.unit.getPos()[1] + math.sin(self.angle) * self.dist]
	
	def readyToDelete(self):
		return self.time <= 0 and self.dist <= self.unit.size + ITEMSIZE / 2
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
			
		#if self.time > 20 or self.time % 5 not in [2, 3]:
		pos = (int(self.pos[0] - ITEMSIZE / 2 - camera.Left()), int(self.pos[1] - ITEMSIZE / 2 - camera.Top()))
		drawItemIcon(camera.getSurface(), pos, self.itemPos, 1)
	
class ExplosionEffect(PictureEffect):
	def __init__(self, picture, pos, floor, time=60, numHits=0, abil=None):
		PictureEffect.__init__(self, picture, pos, floor, time)
		self.startTime = time
		self.numFrames = EFFECTPICS[self.picture].get_width() / EFFECTPICS[self.picture].get_height()
		self.numHits = numHits
		self.hitsLeft = numHits
		self.abil=abil
		
	def update(self):
		self.time -= 1
		if self.hitsLeft > 0 and self.abil:
			if self.time <= (self.startTime / float(self.numHits)) * self.hitsLeft:
				self.hitsLeft -= 1
				self.abil.hitTick(self.pos)
		
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = (int(self.pos[0] - EFFECTPICS[self.picture].get_height() / 2 - camera.Left()), int(self.pos[1] - EFFECTPICS[self.picture].get_height() / 2 - camera.Top()))
		frame = max(min(int((1 - self.time / float(self.startTime)) * self.numFrames), self.numFrames - 1), 0)
		
		pic = EFFECTPICS[self.picture].subsurface([[frame * EFFECTPICS[self.picture].get_height(), 0], 
											[EFFECTPICS[self.picture].get_height(), EFFECTPICS[self.picture].get_height()]])
		camera.getSurface().blit(pic, pos)
		
class FollowingExplosionEffect(ExplosionEffect):
	def __init__(self, picture, target, floor, abil, time=60, numHits = 1):
		ExplosionEffect.__init__(self, picture, target.getPos(), floor, time)
		self.target = target
		self.numHits = numHits
		self.currHit = 0
		self.abil = abil
		
	def update(self):
		self.time -= 1
		self.pos = self.target.getPos()
		if self.time < self.startTime - self.startTime / self.numHits * self.currHit:
			self.currHit += 1
			self.abil.hitTick()
			
class LoopingExplosionEffect(ExplosionEffect):
	def __init__(self, picture, targPos, floor, abil, loopTime, time=60, hitsPerLoop = 1):
		ExplosionEffect.__init__(self, picture, targPos, floor, time)
		self.numHits = 0
		self.hitsPerLoop = hitsPerLoop
		self.loopTime = loopTime
		self.currHit = 0
		self.abil = abil
		self.numFrames = 15
		self.loopsLeft = time / float(loopTime)
		
	def update(self):
		self.time -= 1
		if self.time % self.loopTime == 0:
			self.currHit = 0
			self.loopsLeft -= 1
			
		if self.time % self.loopTime < self.loopTime - self.loopTime / self.hitsPerLoop * self.currHit:
			self.currHit += 1
			self.abil.hitTick(self.pos)
			
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = (int(self.pos[0] - EFFECTPICS[self.picture].get_width() / 5 / 2 - camera.Left()), int(self.pos[1] - EFFECTPICS[self.picture].get_height() / 6 / 2 - camera.Top()))
		frame = max(min(int((1 - self.time % self.loopTime / float(self.loopTime)) * self.numFrames), self.numFrames - 1), 0)
		#print  frame
		yOffset = 0
		if self.loopsLeft <= 1:
			yOffset = 3
		pic = EFFECTPICS[self.picture].subsurface([[frame % 5 * EFFECTPICS[self.picture].get_width() / 5, (frame / 5 + yOffset) * EFFECTPICS[self.picture].get_width() / 5], 
																				[EFFECTPICS[self.picture].get_width() / 5, EFFECTPICS[self.picture].get_width() / 5]])
		camera.getSurface().blit(pic, pos)
		
class CooldownDoneEffect(ExplosionEffect):
	def __init__(self, picture, owner, time=60):
		PictureEffect.__init__(self, picture, owner.getPos(), owner.floor, time)
		self.startTime = time
		self.owner = owner
		self.numFrames = EFFECTPICS[self.picture].get_width() / EFFECTPICS[self.picture].get_height()
		
	def update(self):
		self.time -= 1
		self.pos = self.owner.getPos()
		
class LineEffect(Effect):
	def __init__(self, start, end, floor, radius, time):
		self.pos = [intOf(start), intOf(end)]
		self.floor = floor
		self.radius = radius
		self.time = time
		self.alpha = 255
		self.deltaAlpha = 255 / float(time)
		self.deltaRad = 3 / float(time)
		
	def readyToDelete(self):
		return self.time <= 0
		
	def update(self):
		self.time -= 1
		self.radius += self.deltaRad
		self.alpha -= self.deltaAlpha
	
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		start = intOf(self.pos[0])
		end = intOf(self.pos[1])
		size = int(self.radius)
		alpha = int(self.alpha)
		line = create_transparent_line(end[0] - start[0], end[1] - start[1], [255, 255, 122], alpha, size)
		camera.getSurface().blit(line, [min(end[0], start[0]) - camera.Left(), min(end[1], start[1]) - camera.Top()])
	
class TextEffect(Effect):
	def __init__(self, pos, floor, clr, time, text, size=1):
		self.pos = pos
		self.floor = floor
		self.type = "Text"
		self.time = time
		self.clr = clr
		self.deltaPos = [random.uniform(-1, 1), random.uniform(-2, -5)]
		self.deltaPos += [self.deltaPos[1] * -(random.uniform(1, 3)) / float(time)]
		self.text = text
		self.inc = (clr[0] / float(time),clr[1] / float(time),clr[2] / float(time))
		self.size = size
	
	def readyToDelete(self):
		return self.time <= 0
	
	def update(self):
		self.time -= 1
		#self.pos = (self.pos[0], self.pos[1] - 0.9 * self.calcTimeRate())
		self.pos = (self.pos[0] + self.deltaPos[0], self.pos[1] + self.deltaPos[1])
		self.deltaPos[1] += self.deltaPos[2]
		self.clr = (self.clr[0] - self.inc[0], 
					self.clr[1] - self.inc[1], 
					self.clr[2] - self.inc[2])
	
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		pos = [self.pos[0] - camera.Left(), self.pos[1] - camera.Top()]
		if self.size == 0:
			font = FONTS["EFFECTFONTSMALL"]
		elif self.size == 1:
			font = FONTS["EFFECTFONT"]
		else:
			font = FONTS["EFFECTFONTLARGE"]
		camera.getSurface().blit(font.render(self.text, False, self.clr), pos)

class DamageTextEffect(TextEffect):
	def __init__(self, pos, floor, clr, time, text, size=1):
		TextEffect.__init__(self, pos, floor, clr, time, text, size)
		
class SpellEffect(ExplosionEffect):
	def __init__(self, picture, targPos, floor, time=60, centered = True, numFrames = None, follow=None):
		ExplosionEffect.__init__(self, picture, targPos, floor, time)
		self.numHits = 0
		self.frame = 0
		self.imageWidth = EFFECTPICS[self.picture].get_width() / 5
		if numFrames == None:
			self.numFrames = EFFECTPICS[self.picture].get_height() / self.imageWidth * 5
		else:
			self.frame = numFrames[0]
			self.numFrames = numFrames[1]
		self.frameRate = float(self.numFrames - self.frame) / float(time)
		self.centered = centered
		self.following = follow
		
	def update(self):
		self.frame += self.frameRate
		if self.following != None:
			self.pos = self.following.getPos()
			
	def readyToDelete(self):
		return self.frame >= self.numFrames
			
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		if self.centered:
			pos = (int(self.pos[0] - self.imageWidth / 2 - camera.Left()), int(self.pos[1] - self.imageWidth / 2 - camera.Top()))
		else:
			pos = self.pos
		frame = self.frame
		pic = EFFECTPICS[self.picture].subsurface([[int(frame) % 5 * self.imageWidth, (int(frame) / 5) * self.imageWidth], 
																							[self.imageWidth, self.imageWidth]])
		camera.getSurface().blit(pic, pos)
	
def create_transparent_line(width, height, color, alpha, radius=1):
	size = radius * 2
	temp_surf = pygame.Surface((math.fabs(width) + radius, math.fabs(height) + radius))
	temp_surf.set_alpha(int(alpha))
	temp_surf.fill([122, 13, 75])
	temp_surf.set_colorkey([122, 13, 75])
	if signOf(width) != signOf(height):
		start = [0, math.fabs(height)]
		end = [math.fabs(width), 0]
	else:
		start = [0, 0]
		end = [math.fabs(width), math.fabs(height)]
	pygame.draw.line(temp_surf, color, start, end, radius)

	return temp_surf
	
def create_transparent_circle(color, alpha, radius, width=0):
	size = radius * 2
	temp_surf = pygame.Surface((size, size))
	temp_surf.set_alpha(int(alpha))
	temp_surf.fill([122, 13, 75])
	temp_surf.set_colorkey([122, 13, 75])
	pygame.draw.circle(temp_surf, color, (radius, radius), radius, width)
	return temp_surf
	
PTRS["EFFECTS"] = EffectStruct()