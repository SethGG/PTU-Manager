import random
import csv

class PokemonObject:
	def __init__(self, dex_entry, level=1):
		def pickGender(self):
			try:
				male_chance = float(self.dex_entry["Breeding Information"]["Gender Ratio"][0].split("%")[0])
				if random.randint(0, 99) < male_chance:
					self.gender = "Male"
				else:
					self.gender = "Female"
			except:
				self.gender = "No Gender"
		def pickNature(self):
			sheet = open("pokedex/natures.csv")
			natures = [dict(x) for x in csv.DictReader(sheet)]
			sheet.close()
			self.nature = random.choice(natures)
		def pickAbilities(self):
			self.genetic_abilities = [random.choice(dex_entry["Basic Information"]["Basic Ability"])]
			self.genetic_abilities.append(random.choice(dex_entry["Basic Information"]["Adv Ability"]))
			self.genetic_abilities.append(random.choice(dex_entry["Basic Information"]["High Ability"]))
		def setBaseStats(self):
			self.base_stats = self.dex_entry["Base Stats"].copy()
			self.base_stats[self.nature["Raise"]] += (2 - int(self.nature["Raise"] == "HP"))
			self.base_stats[self.nature["Lower"]] -= (2 - int(self.nature["Lower"] == "HP"))
			self.base_stats[self.nature["Lower"]] = max(1, self.base_stats[self.nature["Lower"]])
			inv_dict = {}
			for stat, value in self.base_stats.items():
				inv_dict.setdefault(value, []).append(stat)
			self.base_relation = [inv_dict[x] for x in sorted(inv_dict.keys())]
		def setTotalStats(self):
			self.total_stats = self.base_stats.copy()
		def setCombatStages(self):
			self.combat_stages = {x : 0 for x in self.base_stats.keys() if x != "HP"}
		def setEvasion(self):
			self.evasion = {
				"Physical Evasion" : int(self.total_stats["Defense"] / 5),
				"Special Evasion" : int(self.total_stats["Special Defense"] / 5),
				"Speed Evasion" : int(self.total_stats["Speed"] / 5)
			}
		def setName(self):
			self.name = self.dex_entry["Name"]
		def setDamage(self):
			self.damage = 0
		def rollShiny(self):
			self.shiny = not bool(random.randint(0, 99))
	
		self.dex_entry = dex_entry
		setName(self)
		rollShiny(self)
		pickGender(self)
		pickNature(self)
		pickAbilities(self)
		setBaseStats(self)
		setTotalStats(self)
		setCombatStages(self)
		setEvasion(self)
		setDamage(self)
		self.setLevel(level)

	def setLevel(self, level):
		self.level = level
		self.active_abilities = self.genetic_abilities[:1+int(self.level/20)]
		self.moves = [x[1:] for x in self.dex_entry["Move List"]["Level Up Move List"] if int(x[0]) <= self.level][-6:]
		self.calcHitPoints()
		self.calcStatPoints()
		
	def setStat(self, stat, value):
		self.total_stats[stat] = value
		if stat == "HP":
			self.calcHitPoints()
		elif stat == "Defense":
			self.evasion["Physical Evasion"] = int(self.total_stats[stat] / 5)
		elif stat == "Special Defense":
			self.evasion["Special Evasion"] = int(self.total_stats[stat] / 5)
		elif stat == "Speed":
			self.evasion["Speed Evasion"] = int(self.total_stats[stat] / 5)
		self.calcStatPoints()
	
	def calcHitPoints(self):
		self.hit_points = self.level + (3 * self.total_stats["HP"]) + 10
		if self.damage > self.hit_points:
			self.damage = self.hit_points
		
	def calcStatPoints(self):
		self.stat_points = self.level + 10 + sum(self.base_stats.values()) - sum(self.total_stats.values())
		
	def checkLegal(self):
		if self.level < 1:
			print("Level can't be lower than 1")
		if self.stat_points < 0:
			print("More stat points spend than available")
		for idx, rank in enumerate(self.base_relation[:-1]):
			upstream = [stat for rank in self.base_relation[idx+1:] for stat in rank]
			for stat in rank:
				if self.total_stats[stat] >= min([self.total_stats[x] for x in upstream]):
					print(stat + " does not follow base relation rule")
