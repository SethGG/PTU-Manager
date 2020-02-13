import tkinter as tk
import tkinter.ttk as ttk
import base64
from urllib.request import urlopen
from PIL import ImageTk, Image
import time

class MenuObserver:
	def levCallback(self, *args):
		self.menu.pokemon.setLevel(self.menu.lev.get())
		self.menu.hitp.set(self.menu.pokemon.hit_points)
		self.menu.hitpl.set(self.menu.hitp.get()-self.menu.pokemon.damage)
		self.menu.statp.set(self.menu.pokemon.stat_points)
		self.menu.movelist.drawMoves()
		for i in range(0,3):
			if i < len(self.menu.pokemon.active_abilities):
				self.menu.abils[i].set(self.menu.pokemon.active_abilities[i])
			else:
				self.menu.abils[i].set("")
	def hitplCallback(self, *args):
		self.menu.pokemon.damage = self.menu.hitp.get() - self.menu.hitpl.get()
	def totHPCallback(self, *args):
		self.menu.hitp.set(self.menu.pokemon.hit_points)
		self.menu.hitpl.set(self.menu.hitp.get()-self.menu.pokemon.damage)
	def totDefCallback(self, *args):
		self.menu.evns["Physical Evasion"].set(self.menu.pokemon.evasion["Physical Evasion"])
	def totSpDefCallback(self, *args):
		self.menu.evns["Special Evasion"].set(self.menu.pokemon.evasion["Special Evasion"])
	def totSpdCallback(self, *args):
		self.menu.evns["Speed Evasion"].set(self.menu.pokemon.evasion["Speed Evasion"])
	def addCallback(self, *args):
		stat = next(stat for stat, add in self.menu.adds.items() if args[0] == str(add))
		new_tot = self.menu.pokemon.base_stats[stat] + self.menu.adds[stat].get()
		self.menu.pokemon.setStat(stat, new_tot)
		self.menu.tots[stat].set(self.menu.statlist.genTotStatString(stat))
		self.menu.statp.set(self.menu.pokemon.stat_points)
	def stageCallback(self, *args):
		stat = next(stat for stat, stage in self.menu.stages.items() if args[0] == str(stage))
		self.menu.pokemon.combat_stages[stat] = self.menu.stages[stat].get()
		self.menu.tots[stat].set(self.menu.statlist.genTotStatString(stat))
	def __init__(self, menu):
		self.menu = menu
		for add in self.menu.adds.values():
			add.trace("w", self.addCallback)
		for stage in self.menu.stages.values():
			stage.trace("w", self.stageCallback)
		self.menu.tots["HP"].trace("w", self.totHPCallback)
		self.menu.tots["Defense"].trace("w", self.totDefCallback)
		self.menu.tots["Special Defense"].trace("w", self.totSpDefCallback)
		self.menu.tots["Speed"].trace("w", self.totSpdCallback)
		self.menu.hitpl.trace("w", self.hitplCallback)	
		self.menu.lev.trace("w", self.levCallback)
		
