import os
from GUI import View, Image, Button

class SkinSelectView(View):
	def setupComponents(self, parent):
		ssv = SkinSelector(width=self.width, height=self.height - 300)
		ssv.position=(0, 0)
		ssv.initializeImages(self)
		self.add(ssv)
		
	def refreshComponent(self):
		pass
		
	def backClicked(self):
		self.container.setView(1)
		
	def picSelected(self, pic):
		self.model.setPicture(pic)
		self.container.setView(1)
	
class SkinSelector(View):
	xLimit = 7
	def initializeImages(self, parent):
		self.images = []
		self.imageNames = []
		skins = [file for file in os.listdir(os.path.join("Data", "Pics", "Actors")) if file[len(file) - 4:].upper() == ".PNG"]
		for skin in skins:
			self.images += [Image(file = os.path.join("Data", "Pics", "Actors", skin))]
			self.imageNames += [skin]
			
		btn = Button(title = "Back", action = self.backClicked, style = 'default')
		btn.position = ((self.width - btn.width) / 2, self.height - btn.height - 10)
		self.add(btn)
		
	def backClicked(self):
		self.container.backClicked()
			
	def handle_event(self, event):
		if event.kind == 'mouse_up':
			xAmt = (event.position[0] / 40)
			if xAmt < self.xLimit:
				yAmt = (event.position[1] / 40)
				selected = xAmt + yAmt * self.xLimit
				if 0 <= selected < len(self.imageNames):
					self.container.picSelected(self.imageNames[selected][:len(self.imageNames[selected]) - 4])
		
	def draw(self, c, r):
		on = 0
		for pic in self.images:
			#picturePath = os.path.join("Data", "Pics", "Actors", skin)
			pos = ((on % self.xLimit) * 40, (on / self.xLimit) * 40)
			src_rect = (39, 0, 39*2, 39)
			dst_rect = (pos[0], pos[1], pos[0] + src_rect[2] - src_rect[0], pos[1] + src_rect[3] - src_rect[1])
			pic.draw(c, src_rect, dst_rect)
			on += 1
			