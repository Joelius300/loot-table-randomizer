This is a modified version of SethBlings 'Loot Table Randomizer'. I have added the possibility to only mix parts of the vanilla set (e.g. only mix the blocks or mix blocks and chests). I have also made sure that if you don't specify a seed, you can still retrieve it later to create the same pack again (this was a big missed opportunity in the original script).

The original script by SethBling can be found in the file 'original.py' of this repo. The folder 'loot_tables' is used by the script and contains the loot_tables for Minecraft 1.14.

Ps. You should watch [SethBlings video](https://www.youtube.com/watch?v=3JEXAZOrykQ) about this script (and like it (and subscribe)).  
Pps. this is my first python script, I know it's not perfect.

### Usage

```
usage: randomize.py [-h] [-s SEED] [--mix [MIX [MIX ...]]]

Random loot table generator

optional arguments:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  The seed you want to use for generating the random
                        loot table. If none is specified, a random seed will
                        be used.
  --mix [MIX [MIX ...]]
                        All folders you want to mix. Valid values are the
                        following: blocks, chests, entities, gameplay. If you
                        omit any of them in your list, its values won't be
                        shuffled with the others but instead stay vanilla. If
                        not specified, everything will be shuffled.
```

### Credits

- Credits for all the minecraft stuff goes to [Mojang](https://www.minecraft.net/) of course.
- Credits for the original script including the idea and everything related goes to [SethBling](https://www.youtube.com/channel/UC8aG3LDTDwNR1UQhSn9uVrw).