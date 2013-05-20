from GUI import View, Image, TextField, Font, Label

from Code.UI.Components import *
from Globals import *

import Code.Units.Equipment as Equipment
import Units
EQUIPMENTSLOT = 1
INVENTORYSLOT = 0
class ChurchView(ViewWithBackButton):
	def setupComponents(self, parent):
		bottom = self.height - 50
		self.characters = []
		#self.equippedDescriptionField = TextField(multiline=True, size=(self.width - EquipDescriptionTopLeft[0] * 2, 100), position=EquipDescriptionTopLeft, enabled=False)
		#self.add(self.equippedDescriptionField)
		#DeadCharacterSlot

		ViewWithBackButton.setupComponents(self, parent)
		
	def refreshComponent(self):
		separation = 5
		vSeparation = 10
		TopLeft = (10, 10)
		while self.characters:
			self.remove(self.characters[0])
			del self.characters[0]
			
		for i in range(len(Units.deadUnits)):
			on = len(self.characters)
			dcs = DeadCharacterSlot()
			dcs.position=(TopLeft[0] + (CHARACTERSLOTSIZE[0] + separation) * (on % (self.width / CHARACTERSLOTSIZE[0])), 
										TopLeft[1] + (CHARACTERSLOTSIZE[1] + vSeparation) * (on / (self.width / CHARACTERSLOTSIZE[0])))
			dcs.setupComponents(self, Units.deadUnits[i])
			self.characters += [dcs]
			self.add(dcs)
		
	def itemClicked(self, deadChar):
		Units.ReviveUnit(deadChar)
		self.container.reloadCharacters()
		self.refreshComponent()
		self.invalidate()
		#if inventorySlot[0] == INVENTORYSLOT:
		#	self.model.equipItem(inventorySlot[1])
		#elif inventorySlot[0] == EQUIPMENTSLOT:
		#	self.model.unequipItem(inventorySlot[1])
		
	def mouseOverInventory(self, deadChar):
		pass
		"""if self.model.character:
			if inventorySlot[0] == INVENTORYSLOT:
				item = self.model.character.getInventoryItem(inventorySlot[1])
				if item:
					self.inventoryDescriptionField.text = item.getDescription()
					equip = self.model.character.getEquippedItem(item.getSlots()[0])
					if equip:
						self.equippedDescriptionField.text = equip.getDescription()
					else:
						self.equippedDescriptionField.text = ""
				else:
					self.inventoryDescriptionField.text = ""
					self.equippedDescriptionField.text = ""
			elif inventorySlot[0] == EQUIPMENTSLOT:
				item = self.model.character.getEquippedItem(inventorySlot[1])
				if item:
					self.equippedDescriptionField.text = item.getDescription()
				else:
					self.equippedDescriptionField.text = """""
		
	def characterChanged(self, model, character):
		pass

CHARACTERSLOTSIZE = (80, 85)
class DeadCharacterSlot(View):
	def setupComponents(self, parent, deadChar):
		self.size = CHARACTERSLOTSIZE
		
		self.cImg = CharacterImage(position = (self.width / 4 - 39 / 4, 9))
		self.cImg.setupComponents()
		self.add(self.cImg)
		self.setItemImage(deadChar[1])
		self.deadChar = deadChar
		
		t = deadChar[0]
		if len(t) > 10:
			t = t[:8] + "..."
		l = Label(text=t)
		l.position = (self.width / 2 - l.width / 2, 0)
		self.add(l)
		
		btn = Button(title = "Revive", action = self.imageClicked, style = 'default')
		btn.position = (self.width / 2 - btn.width / 2, 59)
		self.add(btn)
		
	def setItemImage(self, newItemImg):
		self.cImg.setImage(newItemImg)
		
	def imageClicked(self):
		self.container.itemClicked(self.deadChar)
		
	def mouseOverImage(self):
		self.container.mouseOverInventory(self.deadChar)
		
	def draw(self, c, r):
		c.frame_rect((0, 0, self.width, self.height))

class CharacterImage(View):
	def setupComponents(self):
		self.image = None
		
	def clearImage(self):
		self.image = None
		
	def setImage(self, imagePath):
		path = os.path.join("Data", "Pics", "Actors", imagePath + ".png")
		self.image = Image(file = path)
		
	def draw(self, c, r):
		if self.image:
			main_image_pos = self.position
			src_rect = (39, 0, 39*2, 39)
			dst_rect = (main_image_pos[0], main_image_pos[1], 
									main_image_pos[0] + src_rect[2] - src_rect[0], 
									main_image_pos[1] + src_rect[3] - src_rect[1])
			self.image.draw(c, src_rect, dst_rect)