class PokemonMenu(tk.Tk):
	class NameDisplay(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, relief="solid", bd=1, bg="white")
			tk.Label(self, text=menu.pokemon.name, bg="white").pack()
	
	class SpriteDisplay(tk.Frame):
		def __init__(self, parent, menu):
			tk.Frame.__init__(self, parent, relief="solid", bd=1, bg="white")
			self.sprite = ImageTk.PhotoImage(file="images/sprites/001.png")
			tk.Label(self, image=self.sprite, bg="white").pack()
	
	class InfoDisplay(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, text="Info", relief="solid", bd=1, bg="white")
			tk.Label(self, text="Level", bg="white").grid(row=0, column=0, padx=(10,5), sticky="w")
			menu.lev = tk.IntVar(value=menu.pokemon.level)
			tk.Spinbox(self, from_=1, to=100, textvariable=menu.lev, width=3, bg="grey95", relief="groove", bd=2, highlightbackground="white").grid(row=0, column=1, padx=(5,10), sticky="w")
			tk.Label(self, text="Gender", bg="white").grid(row=1, column=0, padx=(10,5), sticky="w")
			tk.Label(self, text=menu.pokemon.gender, bg="white").grid(row=1, column=1, padx=(5,10), sticky="w")
			tk.Label(self, text="Nature", bg="white").grid(row=2, column=0, padx=(10,5), sticky="w")
			tk.Label(self, text=menu.pokemon.nature["Name"], bg="white").grid(row=2, column=1, padx=(5,10), sticky="w")
			tk.Label(self, text="Type", bg="white").grid(row=3, column=0, padx=(10,5), pady=(0,5), sticky="w")
			type_frame = tk.Frame(self, bg="white")
			self.type_img = []
			for type_ in menu.pokemon.dex_entry["Basic Information"]["Type"]:
				img = Image.open("images/types/"+type_.lower()+".gif")
				img_rgb = img.convert("RGB")		
				rgb = [x+int((255-x)*0.75) for i, x in enumerate(img_rgb.getpixel((1, 1)))]
				color = '#{:02x}{:02x}{:02x}'.format(*rgb)
				img = ImageTk.PhotoImage(img)
				self.type_img.append(img)
				f = tk.Frame(type_frame, relief="groove", bd=2, bg=color)
				tk.Label(f, image=img).pack(padx=2, pady=2)
				f.pack(side="left")
			type_frame.grid(row=3, column=1, padx=(5,10), pady=(0,5), sticky="w")
		
	class StatDisplay(tk.Frame):
		def __init__(self, parent, menu):
			tk.Frame.__init__(self, parent, bg="white")
			self.menu = menu
			s = tk.LabelFrame(self, text="Stats", relief="solid", bd=1, bg="white")
			b = tk.LabelFrame(self, text="Base", relief="solid", bd=1, bg="white")
			a = tk.LabelFrame(self, text="Added", relief="solid", bd=1, bg="white")
			c = tk.LabelFrame(self, text="Stage", relief="solid", bd=1, bg="white")
			t = tk.LabelFrame(self, text="Total", relief="solid", bd=1, bg="white")
			stat_list = ["HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"]
			menu.adds = {}
			menu.stages = {}
			menu.tots = {}
			for idx, stat in enumerate(stat_list):
				s.rowconfigure(idx, weight=1)
				b.rowconfigure(idx, weight=1)
				a.rowconfigure(idx, weight=1)
				c.rowconfigure(idx, weight=1, uniform=1)
				t.rowconfigure(idx, weight=1)
				menu.adds[stat] = tk.IntVar(value=menu.pokemon.total_stats[stat]-menu.pokemon.base_stats[stat])
				menu.tots[stat] = tk.StringVar(value=self.genTotStatString(stat))
				stat_short = stat.replace("Special Attack", "Sp. Atk").replace("Special Defense", "Sp. Def")
				if menu.pokemon.nature["Raise"] != menu.pokemon.nature["Lower"]:
					if stat == menu.pokemon.nature["Raise"]:
						stat_short += " ↑"
					elif stat == menu.pokemon.nature["Lower"]:
						stat_short += " ↓"
				tk.Label(s, text=stat_short, bg="white").grid(row=idx, column=0, padx=10, sticky="w")
				tk.Label(b, text=menu.pokemon.base_stats[stat], bg="white").grid(row=idx, column=0)
				tk.Spinbox(a, from_=0, to=99, textvariable=menu.adds[stat], width=2, bg="grey95", relief="groove", bd=2, highlightbackground="white").grid(row=idx, column=0)
				if stat != "HP":
					menu.stages[stat] = tk.IntVar(value=menu.pokemon.combat_stages[stat])
					tk.Spinbox(c, from_=-6, to=6, textvariable=menu.stages[stat], width=2, bg="grey95", relief="groove", bd=2, highlightbackground="white").grid(row=idx, column=0)
				tk.Label(t, textvariable=menu.tots[stat], bg="white").grid(row=idx, column=0, padx=5)
			b.columnconfigure(0, weight=1)
			a.columnconfigure(0, weight=1)
			c.columnconfigure(0, weight=1)
			t.columnconfigure(0, weight=1)
			s.pack(side="left", fill="y", padx=(0,5))
			b.pack(side="left", fill="y", padx=(0,5))
			a.pack(side="left", fill="y", padx=(0,5))
			c.pack(side="left", fill="y", padx=(0,5))
			t.pack(side="left", fill="y")
		
		def genTotStatString(self, stat):
			if stat == "HP" or self.menu.pokemon.combat_stages[stat] == 0:
				return str(self.menu.pokemon.total_stats[stat])
			elif self.menu.pokemon.combat_stages[stat] > 0:
				val = int((1 + 0.2 * self.menu.pokemon.combat_stages[stat]) * self.menu.pokemon.total_stats[stat])
			elif self.menu.pokemon.combat_stages[stat] < 0:
				val = int((1 + 0.1 * self.menu.pokemon.combat_stages[stat]) * self.menu.pokemon.total_stats[stat])
			return '{:d} ({:+d})'.format(val, val-self.menu.pokemon.total_stats[stat])
		
	class StatPointDisplay(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, text="Stat Points", relief="solid", bd=1, bg="white")
			menu.statp = tk.IntVar(value=menu.pokemon.stat_points)
			tk.Label(self, textvariable=menu.statp, bg="white").pack()
	
	class HitPointDisplay(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, text="Hit Points", relief="solid", bd=1, bg="white")
			menu.hitpl = tk.IntVar(value=menu.pokemon.hit_points-menu.pokemon.damage)
			tk.Spinbox(self, textvariable=menu.hitpl, width=3, from_=0, to=999, bg="grey95", relief="groove", bd=2,  highlightbackground="white").pack(side="left", expand=1, anchor="e", padx=(5,0), pady=(0,3))
			tk.Label(self, text = "/", bg="white").pack(side="left", padx=2, pady=(0,3))
			menu.hitp = tk.IntVar(value=menu.pokemon.hit_points)
			tk.Label(self, textvariable=menu.hitp, bg="white").pack(side="left", expand=1, anchor="w", padx=(0,5), pady=(0,3))
	
	class EvasionDisplay2(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, text="Evasion", relief="solid", bd=1, bg="white")
			evasion_list = ["Physical Evasion", "Special Evasion", "Speed Evasion"]
			menu.evns = {}
			for idx, evn in enumerate(evasion_list):
				menu.evns[evn] = tk.IntVar(value=menu.pokemon.evasion[evn])
				tk.Label(self, text=evn.split()[0], bg="white").grid(row=idx, column=0, padx=(10,5), sticky="w")
				tk.Label(self, textvariable=menu.evns[evn], bg="white").grid(row=idx, column=1, padx=(5,10), sticky="w")
	
	class EvasionDisplay(tk.Frame):
		def __init__(self, parent, menu):
			tk.Frame.__init__(self, parent, bg="white")
			s = tk.LabelFrame(self, text="Evasion", relief="solid", bd=1, bg="white")
			v = tk.LabelFrame(self, text="Score", relief="solid", bd=1, bg="white")
			evasion_list = ["Physical Evasion", "Special Evasion", "Speed Evasion"]
			menu.evns = {}
			for idx, evn in enumerate(evasion_list):
				menu.evns[evn] = tk.IntVar(value=menu.pokemon.evasion[evn])
				tk.Label(s, text=evn.split()[0], bg="white").pack(padx=10, anchor="w", expand=1)
				tk.Label(v, textvariable=menu.evns[evn], bg="white").pack(expand=1)
			s.pack(side="left", fill="y", padx=(0,1))
			v.pack(side="left", fill="y", padx=(1,0))
	
	class MoveDisplay(tk.LabelFrame):
		def __init__(self, parent, menu):
			tk.LabelFrame.__init__(self, parent, text="Moves", relief="solid", bd=1, bg="white")
			self.menu = menu
			self.move_widgets = [None] * 6
			self.first_img = ImageTk.PhotoImage(Image.open("images/types/normal.gif"))
			self.first_move = tk.Label(self, bd=2, compound="left", image=self.first_img, text=self.menu.pokemon.dex_entry["Move List"]["Level Up Move List"][0][1], padx=5, pady=2)
			for i in range(0,6):
				self.rowconfigure(i, uniform=1)
				m = tk.Frame(self, bg="white", relief="groove", bd=2)
				m.grid(row=i, column=0, padx=5, pady=(0,5), sticky="nsew")
			self.drawMoves()
		
		def drawMoves(self):
			def sameMove(i):
				try:
					return self.move_widgets[i]["text"] == self.menu.pokemon.moves[i][0]
				except:
					return False
			
			trash = []
			for i in range(0,6):
				if not sameMove(i):
					if self.move_widgets[i]:
						trash.append(self.move_widgets[i])
					if i < len(self.menu.pokemon.moves):
						m = tk.Label(self, relief="groove", bd=2, compound="left", anchor="w", padx=5, pady=2)
						img = Image.open("images/types/"+self.menu.pokemon.moves[i][1].lower()+".gif")
						img_rgb = img.convert("RGB")		
						rgb = [x+int((255-x)*0.75) for x in img_rgb.getpixel((1, 1))]
						bg_rgb = [x-15 for x in rgb]
						color = '#{:02x}{:02x}{:02x}'.format(*rgb)
						bg_color = '#{:02x}{:02x}{:02x}'.format(*bg_rgb)
						m.img = ImageTk.PhotoImage(img)
						m.configure(bg=color, image=m.img, text=self.menu.pokemon.moves[i][0])
						self.move_widgets[i] = m
						m.grid(row=i, column=0, padx=5, pady=(0,5), sticky="nsew")
						self.menu.CreateToolTip(m, self.menu, m["text"])
						self.update_idletasks()
					else:
						self.move_widgets[i] = None
			if all(x is None for x in self.move_widgets):
				self.first_move.grid(row=0, column=0, padx=5, pady=(0,5), sticky="nsew")
			else:
				self.first_move.grid_forget()
			for t in trash:
				t.grid_forget()
		
	class AbilityDisplay(tk.Frame):
		def __init__(self, parent, menu):
			tk.Frame.__init__(self, parent, bg="white")
			ranks = ["Basic Ability", "Advanced Ability", "High Ability"]
			menu.abils = []
			for i in range(0,3):
				menu.abils.append(tk.StringVar())
				if i < len(menu.pokemon.active_abilities):
					menu.abils[i].set(menu.pokemon.active_abilities[i])
				else:
					menu.abils[i].set("")
				a = tk.LabelFrame(self, text=ranks[i], relief="solid", bd=1, bg="white")
				tk.Label(a, textvariable=menu.abils[i], bg="white").pack(padx=5, pady=(0,5))
				self.rowconfigure(i, uniform=1)
				a.grid(row=i, column=0, sticky="nsew")

	class CreateToolTip:
		def __init__(self, widget, menu, text='widget info'):
			self.waittime = 500
			self.wraplength = 180
			self.widget = widget
			self.menu = menu
			self.text = text
			self.widget.bind("<Enter>", self.enter)
			self.widget.bind("<Leave>", self.leave)
			self.id = None
			self.tw = None

		def enter(self, event=None):
			self.schedule()

		def leave(self, event=None):
			self.unschedule()
			self.hidetip()

		def schedule(self):
			self.unschedule()
			self.id = self.widget.after(self.waittime, self.showtip)

		def unschedule(self):
			id = self.id
			self.id = None
			if id:
				self.widget.after_cancel(id)

		def showtip(self, event=None):
			x = self.menu.winfo_pointerx() + 10
			y = self.menu.winfo_pointery()
			self.tw = tk.Toplevel(self.widget)
			self.tw.wm_overrideredirect(True)
			self.tw.wm_geometry("+%d+%d" % (x, y))
			label = tk.Label(self.tw, text=self.text, justify='left', background="white", relief='solid', borderwidth=1, wraplength = self.wraplength)
			label.pack(ipadx=1)

		def hidetip(self):
			tw = self.tw
			self.tw= None
			if tw:
				tw.destroy()

	def __init__(self, pokemon):
		tk.Tk.__init__(self)
		self.pokemon = pokemon
		self.title("PTU Pokemon Menu")
		self.resizable(False, False)
		image = Image.open("images/background/ruby.png")
		image.thumbnail((1010,1010), Image.ANTIALIAS)
		self.img = ImageTk.PhotoImage(image)
		tk.Label(self, image=self.img).place(x=0, y=0, relwidth=1, relheight=1)
		
		i = tk.Frame(self, relief="solid", bd=1, bg="white")
		self.NameDisplay(i, self).grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")
		self.SpriteDisplay(i, self).grid(row=1, column=0, padx=(10,5), pady=10, sticky="n")
		self.InfoDisplay(i, self).grid(row=1, column=1, padx=(5,10), pady=(1,10), sticky="nsew")
		i.grid(row=0, column=0, pady=(20,5), columnspan=2)
		
		s = tk.Frame(self, relief="solid", bd=1, bg="white")
		self.statlist = self.StatDisplay(s, self)
		self.statlist.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=10, pady=(5,10))
		self.StatPointDisplay(s, self).grid(row=0, column=1, sticky="nsew", padx=(0,10), pady=(5,0))
		self.HitPointDisplay(s, self).grid(row=1, column=1, sticky="nsew", padx=(0,10), pady=(1,0))
		self.EvasionDisplay2(s, self).grid(row=2, column=1, sticky="nsew", padx=(0,10), pady=(1,10))
		s.grid(row=1, column=0, padx=20, pady=5, columnspan=2)

		a = tk.Frame(self, relief="solid", bd=1, bg="white")
		self.abillist = self.AbilityDisplay(a, self)
		self.abillist.pack(padx=10, pady=(5,10))
		a.grid(row=2, column=0, padx=5, pady=(5,20), sticky="ne")
		
		m = tk.Frame(self, relief="solid", bd=1, bg="white")
		self.movelist = self.MoveDisplay(m, self)
		self.movelist.pack(padx=10, pady=(5,10))
		m.grid(row=2, column=1, padx=5, pady=(5,20), sticky="nw")
		
		MenuObserver(self)
