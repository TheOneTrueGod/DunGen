import Globals, math, random
import Code.Engine.Effects as Effects
import Code.Units.Projectiles as Projectiles, Code.Units.Guilds as Guilds, Code.Units.Stats as Stats, Code.Units.Buffs as Buffs
from Globals import *
import sys
class Ability:
	icon = "Test1"
	StatAttack = 0
	StatAttackIncrement = 100
	StatKnockbackAttack = 0
	StatKnockbackAttackIncrement = 100
	KnockbackAmount = 1
	UsePriority = 0
	Damage = 1
	Range = 50
	AttackType = "base"
	GoldCost = 100
	UpgradeCost = 50
	UpgradeIncrement = 50
	RageMultiplier = 10
	AttackingMoveSpeed = 1
	overrideValue = 1
	NeedsCasting = False
	StunFactor = 0.4
	DamageType = damageTypes.UNTYPED
	DamageMod = 1
	Interruptable = True
	Guilds = [Guilds.GuildInfo.Types.FIGHTER]
	TimeFactor = 1
	
	def getSpellCircle(self):
		#'UNTYPED', 'SLASH', 'PIERCE', 'BASH', 'ENERGY', 'FIRE', \
		#'ICE', 'LIGHT', 'DARK', 'POISON')
		if self.DamageType == damageTypes.UNTYPED:
			return ""
		elif self.DamageType == damageTypes.SLASH:
			return ""
		elif self.DamageType == damageTypes.PIERCE:
			return ""
		elif self.DamageType == damageTypes.BASH:
			return ""
		elif self.DamageType == damageTypes.ENERGY:
			return "EnergyCircle"
		elif self.DamageType == damageTypes.FIRE:
			return "FireCircle"
		elif self.DamageType == damageTypes.ICE:
			return "IceCircle"
		elif self.DamageType == damageTypes.LIGHT:
			return ""
		elif self.DamageType == damageTypes.DARK:
			return ""
		elif self.DamageType == damageTypes.POISON:
			return ""
		return ""
	
	@staticmethod
	def isBasicAttack():
		return False
		
	def getKnockbackAmount(self, target):
		return self.KnockbackAmount * (1 - target.getStat("knockbackResistance"))
		
	def interrupt(self):
		if not self.Interruptable:
			self.cooldown[0] = 0
	
	def getAttackingMoveSpeed(self):
		return self.AttackingMoveSpeed
		
	def getDamageType(self):
		return self.DamageType
		
	def getTimeTaken(self):
		return self.timeTaken * self.TimeFactor
		
	@staticmethod
	def getDescription(abil):
		return "A test description."
		
	def getAttackVal(self):
		toRet = self.StatAttack + self.StatAttackIncrement * (self.level)
		if self.user != None:
			toRet += self.user.getAttack(self.AttackType)
		return toRet
		
	def calcDamage(self, owner, target, attack, damageMod):
		from Code.Units.Stats import calcDamage, calcSpellDamage
		if self.isSpell:
			return calcSpellDamage(self.Damage, (owner.getSpellLevel(self.Guilds))) * self.DamageMod
		return calcDamage(attack, target.getStat("defense"), -5) * self.DamageMod * damageMod
		
	def getCooldownPercent(self):
		return 1 - self.cooldown[0] / float(self.cooldown[1])
		
	def __init__(self, owner):
		self.hitsAllies = False
		self.hitsEnemies = True
		self.hitsUser = False
		self.user = None
		self.range = 20
		self.cooldown = [0, 100]
		self.timeTaken = 25
		self.hitFrames = [3]
		self.animationOverride = []
		self.level = 0
		self.owner = owner
		self.isSpell = False
		
	def getRange(self):
		return self.Range
		
	def getCost(self):
		if self.level == 0:
			return self.GoldCost
		return self.UpgradeCost + (self.level - 1) * self.UpgradeIncrement
		
	def isUsable(self, user):
		return self.cooldown[0] <= 0
		
	def use(self, user):
		if self.isUsable(user):
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.getTimeTaken(), self.animationOverride)
			self.user = user
			self.cooldown[0] = self.cooldown[1]
			return True
		return False
		
	def update(self):
		self.cooldown[0] -= (self.cooldown[0] > 0)
		
	def useCallback(self, user):
		pass
		
	def getStunFactor(self):
		return self.StunFactor
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		target.addKnockback(calcKnockback(angle, target, self.getKnockbackAmount(target)))
		self.owner.hitTarget(target, amount)
	
