import os
import random
import io
import zipfile
import json
import sys
import argparse
import types

def parse_args():
    """Setup argument-parser and parse command line arguments. Arguments are validated before returning."""
    parser = argparse.ArgumentParser(description='Random loot table generator')
    parser.add_argument('-s', '--seed', dest='seed', type=int, help='The seed you want to use for generating the random loot table. If none is specified, a random seed will be used.')
    parser.add_argument('--mix', nargs='*', action='append',
    help= f"A set of folders you want to mix. Valid values are the following: {', '.join(valid_folders)}. " \
    "If you omit any of them in all of your lists, its values won\'t be shuffled with the others but instead stay vanilla. " \
    "If not specified, everything will be shuffled. You can specify multiple --mix sets which not be mixed with the other sets. " \
    "However each folder can only appear once of course.")

    args = parser.parse_args()
    validate_args(args)
    return args

def validate_args(args):
    """Validate arguments from command line."""
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

def get_packdata(args):
    """Construct metadata for the datapack.

The returned metadata-object exposes a name, a desc (description) and a filename.
    """
    datapack = types.SimpleNamespace()
    datapack.name = 'random_loot_{}'.format(args.seed)
    datapack.desc = 'Loot Table Randomizer, Seed: {}'.format(args.seed)

    if args.mix is not None:
        datapack.name += '_' + ''.join(map(lambda f: f[0], args.mix))
        datapack.desc += ', Folders: {}'.format(', '.join(valid_folders))

    datapack.filename = datapack.name + '.zip'

    return datapack

def fill_mix_lists(args, to_mix, to_leave_vanilla):
    """Fills the given lists with file-paths according to the arguments."""
    # If no folders are specified, just store all available tables
    if args.mix is None:
        for dirpath, _, filenames in os.walk('loot_tables'):
            for filename in filenames:
                to_mix.append(os.path.join(dirpath, filename))
    # Otherwise split and store the tables for later processing
    else:
        for folder in args.mix:
            for dirpath, _, filenames in os.walk('loot_tables/{}'.format(folder)):
                for filename in filenames:
                    to_mix.append(os.path.join(dirpath, filename))
        # Remaining tables need to be stored as well so they can be 'copied' over
        for to_leave_folder in set(valid_folders).difference(args.mix):
            for dirpath, _, filenames in os.walk('loot_tables/{}'.format(to_leave_folder)):
                for filename in filenames:
                    to_leave_vanilla.append(os.path.join(dirpath, filename))

def get_replacement_dict(to_mix):
    """Returns a dictionary which contains substitutes for the loot_tables (shuffled)."""
    replacement_dict = {}
    remaining_to_mix = to_mix[:] # Copy so every table is used once

    for file in to_mix:
        i = random.randint(0, len(remaining_to_mix)-1)
        replacement_dict[file] = remaining_to_mix[i]
        del remaining_to_mix[i]

    return replacement_dict

def write_zip_swapped(zip, replacement_dict):
    """Write all the tables to the zip file but switch paths according to replacement-dict."""
    for from_file in replacement_dict:
        with open(from_file) as file:
            contents = file.read()

        zip.writestr(os.path.join('data/minecraft/', replacement_dict[from_file]), contents)

def write_zip_vanilla(zip, to_leave_vanilla):
    """Write all the tables that should be left vanilla (simple content copy)."""
    for from_file in to_leave_vanilla:
        with open(from_file) as file:
            contents = file.read()
        zip.writestr(os.path.join('data/minecraft/', from_file), contents)

def write_metadata(zip, datapack):
    """Write datapack-metadata to zip."""
    zip.writestr('pack.mcmeta', json.dumps({'pack':{'pack_format':1, 'description':datapack.desc}}, indent=4))
    zip.writestr('data/minecraft/tags/functions/load.json', json.dumps({'values':['{}:reset'.format(datapack.name)]}))
    zip.writestr('data/{}/functions/reset.mcfunction'.format(datapack.name), 'tellraw @a ["",{"text":"Loot table randomizer by SethBling, modified by Joelius300","color":"green"}]')

def finalize_zip(zip, filename):
    """Finalize zip and create the actual file."""
    zip.close()
    with open(filename, 'wb') as file:
        file.write(zipbytes.getvalue())

if __name__ == '__main__':
    valid_folders = ["blocks", "chests", "entities", "gameplay"]

    # Parse options from command line args
    args = parse_args()

    # Apply seed
    random.seed(args.seed)

    # Get metadata
    datapack = get_packdata(args)

    print('Generating datapack...')

    # Prepare the folder structure which will be used for the zip
    to_mix = []
    to_leave_vanilla = []

    fill_mix_lists(args, to_mix, to_leave_vanilla)
    replacement_dict = get_replacement_dict(to_mix)

    # Use in-memory buffer to create compressed zip-file
    zipbytes = io.BytesIO()
    zip = zipfile.ZipFile(zipbytes, 'w', zipfile.ZIP_DEFLATED, False)

    # Write loot tables and metadata to zip
    if args.mix is not None:
        write_zip_vanilla(zip, to_leave_vanilla)
    write_zip_swapped(zip, replacement_dict)
    write_metadata(zip, datapack)

    # Create file
    finalize_zip(zip, datapack.filename)

    print('Created datapack "{}"'.format(datapack.filename))