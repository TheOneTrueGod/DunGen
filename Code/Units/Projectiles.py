import math
import Code.Engine.Effects as Effects
import Code.Units.Buffs as Buffs
from Globals import *

def getNumFrames(pic):
	if type(pic) == type([]):
		return 1
	else:
		global PROJECTILEPICTURES
		if pic not in PROJECTILEPICTURES:
			PROJECTILEPICTURES[pic] = loadProjectilePic(pic)
		return len(PROJECTILEPICTURES[pic])
		
class Bullet:
	def __init__(self, pos, floor, endPos):
		self.drawn = False
		self.floor = floor
		self.pos = [pos[0], pos[1]]
		self.endPos = [endPos[0], endPos[1]]
	
	def readyToDelete(self):
		return self.drawn
		
	def update(self):
		PTRS["EFFECTS"].addEffect(Effects.LineEffect(self.pos, self.floor, self.endPos, 1, 20))
			
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		start = [int(self.pos[0] / gridsize), int(self.pos[1] / gridsize)]
		end = [int(self.endPos[0] / gridsize), int(self.endPos[1] / gridsize)]
		
		#for pos in raytrace(start, end):
		#	g = gridsize
		#	gridPos = [int(pos[0]), int(pos[1])]
		#	pygame.draw.rect(surface, [255, 255, 0], [[gridPos[0] * g, gridPos[1] * g], [g, g]])
		#	pygame.draw.rect(surface, [0, 255, 0], [[gridPos[0] * g, gridPos[1] * g], [g, g]], 1)
		
		#pygame.draw.line(surface, [255, 0, 0], self.pos, self.endPos)
		self.drawn = True
		
class ProjectileShot:
	def __init__(self, abil, user, target, attack, damageMod=1, angleOffset = 0, range=150, picture="NoPic", projectileSpeed=1, homing=True, hitsAnyone=True, startPos=None, startAng = 0, pierces = False, hitsAllies = False, maxUnitsHit = -1):
		self.initOptions()
		self.attack = attack
		self.damageMod = damageMod
		self.abil = abil
		self.floor = user.floor
		self.picture = picture
		self.maxTurnAngle = math.pi / 3.0
		if startPos == None:
			self.pos = user.getPos()
		else:
			self.pos = startPos
		self.target = target
		self.angle = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0]) + angleOffset
		self.angleOffset = angleOffset
		self.speed = projectileSpeed
		self.time = range / self.speed
		self.range = range
		self.startTime = self.time
		self.user = user
		self.rotationSpeed = math.pi / 100.0
		self.homing = homing
		self.hitsAnyone = hitsAnyone
		self.pierces = pierces
		self.unitsHit = {}
		self.size = 0
		self.hitsAllies = hitsAllies
		self.drawAngle = startAng
		self.maxUnitsHit = maxUnitsHit
		self.childInit()
		
	def linkProjectiles(self, otherProjectile):
		self.unitsHit = otherProjectile.unitsHit
		
	def initOptions(self):
		self.homing = False
		self.hitsAnyone = True
		self.pierces = False
		self.hitsAllies = False
		self.ignoresWalls = False
		self.unitsHit = {}
		
	def childInit(self):
		pass
		
	def deflect(self, unit):
		self.angle = math.atan2(self.pos[1] - unit.getPos()[1], self.pos[0] - unit.getPos()[0])
		self.hitsAllies = True
		self.hitsAnyone = True
		
	def collisionCheck(self, target):
		if dist(target.getPos(), self.pos) <= target.size + self.size and target not in self.unitsHit and (self.maxUnitsHit == -1 or len(self.unitsHit) < self.maxUnitsHit):
			return True
		return False
			
	def update(self):
		self.updatePosition()
		if self.hitsAnyone or self.target.isTrainingDummy():
			for u in PTRS["UNITS"].getTargets(self.user.team, self.hitsAllies, True):
				if self.collisionCheck(u):
					if random.random() <= u.getKeyword("Shield"):
						self.deflect(u)
						self.unitsHit[u] = True
					else:
						self.abil.hitTarget(u, self.angle, self.attack, self.damageMod)
						self.unitsHit[u] = True
						if not self.pierces:
							self.time = -1
						break
		else:
			if not self.target.isTrainingDummy() and self.collisionCheck(self.target):
				if random.random() <= self.target.getKeyword("Shield"):
					self.deflect(self.target)
					self.unitsHit[self.target] = True
				else:
					self.unitsHit[self.target] = True
					self.abil.hitTarget(self.target, self.angle, self.attack, self.damageMod)
					self.time = -1
		if not self.ignoresWalls and GetTerrain(self.floor).getAtPos(self.pos) == 1:
			self.time = -1
		self.time -= 1
		if self.time <= 0:
			pass
		if self.homing:
			self.updateAngleFacing()
			
	def updatePosition(self):
		self.pos = [self.pos[0] + math.cos(self.angle) * self.speed, self.pos[1] + math.sin(self.angle) * self.speed]
			
	def updateAngleFacing(self):
		targAng = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0]) #+ self.angleOffset
		selfAng = self.angle % (math.pi * 2)
		angDiff = getAngDiff(selfAng, targAng)
		if math.fabs(angDiff) > self.maxTurnAngle:
			return
		rotationSpeed = self.rotationSpeed
		if math.fabs(angDiff) < rotationSpeed:
			self.angle = targAng
		else:
			self.angle = (self.angle + max(min(angDiff, rotationSpeed), -rotationSpeed)) % (math.pi * 2)
			
	def readyToDelete(self):
		return self.time <= 0
	
	def drawMe(self, camera):
		if camera.floor != self.floor:
			return
		p = (self.pos[0] - camera.Left(), self.pos[1] - camera.Top())
		drawProjectilePic(camera.getSurface(), self.picture, p, int((self.time / 5) % getNumFrames(self.picture)), int(self.drawAngle * 180 / math.pi))