class BasicAttack(Ability):
	Range = 50
	StunFactor = 0.8
	TimeFactor = 1
	DamageMod = 1
	@staticmethod
	def isBasicAttack():
		return True
	
	def getStunFactor(self):
		return self.StunFactor * self.owner.equipment.getStunFactorAmount()
		
	def getDamageType(self):
		return self.owner.equipment.getDamageType()
		
	def getTimeTaken(self):
		return self.owner.equipment.getAttackTime() * self.TimeFactor
		
	def __init__(self, owner):
		Ability.__init__(self, owner)
		self.cooldown = [0, 0]
		self.hitFrames = [0]
		self.timeTaken = 2
		self.hitsAllies = False
		self.hitsEnemies = True
		self.projectileSpeed = 8
		
	def getRange(self):
		return self.owner.equipment.getRange()
		
	def getKnockbackAmount(self, target):
		return self.owner.equipment.getKnockbackAmount() * (1 - target.getStat("knockbackResistance"))
		
	def use(self, user):
		if self.isUsable(user):
			#user.attackCallback = self.useCallback
			user.hitFrames = self.hitFrames[:]
			if self.animationOverride == []:
				if user.attackSide == 0:
					self.animationOverride = [5, 6, 7, "idle"]
				else:
					self.animationOverride = [10, 11, 12, "idle"]
			user.setState("attack", self.getTimeTaken(), self.animationOverride)
			self.user = user
			if self.cooldown[1] == 0:
				self.cooldown[0] = user.equipment.getCooldown()
			else:
				self.cooldown[0] = self.cooldown[1]
			return True
		return False
	
	def useCallback(self, user):
		if user.target and not user.target.isDead(): #and user.canSeeUnit(user.target): #and dist(user.getPos(), user.target.getPos()) <= self.getRange():
			startAng = 0
			if user.equipment.getPrimaryWeapon() is None or user.equipment.getPrimaryWeapon().isMeleeWeapon():
				ProjectileClass = Projectiles.MeleeAttack
			else:
				ProjectileClass = Projectiles.PlayerProjectile
				startAng = user.angle
			PTRS["BULLETS"].add(ProjectileClass(self, user, user.target, user.getStat("attack"), user.equipment.getDamageMod(), random.uniform(-math.pi / 24.0, math.pi / 24.0), \
												range=self.getRange(), picture=user.equipment.getProjectile(), projectileSpeed=self.projectileSpeed, homing=False, maxUnitsHit=self.getMaxUnitsHit(),
												startAng = startAng))
			user.switchHands()
			
	def getMaxUnitsHit(self):
		return self.owner.equipment.getMaxUnitsHit()
			
######################				
## Enemy Abilities	##
######################

#****Parameters****
#-animationTime # 	---- How long the attack animation should play for
#-pic	'String'			---- Context-sensative picture to use.
#-cooldown #				---- The amount of time in between uses of the ability
#-damage #					---- The base damage of the attack
#-range #						---- The range of the attack
class EnemyAbility(Ability):
	def __init__(self, owner, parameters):
		Ability.__init__(self, owner)
		self.parameters = {}
		self.range = 80
		self.parseParameters(parameters)
		self.pic = "FireballExplosion"
		self.isSpell = False
		self.damage = 5
		if "pic" in self.parameters:
			self.pic = self.parameters["pic"][0]
		if "cooldown" in self.parameters:
			self.cooldown[1] = int(self.parameters["cooldown"][0])
			self.cooldown[0] = random.randint(0, self.cooldown[1])
		if "damage" in self.parameters:
			self.damage = float(self.parameters["damage"][0])
		if "animationTime" in self.parameters:
			self.timeTaken = int(self.parameters["animationTime"][0])
		if "range" in self.parameters:
			self.range = float(self.parameters["range"][0])
		if "isSpell" in self.parameters:
			self.isSpell = bool(self.parameters["isSpell"][0])
		if "damageType" in self.parameters:
			self.DamageType = int(self.parameters["damageType"][0])
			
	def parseParameters(self, parameters):
		on = 0
		key = ""
		try:
			while on < len(parameters):
				if parameters[on][0] == "-" and len(parameters[on]) > 1:
					key = parameters[on][1:]
					self.parameters[key] = []
				elif key:
					self.parameters[key] += [parameters[on]]
				on += 1
		except:
			print "EnemyAbility Error:", sys.exc_info()[0]
			print "Problem with: ", self
			
	def calcDamage(self, owner, target, attack, damageMod):
		from Code.Units.Stats import calcDamage, calcSpellDamage
		if self.isSpell:
			return calcSpellDamage(self.damage, (self.owner.floor - 1) * 10)
		return calcDamage(attack, target.getStat("defense")) * damageMod
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		target.addKnockback(calcKnockback(angle, target, self.getKnockbackAmount(target)))
		self.owner.hitTarget(target, amount)
		
class EnemyShotAbil(EnemyAbility):
	def __init__(self, owner, parameters):
		EnemyAbility.__init__(self, owner, parameters)
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.getTimeTaken())
			self.user = user
			self.cooldown[0] = self.cooldown[1]
		
#Parameters:
#-speed # 					---- How fast the projectile moves
class EnemyProjectileShotAbil(EnemyShotAbil):
	Range = 130
	def __init__(self, owner, parameters):
		EnemyShotAbil.__init__(self, owner, parameters)
		self.timeTaken = 30
		self.hitFrames = [2]
		self.projectileSpeed = 1
		if "speed" in self.parameters:
			self.projectileSpeed = int(self.parameters["speed"][0])
		
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			PTRS["BULLETS"].add(Projectiles.ProjectileShot(self, user, user.target, user.getStat("attack"), 1, random.uniform(-math.pi / 8.0, math.pi / 8.0), range=self.range, picture=self.pic, projectileSpeed=self.projectileSpeed))
#Parameters:
#-shots # 					---- How many shots to fire
class EnemyMultiShotAbil(EnemyProjectileShotAbil):
	Range = 130
	DamageMod = 0.5
	def __init__(self, owner, parameters):
		EnemyProjectileShotAbil.__init__(self, owner, parameters)
		self.timeTaken = 30
		self.hitFrames = [2]
		self.numShots = 3
		if "shots" in self.parameters:
			self.numShots = int(self.parameters["shots"][0])
		
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			for i in range(-self.numShots / 2 + 1, self.numShots / 2 + 1):
				spread = 8.0
				if self.numShots > 8:
					spread = math.pi / float(self.numShots)
				ang = spread * i
				if self.numShots % 2 == 0:
					ang -= spread / 2.0
				PTRS["BULLETS"].add(Projectiles.ProjectileShot(self, user, user.target, user.getStat("attack"), 1, ang, picture=self.pic, projectileSpeed=self.projectileSpeed, homing=False))

