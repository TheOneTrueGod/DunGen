from Globals import *
import Code.Engine.Effects as Effects
class BuffStruct:
	def __init__(self, unit):
		self.unit = unit
		self.buffs = []
		
	def update(self):
		b = 0
		while b < len(self.buffs):
			self.buffs[b].update()
			if self.buffs[b].readyToDelete():
				del self.buffs[b]
			else:
				b += 1
				
	def addBuff(self, newBuff):
		if newBuff.sourceAbil != None:
			for buff in self.buffs:
				if buff.sourceAbil == newBuff.sourceAbil and buff.Type == newBuff.Type:
					buff.merge(newBuff)
					return
		self.buffs += [newBuff]
		
	def getStat(self, stat):
		toRet = 0
		for buff in self.buffs:
			toRet += buff.getStat(stat)
		return toRet
		
	def getKeyword(self, keyword):
		toRet = 0
		for buff in self.buffs:
			toRet += (1 - toRet) * buff.getKeyword(keyword)
		return toRet
		
	def getStatMod(self, stat):
		toRet = 1
		for buff in self.buffs:
			toRet *= buff.getStat(stat)
		return toRet
		
class Buff:
	Type = "Default"
	def __init__(self, sourceAbil, unit, time):
		self.unit = unit
		self.time = time
		self.nextEffect = [0, 10]
		self.sourceAbil = sourceAbil
		
	def merge(self, otherBuff):
		self.time = max(self.time, otherBuff.time)
		
	def update(self):
		self.time -= 1
		self.nextEffect[0] += 1
		if self.nextEffect[0] >= self.nextEffect[1]:
			self.nextEffect[0] -= self.nextEffect[1]
			self.createEffects()
		
	def createEffects(self):
		pass
		
	def getStat(self, stat):
		return 0
		
	def getKeyword(self, keyword):
		return 0
		
	def getStatMod(self, stat):
		return 1

	def readyToDelete(self):
		return self.time <= 0 or self.unit.isDead()
		
class DamageBuff(Buff):
	Type = "Damage"
	def __init__(self, sourceAbil, unit, damageSource, damageType, totalDamage, timeBetweenDamage, timesToDamage):
		Buff.__init__(self, sourceAbil, unit, timeBetweenDamage)
		self.timesToDamage = timesToDamage
		self.timeBetweenDamage = timeBetweenDamage
		self.damageAmount = totalDamage / float(timesToDamage)
		self.damageSource = damageSource
		self.damageType = damageType
		
	def merge(self, otherBuff):
		self.timesToDamage = max(self.timesToDamage, otherBuff.timesToDamage)
		
	def createEffects(self):
		if self.damageType == damageTypes.FIRE:
			PTRS["EFFECTS"].addEffect(Effects.SpellEffect("Burn", self.unit.getPos(), self.unit.floor, 10, True))
		
	def update(self):
		Buff.update(self)
		if self.time <= 0 and self.timesToDamage > 0:
			self.timesToDamage -= 1
			self.time = self.timeBetweenDamage
			self.unit.addDamage(self.damageAmount, self.damageSource, self.damageType, 0)
			if self.damageSource:
				self.damageSource.hitTarget(self.unit, self.damageAmount)
				
class StatBuff(Buff):
	Type = "Stat"
	def __init__(self, sourceAbil, unit, duration, stats, iconPos = None):
		Buff.__init__(self, sourceAbil, unit, duration)
		self.stats = stats
		self.nextEffect = [0, 50]
		self.iconPos = None
		
	def createEffects(self):
		p = self.unit.getPos()
		p = [p[0], p[1] - 15]
		if self.iconPos:
			PTRS["EFFECTS"].addEffect(Effects.FadingBuffEffect(self.iconPos, p, self.unit.floor, 30))
		else:
			if "moveSpeed" in self.stats:
				if self.stats["moveSpeed"] < 1:
					PTRS["EFFECTS"].addEffect(Effects.FadingBuffEffect([0, 0], p, self.unit.floor, 30))
		
	def merge(self, otherBuff):
		self.time = max(self.time, otherBuff.time)
		
	def getStat(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		return 0
		
	def getStatMod(self, stat):
		if stat in self.stats:
			return self.stats[stat]
		return 1
		
class KeywordBuff(StatBuff):
	Type = "Keyword"
	def __init__(self, sourceAbil, unit, duration, keywords, iconPos = None):
		Buff.__init__(self, sourceAbil, unit, duration)
		self.keywords = keywords
		self.nextEffect = [0, 50]
		self.iconPos = None
		
	def createEffects(self):
		p = self.unit.getPos()
		p = [p[0], p[1] - 15]
		if self.iconPos:
			PTRS["EFFECTS"].addEffect(Effects.FadingBuffEffect(self.iconPos, p, self.unit.floor, 30))
		else:
			pass
			#if "moveSpeed" in self.stats:
			#	if self.stats["moveSpeed"] < 1:
			#		PTRS["EFFECTS"].addEffect(Effects.FadingBuffEffect([0, 0], p, self.unit.floor, 30))
		
	def merge(self, otherBuff):
		self.time = max(self.time, otherBuff.time)
		
	def getStat(self, stat):
		return 0
		
	def getKeyword(self, keyword):
		if keyword in self.keywords:
			return self.keywords[keyword]
		return 0
		
	def getStatMod(self, stat):
		return 1
		
class ImmolationBuff(Buff):
	def __init__(self, sourceAbil, unit, numShots, timeBetweenShots):
		Buff.__init__(self, sourceAbil, unit, numShots * timeBetweenShots)
		self.timeBetweenShots = timeBetweenShots
		self.shotsLeft = numShots
		self.startTime = self.time
		self.nextEffect = [timeBetweenShots, timeBetweenShots]
		
	def merge(self, otherBuff):
		pass
		
	def createEffects(self):
		self.sourceAbil.doImmolationEffect(self.unit)
		PTRS["EFFECTS"].addEffect(Effects.SpellEffect("Ignite", self.unit.getPos(), self.unit.floor, self.timeBetweenShots, True))
		
	#WORKING ON IMMOLATION SKILL