class MeleeAttack(ProjectileShot):
	def childInit(self):
		if self.user.getHand() == 0:
			self.angMult = 1
		else:
			self.angMult = -1
			
		self.size = ICONSIZE / 8
		self.pierces = True
		self.ignoresWalls = False
		self.angSpread = math.pi / 4.0
		self.angOffset = (self.angSpread) * self.angMult
		self.finalAngOffset = -self.angSpread * self.angMult
		self.distStart = self.user.size + (self.range - self.user.size) * 0.3
		self.distEnd = self.range
		self.angFacing = self.user.angle
		self.updateDrawAngleInterval = 3
		self.lastUpdateDrawAngle = 0
		self.startPos = [self.pos[0], self.pos[1]]
		self.rotationSpeed = math.pi / 200.0
		self.drawAngle = self.angle + math.pi / 5.0
		if self.drawAngle == 0:
			self.drawAngle += 0.000000001
	
	def updatePosition(self):
		ProjectileShot.updatePosition(self)
		
	def drawMe(self, camera):
		ProjectileShot.drawMe(self, camera)
			
	"""def updatePosition(self):
		timePct = 1 - self.time / float(self.startTime)
		self.lastUpdateDrawAngle += 1
		if self.lastUpdateDrawAngle >= self.updateDrawAngleInterval:
			self.drawAngle -= math.pi / 2.0
			if self.drawAngle <= 0:
				self.drawAngle += math.pi * 2
			if self.drawAngle > math.pi * 2:
				self.drawAngle -= math.pi * 2
			self.lastUpdateDrawAngle = 0
		angle = self.angOffset + (self.finalAngOffset - self.angOffset) * timePct
		dist = self.distStart + (self.distEnd - self.distStart) * timePct
		self.pos = [self.user.getPos()[0] + math.cos(self.angFacing + angle) * dist, 
								self.user.getPos()[1] + math.sin(self.angFacing + angle) * dist]
		PTRS["EFFECTS"].addEffect(Effects.WeaponFadeEffect(self.picture, self.pos, 8, int(self.drawAngle * 180 / math.pi)))
		
	def drawMe(self, camera):
		pass"""
								
class MeleeAttack2(MeleeAttack):
	def childInit(self):
		MeleeAttack.childInit(self)
		self.time = 1
		
	def updatePosition(self):
		pass

	def collisionCheck(self, target):
		if target not in self.unitsHit and (self.maxUnitsHit == -1 or len(self.unitsHit) < self.maxUnitsHit):
			pos = target.getPos()
			if (self.startPos[0] - pos[0])**2 + (self.startPos[1] - pos[1])**2 <= (self.range + target.size)**2:
				ang = math.atan2(pos[1] - self.startPos[1], pos[0] - self.startPos[0])
				angDiff = (self.angFacing - ang)
				if math.fabs(angDiff) < self.angSpread or math.fabs(angDiff) > math.pi * 2 - self.angSpread:
					return True
		return False
		
	def drawMe(self, camera):
		maxToDraw = 3
		maxFadeTime = 12
		minFadeTime = 8
		swordAngle = int(self.angOffset * 180 / math.pi)
		for i in range(maxToDraw):
			angPct = i / float(maxToDraw)
			angle = self.angOffset + (self.finalAngOffset - self.angOffset) * angPct
			duration = int(minFadeTime + (maxFadeTime - minFadeTime) * i / float(maxToDraw))
			dist = self.distEnd 
			distMod = math.fabs(maxToDraw / 2 - i) / float(maxToDraw)
			dist -= (self.distEnd - self.distStart) * distMod
			pos = [self.user.getPos()[0] + math.cos(self.angFacing + angle) * dist, 
						 self.user.getPos()[1] + math.sin(self.angFacing + angle) * dist]
			PTRS["EFFECTS"].addEffect(Effects.WeaponFadeEffect(self.picture, pos, duration, swordAngle))
			swordAngle += 45
	