class EnemyFireball(EnemyAbility):
	Range = 130
	UsePriority = 10
	Interruptable = False
	def __init__(self, owner, parameters):
		EnemyAbility.__init__(self, owner, parameters)
		if self.timeTaken == 25:
			self.timeTaken = 60
		self.hitFrames = [2]
		self.flashingSquares = []
		
	def use(self, user):
		if self.cooldown[0] <= 0:
			user.hitFrames = self.hitFrames[:]
			user.setState("attack", self.getTimeTaken())
			self.user = user
			self.cooldown[0] = self.cooldown[1]
			self.targetSquare = posToCoords(user.target.getPos())
			p = self.targetSquare
			self.flashingSquares = []
			for i in [[-1, 0], [-1, -1], [1, 0], [1, -1], [0, -1], [1, 1], [-1, 1], [0, 1], [0, 0]]:
				e = Effects.FlashingSquare([p[0] + i[0], p[1] + i[1]], user.floor, self.getTimeTaken() * 2 / 4)
				PTRS["EFFECTS"].addEffect(e)
				self.flashingSquares += [e]
			if self.getSpellCircle():
				e = Effects.SpellEffect(self.getSpellCircle(), self.owner.getPos(), user.floor, 20)
				PTRS["EFFECTS"].addEffect(e, 0)
		
	def useCallback(self, user):
		targ = coordsToPos(self.targetSquare)
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			for u in PTRS["UNITS"].getPlayers():
				coords = posToCoords(u.getPos())
				for e in self.flashingSquares:
					if e.coord[0] == coords[0] and e.coord[1] == coords[1]:
						self.hitTarget(u, math.atan2(u.getPos()[1] - targ[1], u.getPos()[0] - targ[0]), user.getStat("attack"), 1)
			pos = [self.targetSquare[0] * TILESIZE[0] + random.uniform(0, TILESIZE[0]), 
						 self.targetSquare[1] * TILESIZE[1] + random.uniform(0, TILESIZE[1])]
			PTRS["EFFECTS"].addEffect(Effects.ExplosionEffect(self.pic, pos, user.floor, 10))
			
class EnemyDarkHole(EnemyFireball):
	Range = 100
	UsePriority = 15
	Interruptable = False
	def __init__(self, owner, parameters):
		EnemyAbility.__init__(self, owner, parameters)
		self.timeTaken = 80
		self.hitFrames = [2]
		self.flashingSquares = []

	def useCallback(self, user):
		targ = coordsToPos(self.targetSquare)
		pos = coordsToPos(self.targetSquare)
		PTRS["EFFECTS"].addEffect(Effects.LoopingExplosionEffect(self.pic, pos, user.floor, self, 15, 200, 3))
	
	def hitTick(self, pos):
		for u in PTRS["UNITS"].getPlayers():
			if dist(pos, u.getPos()) <= TILESIZE[0] * 1.5:
				self.hitTarget(u, math.atan2(u.getPos()[1] - pos[1], u.getPos()[0] - pos[0]), self.owner.getStat("attack"), 1)

#Parameters:
#-numShots = number of projectiles to spin around them.
class EnemySpinnerAbil(EnemyAbility):
	UsePriority = 5
	DamageMod = 0.4
	Range = 100
	def __init__(self, owner, parameters):
		EnemyAbility.__init__(self, owner, parameters)
		self.timeTaken = 40
		self.hitFrames = [2]
		self.numShots = 4
		if "numShots" in self.parameters:
			self.numShots = int(self.parameters["numShots"][0])
		
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			PTRS["BULLETS"].add(Projectiles.SpinnerProjectile(self, user, user.target, user.getStat("attack"), picture=self.pic, numShots = self.numShots))
			
#Parameters:
#-numShots = number of projectiles to spin around them.
class EnemyProjectileBarrierAbil(EnemyAbility):
	UsePriority = 5
	def __init__(self, owner, parameters):
		EnemyAbility.__init__(self, owner, parameters)
		self.timeTaken = 40
		self.hitFrames = [2]
		self.numShots = 4
		if "numShots" in self.parameters:
			self.numShots = int(self.parameters["numShots"][0])
		
	def useCallback(self, user):
		if user.target and user.canSeeUnit(user.target) and not user.target.isDead():
			PTRS["BULLETS"].add(Projectiles.ProjectileBarrier(self, user, user.target, user.getStat("attack"), picture=self.pic, numShots = self.numShots))
