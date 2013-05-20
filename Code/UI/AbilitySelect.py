from GUI import View, Image, TextField, Font

from Code.UI.Components import *
from Globals import *

import Code.Units.Equipment as Equipment
EQUIPPEDSLOT = 0
LEARNEDSLOT = 1
class AbilitySelect(ViewWithBackButton):
	def setupComponents(self, parent):
		self.learnedAbilities = []
		separation = 5
		bottom = self.height - 50
		inventoryHeight = ((ABILITYDISPLAYSLOTS - 1) / 8 + 1) * (40 + separation)
		descriptionHeight = 110
		
		EquipmentTopLeft = (self.width / 2, 10)
		InventoryTopLeft = (10, 10 + (40 + separation) + descriptionHeight + 10 * 2)
		EquipDescriptionTopLeft = (10, 10 + (40 + separation) + 10 * 1)
		
		self.abilitySlots = []
		for i in range(ABILITYSLOTS):
			on = len(self.abilitySlots)
			abilSlot = AbilitySlot(position=(EquipmentTopLeft[0] + (40 + separation) * on - (40 + separation) * ABILITYSLOTS / 2, 
																			 EquipmentTopLeft[1]))
			self.abilitySlots += [abilSlot]
			abilSlot.setupComponents(self, [EQUIPPEDSLOT, on])
			self.add(abilSlot)
		
		self.learnedSlots = []
		for i in range(ABILITYDISPLAYSLOTS):
			on = len(self.learnedSlots)
			isl = AbilitySlot(position=(InventoryTopLeft[0] + (40 + separation) * (on % 6), InventoryTopLeft[1] + (40 + separation) * (on / 6)))
			self.learnedSlots += [isl]
			isl.setupComponents(self, [LEARNEDSLOT, on])
			self.add(isl)
			
		self.equippedDescriptionField = TextField(multiline=True, size=(self.width - EquipDescriptionTopLeft[0] * 2, 100), position=EquipDescriptionTopLeft, enabled=False)
		self.add(self.equippedDescriptionField)

		ViewWithBackButton.setupComponents(self, parent)
		
	def itemClicked(self, inventorySlot):
		if self.model.character:
			if inventorySlot[0] == LEARNEDSLOT and 0 <= inventorySlot[1] < len(self.learnedAbilities):
				self.model.character.equipAbil(self.learnedAbilities[inventorySlot[1]])
				self.model.characterUpdated()
			elif inventorySlot[0] == EQUIPPEDSLOT:
				self.model.character.unEquipAbil(inventorySlot[1])
				self.model.characterUpdated()
		
	def mouseOverInventory(self, inventorySlot):
		if self.model.character:
			abil = None
			if inventorySlot[0] == LEARNEDSLOT and 0 <= inventorySlot[1] < len(self.learnedAbilities):
				abil = self.learnedAbilities[inventorySlot[1]]
			elif inventorySlot[0] == EQUIPPEDSLOT:
				abil = self.model.character.getSelectedAbil(inventorySlot[1])
			if abil:
				self.equippedDescriptionField.text = abil.getDescription(abil)
			else:
				self.equippedDescriptionField.text = ""
		
	def characterChanged(self, model, character):
		if character:
			self.invalidate()
			#Setup the 'learned' abilities
			self.learnedAbilities = character.getLearnedAbilities()
			on = 0
			for abil in self.learnedAbilities:
				if abil:
					self.learnedSlots[on].setImage(abil.icon)
				else:
					self.learnedSlots[on].setImage(None)
				on += 1
			for i in range(on, ABILITYDISPLAYSLOTS):
				self.learnedSlots[i].setImage(None)
			#Setup the 'equipped' ability slots
			on = 0
			for slot in self.abilitySlots:
				abil = character.getSelectedAbil(on)
				if abil:
					self.abilitySlots[on].setImage(abil.icon)
				else:
					self.abilitySlots[on].setImage(None)
				on += 1
		
class AbilitySlot(View):
	def setupComponents(self, parent, slotNum):
		self.size = (40, 40)
		self.slotNum = slotNum
		
		self.eImg = AbilityImage(position = (0, 0))
		self.eImg.setupComponents()
		self.add(self.eImg)
		
	def setImage(self, newImg):
		if newImg == None:
			self.eImg.setImage(None)
		else:
			self.eImg.setImage(newImg)
		
	def imageClicked(self, position):
		self.container.itemClicked(self.slotNum)
		
	def mouseOverImage(self):
		self.container.mouseOverInventory(self.slotNum)

class AbilityImage(View):
	def handle_event(self, event):
		if event.kind == 'mouse_up':
			if self.position[0] <= event.position[0] <= self.position[0] + 40 and \
				 self.position[1] <= event.position[1] <= self.position[1] + 40:
				self.container.imageClicked(event.position)
		elif event.kind == 'mouse_move':
			self.container.mouseOverImage()
		
	def setupComponents(self):
		path = os.path.join("Data", "Pics", "Abilities", "Frame.png")
		self.border = Image(file = path)
		self.image = None
		
	def clearImage(self):
		self.image = None
		
	def setImage(self, imagePath):
		if imagePath:
			path = os.path.join("Data", "Pics", "Abilities", imagePath + ".png")
			self.image = Image(file = path)
		else:
			self.image = None
		
	def draw(self, c, r):
		main_image_pos = self.position
		src_rect = (0, 0, 40, 40)
		dst_rect = (main_image_pos[0], main_image_pos[1], 
								main_image_pos[0] + 40, 
								main_image_pos[1] + 40)
		if self.image:
			self.image.draw(c, src_rect, dst_rect)
		if self.border:
			self.border.draw(c, src_rect, dst_rect)