class PlayerProjectile(ProjectileShot):
	def childInit(self):
		self.rotationSpeed = math.pi / 15.0
		
class MagicMissile(ProjectileShot):
	def childInit(self):
		self.maxTurnAngle = math.pi * 2.0
		self.rotationSpeed = math.pi / 15.0
		
	def updateAngleFacing(self):
		ProjectileShot.updateAngleFacing(self)
		self.drawAngle = self.angle
		
class SpinnerProjectile:
	def __init__(self, abil, user, target, attack, damageMod=1, picture="NoPic", numShots=4):
		self.attack = attack
		self.damageMod = damageMod
		self.target = target
		self.abil = abil
		self.user = user
		self.picture = picture
		self.pos = self.target.getPos()
		self.angle = random.uniform(0, math.pi * 2)
		self.nextShot = 20
		self.numShots = numShots
		self.shotsLeft = self.numShots
		self.time = 0
		self.floor = user.floor
			
	def update(self):
		self.pos = self.user.getPos()
		self.angle += math.pi / 51.0
		self.nextShot -= 1
		self.time += 1
		if self.nextShot <= 0:
			startPos = (self.pos[0] + math.cos(self.angle + math.pi * 2 / float(self.numShots) * (self.shotsLeft - 1)) * 50, 
									self.pos[1] + math.sin(self.angle + math.pi * 2 / float(self.numShots) * (self.shotsLeft - 1)) * 50)
			if GetTerrain(self.floor).getAtPos(startPos) not in [1, 9]:
				PTRS["BULLETS"].add(ProjectileShot(self.abil, self.user, self.target, self.attack, self.damageMod, 0, range=100, picture=self.picture, projectileSpeed=2, startPos=startPos))
				self.nextShot = 30 + random.randint(0, 30)
				self.shotsLeft -= 1
		
	def readyToDelete(self):
		return self.shotsLeft <= 0
	
	def drawMe(self, camera):
		if self.floor == camera.floor:
			for i in range(self.shotsLeft):
				p = (self.pos[0] + math.cos(self.angle + math.pi * 2 / float(self.numShots) * i) * 50 - camera.Left(), 
						 self.pos[1] + math.sin(self.angle + math.pi * 2 / float(self.numShots) * i) * 50 - camera.Top())
				drawProjectilePic(camera.getSurface(), self.picture, p, int((self.time / 5) % getNumFrames(self.picture)), int(self.angle * 180 / math.pi))
#Incomplete			
class ProjectileBarrier:
	def __init__(self, abil, user, target, picture="NoPic", numShots=4):
		self.target = target
		self.abil = abil
		self.user = user
		self.picture = picture
		self.pos = self.target.getPos()
		self.angle = 0
		self.time = 80
		self.numShots = numShots
		self.shotsLeft = self.numShots
			
	def update(self):
		self.pos = self.target.getPos()
		self.angle += math.pi / 64.0
		self.time -= 1
		
	def readyToDelete(self):
		return self.time <= 0
	
	def drawMe(self, camera):
		for i in range(self.shotsLeft):
			p = (self.pos[0] - camera.Left() - math.cos(self.angle + math.pi * 2 / self.shotsLeft * i) * 50, 
					 self.pos[1] - camera.Top()  - math.sin(self.angle + math.pi * 2 / self.shotsLeft * i) * 50)
			drawProjectilePic(camera.getSurface(), self.picture, p, int((self.time / 5) % getNumFrames(self.picture)), int(self.angle * 180 / math.pi))

class ChargeProjectile(PlayerProjectile):
	def __init__(self, abil, user, target, attack, damageMod):
		ProjectileShot.initOptions(self)
		self.target = target
		self.damageMod = damageMod
		self.attack = attack
		self.abil = abil
		self.user = user
		self.size = self.user.size
		self.pos = self.user.getPos()
		self.angle = math.atan2(target.getPos()[1] - user.getPos()[1], target.getPos()[0] - user.getPos()[0])
		self.speed = 10
		self.hitsAnyone = True
		self.homing = False
		self.time = 20
		self.floor = user.floor
		self.pierces = True
		self.maxUnitsHit = 3
		self.user.disable()
			
	def update(self):
		PlayerProjectile.update(self)
		if self.time <= 0:
			self.user.enable()
		else:
			self.user.addBuff(Buffs.KeywordBuff(self.abil, self.user, 2, {"Shield":1}))
			self.user.pos = [self.pos[0], self.pos[1]]
			self.user.angle = self.angle
			
	def readyToDelete(self):
		return self.time <= 0
	
	def drawMe(self, camera):
		pass