######################				
## Player Abilities	##
######################			
class PlayerAbility(BasicAttack):
	overrideValue = 2
	icon = "NoRing"
	DisplayName = "ERROR: NOT AN ABILITY."
	DisplayDescription = \
	"""
	Just a quick multi
	line test
	"""
	
	def __init__(self, owner):
		BasicAttack.__init__(self, owner)
		self.hitFrames = [0]
	
	@staticmethod
	def isBasicAttack():
		return False
		
	@staticmethod
	def getDescription(abil):
		return abil.DisplayName + abil.DisplayDescription.replace("	", "")

#Warrior Abilities
class SplitAttack(PlayerAbility):
	icon = "SplitShot"
	DisplayName = "Split Shot"
	DamageMod = 0.8
	StunFactor = 0.8
	TimeFactor = 1
	DisplayDescription = \
	"""
		Throw three attacks at once
	"""
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.hitFrames = [2]
		self.timeTaken = 60
		self.cooldown = [0, 40]
		
	def useCallback(self, user):
		if user.target and not user.target.isDead(): #and user.canSeeUnit(user.target): #and dist(user.getPos(), user.target.getPos()) <= self.getRange():
			startAng = 0
			if user.equipment.getPrimaryWeapon() is None or user.equipment.getPrimaryWeapon().isMeleeWeapon():
				ProjectileClass = Projectiles.MeleeAttack
			else:
				ProjectileClass = Projectiles.PlayerProjectile
				startAng = user.angle
			for angleOffset in [-math.pi / 5.0, 0, math.pi / 5.0]:
				PTRS["BULLETS"].add(ProjectileClass(self, user, user.target, user.getStat("attack"), user.equipment.getDamageMod(), random.uniform(-math.pi / 24.0, math.pi / 24.0) + angleOffset, \
													range=self.getRange(), picture=user.equipment.getProjectile(), projectileSpeed=self.projectileSpeed, homing=False, maxUnitsHit=self.getMaxUnitsHit(),
													startAng = startAng))
				user.switchHands()
class PowerAttack(PlayerAbility):
	icon = "Power Attack"
	DisplayName = "Power Attack"
	Range = 50
	StunFactor = 1.5
	TimeFactor = 2.0
	DamageMod = 2.0
	NeedsCasting = True
	DisplayDescription = \
	"""
	A swing with a good windup that deals 2x normal damage and stuns.
	"""
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.hitFrames = [2]
		self.timeTaken = 60
		self.animationOverride = [5, 5, 6, 7, 8, 9, "idle"]
		self.cooldown = [0, 160]
		
	def getMaxUnitsHit(self):
		return self.owner.equipment.getMaxUnitsHit() + 2
		
	def getRange(self):
		return self.owner.equipment.getRange() + 15
		
	def useCallback(self, user):
		PlayerAbility.useCallback(self, user)
		
	def isUsable(self, user):
		weap = user.equipment.getPrimaryWeapon()
		return self.cooldown[0] <= 0 and (not weap or weap.isMeleeWeapon())
	
class TripleAttack(PlayerAbility):
	icon = "TripleAttack"
	DisplayName = "Triple Attack"
	DamageMod = 0.6
	StunFactor = 0.5
	TimeFactor = 0.5
	DisplayDescription = \
	"""
	Three attacks against the target at 50% of the normal damage.
	"""
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.animationOverride = [5, 6, 7, 10, 11, 12, 5, 6, 7, "idle"]
		self.hitFrames = [1, 4, 7]
		self.timeTaken = 80
		self.cooldown = [0, 120]

	def use(self, user):
		if self.isUsable(user):
			PlayerAbility.use(self,user)
			
	def useCallback(self, user):
		PlayerAbility.useCallback(self, user)
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		target.addKnockback(calcKnockback(angle, target, self.getKnockbackAmount(target)))
		self.owner.hitTarget(target, amount)
	
class Smash(PlayerAbility):
	icon = "Smash"
	DisplayName = "Smash"
	Range = 50
	StunFactor = 1.4
	DamageMod = 0.75
	DisplayDescription = \
	"""
	A quick punch that always does bashing damage.
	"""
	def getDamageType(self):
		return damageTypes.BASH
		
	def isUsable(self, user):
		weap = user.equipment.getPrimaryWeapon()
		return self.cooldown[0] <= 0 and (not weap or weap.isMeleeWeapon())
	
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.hitFrames = [0]
		self.timeTaken = 15
		self.animationOverride = [5, 6, 7, 8, 9, "idle"]
		self.cooldown = [0, 80]

class Whirlwind(PlayerAbility):
	icon = "Whirlwind"
	DisplayName = "Whirlwind"
	Range = 40
	StunFactor = 0.5
	DamageMod = 0.5
	TimeFactor = 2.0
	SecondaryTargets = 5
	DisplayDescription = \
	"""
	Slash wildly, damaging everyone nearby.
	"""
	
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.hitFrames = [2]
		self.animationOverride = [5, 6, 7, 8, 9, "idle"]
		self.cooldown = [0, 100]
		self.drawnSlash = False
		
	def isUsable(self, user):
		weap = user.equipment.getPrimaryWeapon()
		return self.cooldown[0] <= 0 and (not weap or weap.isMeleeWeapon())
		
	def use(self, user):
		if self.isUsable(user):
			PlayerAbility.use(self,user)
			self.drawnSlash = False
		
	def useCallback(self, user):
		PTRS["EFFECTS"].addEffect(Effects.FollowingExplosionEffect("BigSlash", user, user.floor, self, 20, 4))
		self.drawnSlash = True
			
	def hitTick(self):
		targetsHit = 0
		for u in PTRS["UNITS"].getEnemyUnits():
			if self.user.isValidTarget(u, self) and inSameRoom(self.user, u) and dist(self.user.getPos(), u.getPos()) <= self.Range and self.user.canSeeUnit(u, self):
				targetsHit += 1
				self.hitTarget(u, math.atan2(u.getPos()[1] - self.user.getPos()[1], u.getPos()[0] - self.user.getPos()[0]),
												self.user.getStat("attack"), self.user.equipment.getDamageMod())
				if targetsHit >= self.SecondaryTargets:
					break
		self.owner.switchHands()

