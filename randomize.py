import os
import random
import io
import zipfile
import json
import sys
import argparse

valid_folders = ["blocks", "chests", "entities", "gameplay"]

# Setup argument-parser
parser = argparse.ArgumentParser(description='Random loot table generator')
parser.add_argument('-s', '--seed', dest='seed', type=int, help='The seed you want to use for generating the random loot table. If none is specified, a random seed will be used.')
parser.add_argument('--mix', nargs='*', help= 'All folders you want to mix. Valid values are the following: {}. If you omit any of them in your list, its values won\'t be shuffled with the others but instead stay vanilla. If not specified, everything will be shuffled.'.format(', '.join(valid_folders)))

args = parser.parse_args()

# Validate arguments
if args.mix is not None:
	for folder in args.mix:
		if folder not in valid_folders:
			print('The --mix argument only accepts a list of the following folders: {}'.format(', '.join(valid_folders)))
			exit()
	if len(set(args.mix)) != len(args.mix):
		print('Each folder listed for --mix can only appear once.')
		exit()
	# If all or none of them are given, treat it like it's None
	if len(args.mix) == len(valid_folders) or len(args.mix) == 0:
		args.mix = None

# Explicit seed generation (allows for seed sharing even when no seed is specified)
if args.seed == None:
	args.seed = random.randrange(sys.maxsize)

# Prepare metadata and apply seed
random.seed(args.seed)
datapack_name = 'random_loot_{}'.format(args.seed)
datapack_desc = 'Loot Table Randomizer, Seed: {}'.format(args.seed)

if args.mix is not None:
	datapack_name += '_' + ''.join(map(lambda f: f[0], args.mix))
	datapack_desc += ', Folders: {}'.format(', '.join(valid_folders))

datapack_filename = datapack_name + '.zip'

print('Generating datapack...')

# Prepare the folder structure which will be used for the zip
to_mix = []
to_leave_vanilla = []

# If no folders are specified, just store all available tables
if args.mix is None:
	for dirpath, dirnames, filenames in os.walk('loot_tables'):
		for filename in filenames:
			to_mix.append(os.path.join(dirpath, filename))
# Otherwise split and store the tables for later processing
else:
	for folder in args.mix:
		for dirpath, dirnames, filenames in os.walk('loot_tables/{}'.format(folder)):
			for filename in filenames:
				to_mix.append(os.path.join(dirpath, filename))
	# Remaining tables need to be stored as well so they can be 'copied' over
	for to_leave_folder in set(valid_folders).difference(args.mix):
		for dirpath, dirnames, filenames in os.walk('loot_tables/{}'.format(to_leave_folder)):
			for filename in filenames:
				to_leave_vanilla.append(os.path.join(dirpath, filename))

# Shuffle and populate a dictionary with the replacements
replacement_dict = {}
remaining_to_mix = to_mix[:] # Copy so every table is used once

for file in to_mix:
	i = random.randint(0, len(remaining_to_mix)-1)
	replacement_dict[file] = remaining_to_mix[i]
	del remaining_to_mix[i]

# Use in-memory buffer to create compressed zip-file
zipbytes = io.BytesIO()
zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

# Write all the tables to the zip file but switch paths according to replacement-dict
for from_file in replacement_dict:
	with open(from_file) as file:
		contents = file.read()
		
	zip.writestr(os.path.join('data/minecraft/', replacement_dict[from_file]), contents)

# Write all the tables that should be left vanilla (simple content copy)
if args.mix is not None:
	for from_file in to_leave_vanilla:
		with open(from_file) as file:
			contents = file.read()
		zip.writestr(os.path.join('data/minecraft/', from_file), contents)	

# Write datapack-metadata
zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack_desc}}, indent=4))
zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack_name)]}))
zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack_name), 'tellraw @a ["",{"text":"Loot table randomizer by SethBling, modified by Joelius300","color":"green"}]')

# Finalize zip and create the actual file
zip.close()
with open(datapack_filename, 'wb') as file:
	file.write(zipbytes.getvalue())
	
print('Created datapack "{}"'.format(datapack_filename))