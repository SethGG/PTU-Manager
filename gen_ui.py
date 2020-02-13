import tkinter as tk
import gen_lib
import pok_ui
from pprint import pprint

class TrainerLevelSpinbox(tk.LabelFrame):
	def __init__(self, parent):
		tk.LabelFrame.__init__(self, parent, text="Trainer Level")
		self.val = tk.StringVar()
		self.val.set(1)
		self.last_val = 1
		sb = tk.Spinbox(self, from_=1, to=40, textvariable=self.val)
		sb.pack()	
		self.val.trace('w', self.correctVal)
		
	def correctVal(self, a, b, c):
		try:
			tl = int(self.val.get())
		except:
			if not self.val.get():
				self.last_val = self.val.get()
				return
			self.val.set(self.last_val)
			return
		if tl > 40 or tl < 1:
			self.val.set(self.last_val)
		self.last_val = self.val.get()
		
	def getTrainerLevel(self):
		return int(self.val.get())
		
class HabitatChecklist(tk.LabelFrame):
	def __init__(self, parent):
		tk.LabelFrame.__init__(self, parent, text="Habitats")
		habitats = ["Arctic", "Beach", "Cave", "Desert", "Forest", "Freshwater", "Grassland", "Marsh", "Mountain", "Ocean", "Rainforest", "Taiga", "Tundra", "Urban"]
		self.vars = []
		for num,choice in enumerate(habitats):
			var = tk.StringVar(value="")
			self.vars.append(var)
			cb = tk.Checkbutton(self, var=var, text=choice, onvalue=choice, offvalue="", anchor="w", width=10)
			cb.grid(row=int(num%7), column=int(num/7))
			
	def getCheckedItems(self):
		values = []
		for var in self.vars:
			value =  var.get()
			if value:
				values.append(value)
		return values
		
class GenerateButton(tk.Button):
	def __init__(self, parent, t, h):
		tk.Button.__init__(self, parent, text="Generate", command=self.generatePokemon)
		self.parent = parent
		self.t = t
		self.h = h
		
	def generatePokemon(self):
		pokedex = gen_lib.createPokedex("pokedex.pickle")
		population = gen_lib.createPopulation(pokedex, self.h.getCheckedItems())
		pprint(population)
		sample = gen_lib.createSample(population, 5)
		pprint(sample)
		encounter = gen_lib.decideEncounter(pokedex, sample, self.t.getTrainerLevel())
		nature = gen_lib.pickNature("natures.csv")
		pok_ui.PokemonMenu(encounter, nature)
		
class GenerationMenu(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.title("PTU Pokémon Generator")
		self.geometry('240x270')
		self.resizable(False, False)	
		f = tk.Frame(self)
		f.place(relx=0.5, rely=0.5, anchor='c')	
		t = TrainerLevelSpinbox(f)
		t.pack(fill='both')
		h = HabitatChecklist(f)
		h.pack(fill='both')
		b = GenerateButton(f, t, h)
		b.pack(fill='both')	