class Charge(PlayerAbility):
	icon = "Charge"
	DisplayName = "Charge"
	Range = 40
	StunFactor = 0.5
	DamageMod = 1.5
	TimeFactor = 1.0
	NeedsCasting = True
	DisplayDescription = \
	"""
	Rush at the target dealing bashing damage and knocking them back
	"""
	
	def getTimeTaken(self):
		return self.timeTaken * self.TimeFactor
		
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.hitFrames = [4 * 3]
		self.animationOverride = [0, 1, 2, 1]*3 + ["idle"]
		self.hitsLeft = 3
		self.timeTaken = 20
		self.cooldown = [0, 120]
		
	def useCallback(self, user):
		PTRS["BULLETS"].add(Projectiles.ChargeProjectile(self, user, self.user.target, user.getStat("attack"), user.equipment.getDamageMod()))
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		self.hitsLeft -= 1
		target.addKnockback(calcKnockback(angle, target, self.getKnockbackAmount(target)))
		self.owner.hitTarget(target, amount)
		
class BoomerangBlade(PlayerAbility):
	icon = "Boomerang Blade"
	DisplayName = "Boomerang Blade"
	Range = 40
	StunFactor = 0.5
	DamageMod = 1.1
	TimeFactor = 1.5
	DisplayDescription = \
	"""
	Throw a blade at an arc that returns back to you.
	"""
	def __init__(self, owner):
		PlayerAbility.__init__(self, owner)
		self.timeTaken = 50
		self.cooldown = [0, 120]
		
	def useCallback(self, user):
		PTRS["BULLETS"].add(Projectiles.BoomerangProjectile(self, user, self.user.target, user.getStat("attack"), picture=user.equipment.getProjectile(), range=self.getRange() * 2))
		self.owner.switchHands()
		
	def isUsable(self, user):
		if self.cooldown[0] <= 0:
			weap = user.equipment.getPrimaryWeapon()
			return self.cooldown[0] <= 0 and (not weap or weap.isMeleeWeapon())
		
#Mage Abilities
class MagicSpell(Ability):
	Guilds = [Guilds.GuildInfo.Types.SORCERER]
	KnockbackAmount = 0
	overrideValue = 2
	icon = "NoRing"
	DisplayName = "ERROR: NOT AN ABILITY."
	DisplayDescription = \
	"""
	Just a quick multi
	line test
	"""
	@staticmethod
	def isBasicAttack():
		return False
		
	@staticmethod
	def getDescription(abil):
		return abil.DisplayName + abil.DisplayDescription.replace("	", "")
		
	def __init__(self, owner):
		Ability.__init__(self, owner)
		self.isSpell = True
		
	def getKnockbackAmount(self, target):
		return self.KnockbackAmount * (1 - target.getStat("knockbackResistance"))
		
	def use(self, user):
		if self.isUsable(user):
			if Ability.use(self, user):
				e = Effects.SpellEffect(self.getSpellCircle(), self.owner.getPos(), user.floor, 20)
				PTRS["EFFECTS"].addEffect(e, 0)
				return True
		return False