class BoomerangProjectile(PlayerProjectile):
	def __init__(self, abil, user, target, attack, damageMod=1, picture="NoPic", range=50):
		ProjectileShot.initOptions(self)
		self.attack = attack
		self.damageMod = damageMod
		self.target = target
		self.abil = abil
		self.user = user
		self.size = self.user.size
		self.pos = self.user.getPos()
		self.angle = math.atan2(target.getPos()[1] - user.getPos()[1], target.getPos()[0] - user.getPos()[0])
		self.speed = 5
		self.hitsAnyone = True
		self.homing = False
		self.time = int(range / float(self.speed))
		self.floor = user.floor
		self.pierces = True
		self.picture = picture
		self.returning = False
		self.returned = False
		self.drawAngle = self.angle + math.pi / 5.0
		self.maxUnitsHit = 5
		
	def update(self):
		if self.returning:
			self.angle = math.atan2(self.user.getPos()[1] - self.pos[1], self.user.getPos()[0] - self.pos[0])
			self.drawAngle = self.angle + math.pi / 5.0
		PlayerProjectile.update(self)
		if self.time <= 0 and not self.returning:
			self.returning = True
			self.unitsHit = {}
		if self.returning:
			if dist(self.pos, self.user.getPos()) <= self.user.size:
				self.returned = True
		
	def readyToDelete(self):
		return self.returned
			
class IceBallProjectile:
	def __init__(self, abil, user, target, attack, damageMod = 1, range=150):
		self.target = target
		self.attack = attack
		self.damageMod = damageMod
		self.abil = abil
		self.user = user
		self.picture = "IceBall"
		if self.picture not in EFFECTPICS and self.picture != None:
			path = os.path.join("Data", "Pics", "Effects", self.picture + ".png")
			if not os.path.exists(path):
				path = os.path.join("Data", "Pics", "Effects", "Exclamation.png")
				print "ERROR: EFFECT PIC NOT FOUND:", self.picture
			EFFECTPICS[self.picture] = pygame.image.load(path)
			EFFECTPICS[self.picture].set_colorkey([255, 0, 255])
		self.pos = self.user.getPos()
		self.imageWidth = EFFECTPICS[self.picture].get_width() / 5
		self.step = 0
		self.frame = 0
		self.time = 15
		self.range = range
		self.projectileSpeed = 5
			
	def update(self):
		if self.step == 0:
			self.pos = self.user.getPos()
			if self.frame == 13:
				self.time -= 1
				if self.time <= 0:
					self.step = 1
					self.time = self.range / float(self.projectileSpeed)
			else:
				self.frame += 0.5
		elif self.step == 1:
			ang = math.atan2(self.target.getPos()[1] - self.pos[1], self.target.getPos()[0] - self.pos[0])
			speed = self.projectileSpeed
			self.pos = [self.pos[0] + math.cos(ang) * speed, self.pos[1] + math.sin(ang) * speed]
			self.time -= 1
			if self.time <= 0:
				self.step = 2
				self.abil.explodeAt(self.pos, self.target, ang)
			elif dist(self.pos, self.target.getPos()) <= self.target.size:
				self.pos = self.target.getPos()
				self.step = 2
				self.abil.explodeAt(self.pos, self.target, ang)
		elif self.step == 2:
			self.frame += 0.5
			if self.frame > 20:
				self.step = 3
		
	def readyToDelete(self):
		return self.step > 2
	
	def drawMe(self, camera):
		p = (self.pos[0] - camera.Left() - self.imageWidth / 2, 
				 self.pos[1] - camera.Top()  - self.imageWidth / 2)
		camera.getSurface().blit(EFFECTPICS[self.picture].subsurface([int(self.frame) % 5 * self.imageWidth, int(self.frame) / 5 * self.imageWidth, self.imageWidth, self.imageWidth]), p)
			
class BulletStruct:
	def __init__(self):
		self.bullets = []
		
	def add(self, newB):
		self.bullets += [newB]
		
	def update(self):
		i = 0
		while i < len(self.bullets):
			self.bullets[i].update()
			if self.bullets[i].readyToDelete():
				del self.bullets[i]
			else:
				i += 1
	def drawMe(self, surface):
		for b in self.bullets:
			b.drawMe(surface)
			
PTRS["BULLETS"] = BulletStruct()