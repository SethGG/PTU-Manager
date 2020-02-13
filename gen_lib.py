import csv
import random
import pickle

def loadPokedex(file):
	pickle_in = open(file, "rb")
	pokedex = pickle.load(pickle_in)
	pickle_in.close()
	return pokedex

def loadPool(file):
	sheet = open(file)
	pool = [x for x in csv.DictReader(sheet)]
	sheet.close()
	return pool

def generatePokemon(pokedex, pool, habitats, tlevel):

	def createPopulation(pokedex, pool, habitats):
		population = []
		for pokemon in pool:
			if pokemon["Name"] in pokedex:
				for h in pokedex[pokemon["Name"]]["Breeding Information"]["Habitat"]:
					if h in habitats:
						for x in range(0,int(pokemon["Rarity"])):
							population.append(pokemon["Name"])
						break
		return population

	def createSample(population, size):
		sample = random.sample(population, size)
		return sample
	
	def decideEncounter(pokedex, sample, tlevel):
		scores = []
		for pokemon in sample:
			stat_sum = sum(x for x in pokedex[pokemon]["Base Stats"].values())
			scores.append((stat_sum-20-tlevel)**2)
		encounter = next(x for _,x in sorted(zip(scores,sample)))
		return encounter
	
	population = createPopulation(pokedex, pool, habitats)
	sample = createSample(population, 4)
	return decideEncounter(pokedex, sample, tlevel)