## !! Energy !! ##
class MagicMissile(MagicSpell):
	icon = ["Spell Icons", [0, 2]]
	DisplayName = "Magic Missile"
	Range = 180
	StunFactor = 0.3
	NeedsCasting = True
	DamageType = damageTypes.ENERGY
	Guilds = [Guilds.GuildInfo.Types.SORCERER]
	DisplayDescription = \
	"""
	Fires five missiles at a single enemy.  Very short cast time.
	"""
	def __init__(self, owner):
		MagicSpell.__init__(self, owner)
		self.pic = "MagicMissile"
		self.projectileSpeed = 6
		self.numShots = 5
		self.Damage = Stats.MagicDamageExpressions["Low"]["Single"] / float(self.numShots)
			#self.hitFrames = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5]
		self.cooldown = [0, 60]
		self.isSpell = True
		self.timeTaken = 40
		self.calcAnimationOverride(1, self.numShots / 2 + 2)
		self.calcHitFrames()
		self.firstCallback = True
		
	def use(self, user):
		if self.isUsable(user):
			if MagicSpell.use(self, user):
				self.firstCallback = True
		
	def calcAnimationOverride(self, introLoops, numReleaseFrames):
		loopFrames = (self.getTimeTaken() - 2 * (numReleaseFrames + introLoops)) / 6
		self.animationOverride = [15, 16] * introLoops + [17, 18, 19] * loopFrames + [20] * numReleaseFrames + ["idle"]
		self.firstHitFrame = loopFrames * 3 + introLoops * 2
		
	def calcHitFrames(self):
		self.hitFrames = []
		on = 0
		for i in range(self.numShots):
			self.hitFrames += [self.firstHitFrame + on * (len(self.animationOverride) - 1 - self.firstHitFrame) / float(self.numShots)]
			on += 1
		
	def getDamageType(self):
		return self.DamageType
		
	def useCallback(self, user):
		if self.firstCallback:
			self.firstCallback = False
		maxAngle = math.pi / 2.0
		targetsHit = []
		for u in PTRS["UNITS"].getEnemyUnits():
			if user.isValidTarget(u, self) and inSameRoom(user.target, u) and \
							dist(user.getPos(), u.getPos()) <= self.Range and user.canSeeUnit(u, self):
				ang = math.atan2(u.pos[1] - user.pos[1], u.pos[0] - user.pos[0])
				angDiff = (user.angleFacing - ang)
				if math.fabs(angDiff) < maxAngle or math.fabs(angDiff) > math.pi * 2 - maxAngle:
					targetsHit += [u]
		
		if targetsHit:
			targIndex = random.randint(0, len(targetsHit) - 1)
			self.target = targetsHit[targIndex]
			PTRS["BULLETS"].add(Projectiles.MagicMissile(self, user, self.target, user.getStat("attack"), 1, random.uniform(-math.pi / 1.5, math.pi / 1.5), \
																	range=self.Range, picture=self.pic, projectileSpeed=self.projectileSpeed, hitsAnyone=False))
		else:
			self.target = user.target
			PTRS["BULLETS"].add(Projectiles.MagicMissile(self, user, self.target, user.getStat("attack"), 1, random.uniform(-math.pi / 1.5, math.pi / 1.5), \
																	range=self.Range, picture=self.pic, projectileSpeed=self.projectileSpeed, hitsAnyone=False))
		
	def hitTarget(self, target, angle, attack, damageMod):
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		self.owner.hitTarget(target, amount)

class MissileStorm(MagicMissile):
	icon = ["Spell Icons", [1, 2]]
	DisplayName = "Missile Storm"
	Range = 200
	DisplayDescription = \
	"""
	Fires fifteen missiles at a single enemy.  Very short cast time.
	"""
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.numShots = 15
		self.cooldown = [0, 180]
		self.Damage = Stats.MagicDamageExpressions["Medium"]["Single"] / float(self.numShots)
		self.timeTaken = 60
		self.calcAnimationOverride(1, self.numShots / 2 + 2)
		self.calcHitFrames()
#DISABLED
class GreaterMissileStorm(MagicMissile):
	icon = "Greater Missile Storm"
	DisplayName = "Greater Missile Storm"
	Range = 210
	DisplayDescription = \
	"""
	Fires twenty five missiles at a single enemy.  Very short cast time.
	"""
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.numShots = 25
		self.Damage = Stats.MagicDamageExpressions["High"]["Single"] / float(self.numShots)
		self.cooldown = [0, 300]
		self.timeTaken = 150
		self.calcAnimationOverride(2, self.numShots / 2 + 2)
		self.calcHitFrames()
## !! Fire !! ##
class Sparks(MagicMissile):
	icon = ["Spell Icons", [0, 0]]
	DisplayName = "Sparks"
	Range = 130
	SecondaryTargets = 2
	StunFactor = 1
	NeedsCasting = True
	DamageType = damageTypes.FIRE
	SecondaryTargetRange = 80
	DisplayDescription = \
	"""
	Fires five missiles at a single enemy.  Very short cast time.
	"""
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.pic = "Sparks"
		self.projectileSpeed = 3
		self.Damage = Stats.MagicDamageExpressions["Low"]["Area"]
		self.timeTaken = 40
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		
	def useCallback(self, user):
		if user.target.isTrainingDummy():
			nextTargets = -1
		else:
			PTRS["BULLETS"].add(Projectiles.PlayerProjectile(self, user, user.target, user.getStat("attack"), 1, random.uniform(-math.pi / 12.0, math.pi / 12.0), \
																range=self.Range, picture=self.pic, projectileSpeed=self.projectileSpeed, hitsAnyone=False))
			nextTargets = 0
		for u in PTRS["UNITS"].getEnemyUnits():
			if nextTargets >= self.SecondaryTargets:
				break
			if u != user.target and user.isValidTarget(u, self) and inSameRoom(user.target, u) and dist(user.getPos(), u.getPos()) <= self.SecondaryTargetRange and user.canSeeUnit(u, self):
				nextTargets += 1
				PTRS["BULLETS"].add(Projectiles.PlayerProjectile(self, user, u, user.getStat("attack"), 1, random.uniform(-math.pi / 12.0, math.pi / 12.0), \
															range=self.Range, picture=self.pic, projectileSpeed=self.projectileSpeed, hitsAnyone=False))
					
	def hitTarget(self, target, angle, attack, damageMod):
		MagicMissile.hitTarget(self, target, angle, attack, damageMod)
		
