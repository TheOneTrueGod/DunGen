from GUI import View, Image, TextField, Font

from Code.UI.Components import *
from Globals import *

import Code.Units.Equipment as Equipment
EQUIPMENTSLOT = 1
INVENTORYSLOT = 0
class EquipmentView(ViewWithBackButton):
	def setupComponents(self, parent):
		separation = 5
		bottom = self.height - 50
		inventoryHeight = ((INVENTORYSLOTS - 1) / 8 + 1) * (30 + separation)
		descriptionHeight = 110
		#EquipmentTopLeft = (10, 10)
		#InventoryTopLeft = (10, bottom - inventoryHeight)
		#InvDescriptionTopLeft = (10, bottom - inventoryHeight - descriptionHeight)
		#EquipDescriptionTopLeft = (10, bottom - inventoryHeight - descriptionHeight * 2)
		
		InventoryTopLeft = (10, 10)
		InvDescriptionTopLeft = (10, 10 + inventoryHeight)
		EquipmentTopLeft = (10, 10 + inventoryHeight + 10 + descriptionHeight + 20)
		EquipDescriptionTopLeft = (10, 10 + inventoryHeight + 10 + descriptionHeight + 20 + 2 * (30 + separation))
		
		self.equipmentSlots = []
		for i in range(EQUIPMENTSLOTS):
			on = len(self.equipmentSlots)
			esl = InventorySlot(position=(EquipmentTopLeft[0] + (30 + separation) * (on % 7), EquipmentTopLeft[1] + (30 + separation) * (on / 7)))
			self.equipmentSlots += [esl]
			esl.setupComponents(self, [EQUIPMENTSLOT, on])
			self.add(esl)
		
		self.inventorySlots = []
		for i in range(INVENTORYSLOTS):
			on = len(self.inventorySlots)
			isl = InventorySlot(position=(InventoryTopLeft[0] + (30 + separation) * (on % 8), InventoryTopLeft[1] + (30 + separation) * (on / 8)))
			self.inventorySlots += [isl]
			isl.setupComponents(self, [INVENTORYSLOT, on])
			self.add(isl)
			
		self.inventoryDescriptionField = TextField(multiline=True, size=(self.width - InvDescriptionTopLeft[0] * 2, 100), position=InvDescriptionTopLeft, enabled=False)
		self.add(self.inventoryDescriptionField)
		
		self.equippedDescriptionField = TextField(multiline=True, size=(self.width - EquipDescriptionTopLeft[0] * 2, 100), position=EquipDescriptionTopLeft, enabled=False)
		self.add(self.equippedDescriptionField)

		ViewWithBackButton.setupComponents(self, parent)
		
	def itemClicked(self, inventorySlot):
		if inventorySlot[0] == INVENTORYSLOT:
			self.model.equipItem(inventorySlot[1])
		elif inventorySlot[0] == EQUIPMENTSLOT:
			self.model.unequipItem(inventorySlot[1])
		
	def mouseOverInventory(self, inventorySlot):
		if self.model.character:
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
					self.equippedDescriptionField.text = ""
		
	def characterChanged(self, model, character):
		if character:
			self.invalidate()
			on = 0
			for item in character.getInventoryList():
				if item:
					self.inventorySlots[on].setItemImage(item.getImage())
				else:
					self.inventorySlots[on].setItemImage(None)
				on += 1
			on = 0
			for item in character.getEquippedItems():
				if item:
					self.equipmentSlots[on].setItemImage(item.getImage())
				else:
					self.equipmentSlots[on].setItemImage(None)
				on += 1
		
class InventorySlot(View):
	def setupComponents(self, parent, slotNum):
		self.size = (30, 30)
		self.slotNum = slotNum
		
		self.eImg = EquipmentImage(position = (0, 0))
		self.eImg.setupComponents()
		self.add(self.eImg)
		
	def setItemImage(self, newItemImg):
		if newItemImg == None:
			if self.slotNum[0] == EQUIPMENTSLOT:
				self.eImg.setImage(Equipment.EmptyPics[self.slotNum[1]])
			elif self.slotNum[0] == INVENTORYSLOT:
				self.eImg.clearImage()
		else:
			self.eImg.setImage(newItemImg)
		
	def imageClicked(self, position):
		self.container.itemClicked(self.slotNum)
		
	def mouseOverImage(self):
		self.container.mouseOverInventory(self.slotNum)

class EquipmentImage(View):
	def handle_event(self, event):
		if event.kind == 'mouse_up':
			if self.position[0] <= event.position[0] <= self.position[0] + 40 and \
				 self.position[1] <= event.position[1] <= self.position[1] + 40:
				self.container.imageClicked(event.position)
		elif event.kind == 'mouse_move':
			self.container.mouseOverImage()
		
	def setupComponents(self):
		path = os.path.join("Data", "Pics", "Equipment", "EmptySlot.png")
		self.border = Image(file = path)
		self.image = None
		
	def clearImage(self):
		self.image = None
		
	def setImage(self, imagePath):
		path = os.path.join("Data", "Pics", "Equipment", imagePath + ".png")
		self.image = Image(file = path)
		
	def draw(self, c, r):
		main_image_pos = self.position
		src_rect = (0, 0, 30, 30)
		dst_rect = (main_image_pos[0], main_image_pos[1], 
								main_image_pos[0] + 30, 
								main_image_pos[1] + 30)
		if self.image:
			self.image.draw(c, src_rect, dst_rect)
		if self.border:
			self.border.draw(c, src_rect, dst_rect)
