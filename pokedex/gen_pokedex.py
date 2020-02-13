#!/usr/bin/env python3

from PyPDF4 import PdfFileReader
from pprint import pprint
import re
import sys
import pickle

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

def processPage(page):

	def processName(raw):
		processed = raw.strip()
		new = ""
		for idx, char in enumerate(processed):
			if idx == 0 or processed[idx-1] == "-" or processed[idx-1] == " ":
				new += char
			else:
				new += char.lower()
		return new

	def processBaseStats(raw):
		processed = "\n".join(x.strip() for x in raw.splitlines() if not x.isspace())
		base_stats = {}
		regex = re.compile(r"^(.+):$\n^(\d+)$", re.MULTILINE)
		for match in regex.findall(processed):
			base_stats[match[0]] = int(match[1])
		return base_stats
	
	def processBasicInfo(raw):
		processed = "\n".join(x.strip() for x in raw.splitlines() if not x.isspace())
		basic_info = {}
		
		regex = re.compile(r"^Type : (.+)$", re.MULTILINE)
		for match in regex.findall(processed):
			basic_info["Type"] = match.split(" / ")
			
		regex = re.compile(r"^(\w+ Ability)(?: \d)?: (.+)$", re.MULTILINE)
		for match in regex.findall(processed):
			if match[0] in basic_info:
				basic_info[match[0]].append(match[1])
			else:
				basic_info[match[0]] = [match[1]]
		
		regex = re.compile(r"^Evolution:$\n^(.+)\Z", re.MULTILINE|re.DOTALL)
		for match in regex.findall(processed):
			regex = re.compile(r"^(\d - .+?)(?=$\n^\d -|\Z)", re.MULTILINE|re.DOTALL)
			basic_info["Evolution"] = [x.replace("\n", " ") for x in regex.findall(match)]

		return basic_info
	
	def processSizeInfo(raw):
		processed = "\n".join(x.strip() for x in raw.splitlines() if not x.isspace())
		size_info = {}
		regex = re.compile(r"^(\w+) : (.+) \((\w+)\)$", re.MULTILINE)
		for match in regex.findall(processed):
			size_info[match[0]] = list(match[1:])
		return size_info
	
	def processBreedInfo(raw):
		processed = "\n".join(x.strip() for x in raw.splitlines() if not x.isspace())
		breed_info = {}
		
		gen_regex = re.compile(r"^Gender Ratio  : (.+)$", re.MULTILINE)
		for match in gen_regex.findall(processed):
			breed_info["Gender Ratio"] = match.split(" / ")
			
		egg_regex = re.compile(r"^Egg Group : (.+)$", re.MULTILINE)
		for match in egg_regex.findall(processed):
			breed_info["Egg Group"] = match.split(" / ")
		
		hat_regex = re.compile(r"^Average Hatch Rate: (.+)$", re.MULTILINE)
		for match in hat_regex.findall(processed):
			breed_info["Average Hatch Rate"] = match
		
		diet_regex = re.compile(r"^Diet : (.+)$", re.MULTILINE)
		for match in diet_regex.findall(processed):
			breed_info["Diet"] = match.split(", ")
		
		hab_regex = re.compile(r"^Habitat  ?: (.+)\Z", re.MULTILINE|re.DOTALL)
		for match in hab_regex.findall(processed):
			breed_info["Habitat"] = match.replace("\n", " ").split(", ")
		
		return breed_info
	
	def processCapList(raw):
		processed = "".join(x.replace("-", "") for x in raw.strip().splitlines())
		regex = re.compile(r", *(?![^\(]+\))")
		cap_list = regex.split(processed)
		return cap_list
	
	def processSkillList(raw):
		processed = "".join(x.replace("-", "") for x in raw.strip().splitlines())
		skill_list = processed.split(", ")
		return skill_list
	
	def processMoveList(raw):
		processed = "\n".join(x.strip() for x in raw.splitlines() if not x.isspace())
		move_list = {}
		
		regex = re.compile(
			r"^Level Up Move List$\n^(.+?)(?=$\n^[^\n]+ Move List$|\Z)", re.MULTILINE|re.DOTALL)
		for match in regex.findall(processed):
			regex = re.compile(r"^(\d+)  (.+) - (\w+)$", re.MULTILINE)
			move_list["Level Up Move List"] = [list(x) for x in regex.findall(match)]
		
		regex = re.compile(
			r"^TM/HM Move List$\n^(.+?)(?=$\n^[^\n]+ Move List$|\Z)", re.MULTILINE|re.DOTALL)
		for match in regex.findall(processed):
			merged = match.replace("\n", " ").replace(" - ", "").replace("- ", "-")
			regex = re.compile(r"(A?\d+) (.+?)(?= ?, |\Z)")
			move_list["TM/HM Move List"] = [list(x) for x in regex.findall(merged)]
		
		regex = re.compile(
			r"^Egg Move List$\n^(.+?)(?=$\n^[^\n]+ Move List$|\Z)", re.MULTILINE|re.DOTALL)
		for match in regex.findall(processed):
			merged = match.replace("\n", " ").replace(" - ", "").replace("- ", "-")
			regex = re.compile(r" ?, ")
			move_list["Egg Move List"] = regex.split(merged)
			
		regex = re.compile(
			r"^Tutor Move List$\n^(.+?)(?=$\n^[^\n]+ Move List$|\Z)", re.MULTILINE|re.DOTALL)
		for match in regex.findall(processed):
			merged = match.replace("\n", " ").replace(" - ", "").replace("- ", "-")
			regex = re.compile(r" ?, ")
			move_list["Tutor Move List"] = regex.split(merged)
		
		return move_list

	regex = re.compile(
		r"^(\d+)$\n" + 
		r"^([^\n]+?)$\n" +
		r"^.+?$\n" +
		r"^ *Base Stats: *$\n" +
		r"^(.+?)$\n" +
		r"^ *Basic Information *$\n" +
		r"^(.+?)$\n" +
		r"^ *Size Information *$\n" +
		r"^(.+?)$\n" +
		r"^ *Breeding Information *$\n" +
		r"^(.+?)$\n" +
		r"^ *Capability List *$\n" +
		r"^(.+?)$\n" +
		r"^ *Skill List *$\n" +
		r"^(.+?)$\n" +
		r"^ *Move List *$\n" +
		r"^(.+?)$\n" +
		r"(?=\Z|^ *Mega Evolution *\w?$\n)",
		re.MULTILINE|re.DOTALL)
	
	page_dict = {}	
	for match in regex.findall(page):
		page_dict["Page Number"] = match[0]
		page_dict["Name"] = processName(match[1])
		page_dict["Base Stats"] = processBaseStats(match[2])
		page_dict["Basic Information"] = processBasicInfo(match[3])
		page_dict["Size Information"] = processSizeInfo(match[4])
		page_dict["Breeding Information"] = processBreedInfo(match[5])
		page_dict["Capability List"] = processCapList(match[6])
		page_dict["Skill List"] = processSkillList(match[7])
		page_dict["Move List"] = processMoveList(match[8])
		
	return page_dict
    
def readPage(num, pdf_toread):
	page = pdf_toread.getPage(num)

	page_text = page.extractText()
	page_text = page_text.replace('˜', "Th")
	page_text = page_text.replace('˚', "fi")
	page_text = page_text.replace('™', '’')
	page_text = page_text.replace('ﬂ', '”')
	page_text = page_text.replace('˝', 'ft')
	page_text = page_text.replace('ˆ', 'fl')
	page_text = page_text.replace('˛', 'ff')
	
	return page_text

def createPokedex(file):
	pdf_toread = PdfFileReader(file)
	num_of_pages = pdf_toread.getNumPages()
	pokedex = {}
	
	print("Building Pokedex Dictionary")
	for i in range(num_of_pages):
		page = readPage(i, pdf_toread)
		pokemon = processPage(page)
		if pokemon:
			pokedex[pokemon["Name"]] = pokemon
	
	print("Build Complete, " + str(len(pokedex)) + " Pokemon In Dictionary")
	pickle_out = open("pokedex.pickle", "wb")
	pickle.dump(pokedex, pickle_out)
	pickle_out.close()

if __name__== "__main__":
	createPokedex(sys.argv[1])