class Ignite(Sparks):
	icon = ["Spell Icons", [1, 0]]
	DisplayName = "Ignite"
	SecondaryTargets = 5
	def __init__(self, owner):
		Sparks.__init__(self, owner)
		self.Damage = Stats.MagicDamageExpressions["Medium"]["Area"]
		self.timeTaken = 40
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		self.numShots = 1
		self.cooldown = [0, 200]
		self.calcHitFrames()
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		#(self, unit, damageSource, damageType, totalDamage, timeBetweenDamage, timesToDamage)
		timeBetweenDamage = 10
		timesToDamage = 10
		target.addBuff(Buffs.DamageBuff(self, target, self.owner, self.DamageType, self.Damage, timeBetweenDamage, timesToDamage))
		target.addKnockback(calcKnockback(angle, target, self.getKnockbackAmount(target)))
		PTRS["EFFECTS"].addEffect(Effects.SpellEffect("Ignite", target.getPos(), target.floor, 40, True, None, target))

class Explosion(MagicMissile):
	icon = ["Spell Icons", [1, 0]]
	DisplayName = "Explosion"
	DamageType = damageTypes.FIRE
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.Damage = Stats.MagicDamageExpressions["High"]["Area"]
		self.timeTaken = 60
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		self.numShots = 1
		self.radius = 100
		self.cooldown = [0, 200]
		self.calcHitFrames()
		
	def useCallback(self, user):
		if user.target and (user.canSeeUnit(user.target) and not user.target.isDead()) or user.target.isTrainingDummy():
			for u in PTRS["UNITS"].getEnemyUnits():
				d = dist(u.getPos(), user.target.getPos())
				if d < self.radius:
					self.hitTarget(u, math.atan2(u.getPos()[1] - user.target.getPos()[1], u.getPos()[0] - user.target.getPos()[0]), user.getStat("attack"), 1)
		PTRS["EFFECTS"].addEffect(Effects.ExplosionEffect("FireballExplosion", user.target.getPos(), user.floor, 10))

class Immolation(Sparks):
	icon = ["Spell Icons", [2, 0]]
	DisplayName = "Immolation"
	SecondaryTargets = 2
	StunFactor = 0
	def __init__(self, owner):
		Sparks.__init__(self, owner)
		self.numShots = 5
		self.Damage = Stats.MagicDamageExpressions["Low"]["Area"] / self.numShots / 2.0
		self.timeTaken = 40
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		self.cooldown = [0, 200]
		
	def doImmolationEffect(self, sourceUnit):
		for u in PTRS["UNITS"].getEnemyUnits():
			if u != sourceUnit and inSameRoom(sourceUnit, u) and dist(sourceUnit.getPos(), u.getPos()) <= self.SecondaryTargetRange and sourceUnit.canSeeUnit(u, self):
				Sparks.hitTarget(self, u, math.atan2(sourceUnit.getPos()[1] - u.getPos()[1], sourceUnit.getPos()[0] - u.getPos()[0]), self.owner.getStat("attack"), 1)
		
	def hitTarget(self, target, angle, attack, damageMod):
		from Code.Units.Stats import calcKnockback
		timeBetweenShots = 20
		target.addBuff(Buffs.ImmolationBuff(self, target, self.numShots, timeBetweenShots))
		
## !! Ice !! ##
class IcicleBlast(MagicMissile):
	icon = ["Spell Icons", [0, 1]]
	DisplayName = "Icicle Blast"
	Range = 90
	StunFactor = 0.3
	NeedsCasting = True
	DamageType = damageTypes.ICE
	Guilds = [Guilds.GuildInfo.Types.SORCERER]
	DisplayDescription = \
	"""
	Fires a blast of icicles at the enemy
	"""
	def __init__(self, owner):
		MagicSpell.__init__(self, owner)
		self.pic = "Icicle"
		self.projectileSpeed = 10
		self.numShots = 15
		self.shotsPerFrame = 2
		self.Damage = Stats.MagicDamageExpressions["Medium"]["Area"] / float(self.numShots)
		self.hitFrames = [1]
		self.cooldown = [0, 60]
		self.isSpell = True
		self.timeTaken = 40
		self.calcAnimationOverride(1, self.numShots / 2 + 2)
		self.calcHitFrames()
		self.firstCallback = True
		
		self.shotOn = 0
		
	def use(self, user):
		if self.isUsable(user):
			if MagicSpell.use(self, user):
				self.firstCallback = True
		
	def calcAnimationOverride(self, introLoops, numReleaseFrames):
		loopFrames = (self.getTimeTaken() - 2 * (numReleaseFrames + introLoops)) / 6
		self.animationOverride = [15, 16] * introLoops + [17, 18, 19] * loopFrames + [20] * numReleaseFrames + ["idle"]
		self.firstHitFrame = loopFrames * 3 + introLoops * 2
		
	def calcHitFrames(self):
		self.hitFrames = []
		on = 0
		for i in range(self.numShots):
			self.hitFrames += [self.firstHitFrame + on * (len(self.animationOverride) - 1 - self.firstHitFrame) / float(self.numShots)]
			on += 1
		
	def getDamageType(self):
		return self.DamageType
		
	def useCallback(self, user):
		self.target = user.target
		self.shotOn += 1
		lastProjectile = None
		for i in range(self.shotsPerFrame):
			if self.target:
				newProjectile = PTRS["BULLETS"].add(Projectiles.PlayerProjectile(self, user, self.target, user.getStat("attack"), 1, random.uniform(-math.pi / 6.0, math.pi / 6.0), \
																						range=int(self.Range * random.uniform(0.8, 1.2)), picture=self.pic, projectileSpeed=self.projectileSpeed, hitsAnyone=True, pierces=True, homing=False))
				if lastProjectile:
					lastProjectile.linkProjectiles(newProjectile)
				lastProjectile = newProjectile
		
	def hitTarget(self, target, angle, attack, damageMod):
		amount = target.addDamage(self.calcDamage(self.owner, target, attack, damageMod), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
		self.owner.hitTarget(target, amount)
		target.addBuff(Buffs.StatBuff(self, target, 300, {"moveSpeed":0.9}))

class IceBall(MagicMissile):
	icon = ["Spell Icons", [1, 1]]
	DisplayName = "Ice Ball"
	Range = 130
	StunFactor = 3
	NeedsCasting = True
	KnockbackAmount = 5
	DamageType = damageTypes.ICE
	AoE = 40
	DisplayDescription = \
	"""
	Creates a giant ball of ice and launches it at the enemy
	"""
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.projectileSpeed = 3
		self.Damage = Stats.MagicDamageExpressions["Medium"]["Area"]
		self.timeTaken = 40
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		self.numShots = 1
		self.cooldown = [0, 200]
		self.calcHitFrames()
		
	def useCallback(self, user):
		PTRS["BULLETS"].add(Projectiles.IceBallProjectile(self, user, user.target, user.getStat("attack")))
	
	def explodeAt(self, tPos, target, angle):
		from Code.Units.Stats import calcKnockback
		for u in PTRS["UNITS"].getTargets(self.owner.team, False, True):
			d = dist(u.getPos(), tPos)
			if d <= u.size + self.AoE:
				if target is u:
					ang = angle
				else:
					ang = math.atan2(u.getPos()[1] - tPos[1], u.getPos()[0] - tPos[0])
				amount = u.addDamage(self.calcDamage(self.owner, u, self.owner.getStat("attack"), 1), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
				u.addKnockback(calcKnockback(ang, u, self.getKnockbackAmount(u)))
				u.addBuff(Buffs.StatBuff(self, u, 200, {"moveSpeed":0.5}))
				self.owner.hitTarget(u, amount)

class Chill(MagicMissile):
	icon = ["Spell Icons", [2, 1]]
	DisplayName = "Chill"
	Range = 130
	StunFactor = 0.3
	NeedsCasting = True
	KnockbackAmount = 5
	DamageType = damageTypes.ICE
	AoE = 60
	DamageMod = 0.1
	DisplayDescription = \
	"""
	Creates a giant ball of ice and launches it at the enemy
	"""
	def __init__(self, owner):
		MagicMissile.__init__(self, owner)
		self.projectileSpeed = 3
		self.Damage = Stats.MagicDamageExpressions["Medium"]["Area"]
		self.timeTaken = 50
		self.calcAnimationOverride(1, 3)
		self.hitFrames = [self.firstHitFrame]
		self.numShots = 1
		self.cooldown = [0, 250]
		self.calcHitFrames()
		
	def useCallback(self, user):
		ang = math.atan2(user.target.getPos()[1] - user.getPos()[1], user.target.getPos()[0] - user.getPos()[0])
		d = min(dist(user.getPos(), user.target.getPos()), self.Range)
		pos = intOf([user.getPos()[0] + math.cos(ang) * d, user.getPos()[1] + math.sin(ang) * d])
		PTRS["EFFECTS"].addEffect(Effects.ExplosionEffect("FrostExplosion", pos, user.floor, 70, 10, self))
		
	def hitTick(self, tPos):
		from Code.Units.Stats import calcKnockback
		for u in PTRS["UNITS"].getTargets(self.owner.team, False, True):
			d = dist(u.getPos(), tPos)
			if d <= self.AoE:
				ang = math.atan2(u.getPos()[1] - tPos[1], u.getPos()[0] - tPos[0])
				amount = u.addDamage(self.calcDamage(self.owner, u, self.owner.getStat("attack"), 1), self.owner, self.getDamageType(), stunFactor = self.getStunFactor())
				u.addBuff(Buffs.StatBuff(self, u, 200, {"moveSpeed": 0.3}))
				self.owner.hitTarget(u, amount)

######################
## Player Abilities ##
######################
playerAbilDict = {"TripleAttack":TripleAttack, "Smash":Smash, "Whirlwind":Whirlwind, "PowerAttack":PowerAttack, "Charge":Charge, 
									"BoomerangBlade":BoomerangBlade, "SplitAttack":SplitAttack,
								  #Sorcerer Spells
									"MagicMissile":MagicMissile, "MissileStorm":MissileStorm, "GreaterMissileStorm":GreaterMissileStorm, 
									"Sparks":Sparks, "Ignite":Ignite, "Chill":Chill, "Explosion":Explosion, "Immolation":Immolation,
									"IcicleBlast":IcicleBlast, "IceBall":IceBall}
abilList = {"MELEE":BasicAttack, "RANGED":BasicAttack}
enemyAbilList = {"PROJECTILE":EnemyProjectileShotAbil, "MULTISHOT":EnemyMultiShotAbil, "FIREBALL":EnemyFireball, 
								 "DARKHOLE":EnemyDarkHole, "SPINNER":EnemySpinnerAbil, "BARRIER":EnemyProjectileBarrierAbil}
attackTypes = ["weapon"]