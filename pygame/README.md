# Rhythm Rush
Rush through 3 intense levels by jumping over obstacles! Includes multiple songs, gamemodes, and mechanics!\
<br>

# Playing
Press space or click to jump. The game starts simple but progressively gets harder. As you encounter new objects,
experiment to find out what they do.

# Making Levels
Levels were designed to be easily customisable. All you have to do is copy the `template.level` file into the `levels`
folder, rename it, and start creating!

## Naming
The file name of the level does not matter, however, the order that they show up in game will follow the alphabetical
order of the files.

The name that you put inside the file will show up in game.

## Music
Put an audio file in the `levels/music` folder then put the file name in the music field of the level file.

## Colour
The colour field only changes the background colour on the level select screen. Changing the colour of the actual level
must be done by using the [background trigger](#background-trigger).

## Level
This is an array of arrays representing a grid that makes up the level. Change each object by changing the string from
"00" to the code for your object. Here are a list of objects:

### Spike
Code: `S1`\
A triangle which kills the player when touched

### Spike (flipped)
Code: `S2`\
Same as [Spike](#spike) but upside-down

### Short spike
Code: `s1`
Same as [Spike](#spike) but half the height

### Short spike (flipped)
Code: `s2`
Same as [Short spike](#short-spike) but upside-down

### Block
Code: `B1`
A block that the player can land on without dying. Still kills player if they run into it from the side

### Half block
Code: `b1`
Same as [Block](#block) but half the height. Goes on upper half of the grid

### Cube portal
Code: `P0`
A portal which transforms the player into the cube gamemode (default gamemode)

### Ship portal
Code: `P1`
A portal which transforms the player into the ship gamemode

### Yellow pad
Code: `p1`
A pad that launches the player upwards when touched

### Yellow orb
Code: `o1`
An orb that launches the player upwards when they try to jump and are touching it

### Background trigger
Code: `bg`
An invisible trigger that changes the background colour when passed

__Usage__\
The trigger can be put anywhere in a column and does not need to be touched by the player to activate. It is usually
put at the top but does not need to be.

After the trigger code, put a hex code representing the desired background colour

__Example__\
`bg#ffffff`

__Fixing the grid__\
Due to this object taking up more than 2 characters, it can break the grid of the level text file, making the rest
of the level hard to edit. To fix this, simply delete both zeroes in the following 3 objects and 1 zero in the 4th.

<u>Example:</u>\
Change this: `"bg#ffffff", "00", "00", "00", "00"`\
To this: `"bg#ffffff", "", "", "", "0"`

# Challenges
## Physics
Getting the physics of the game to feel natural and intuitive took a lot of work. This was mostly a trial-and-error
process by changing jump and gravity values then testing to see how it felt. One thing that still does not work very
well is the ship physics, although they are good enough to not be a priority.

## Integer overflow
The way the game works is by pre-rendering the entire level on a surface then using `blit` to copy it. To move the level,
the entire surface is moved, giving the illusion of objects moving. This was done in an attempt to reduce the rendering
time per frame by not needing to render objects individually while playing, only at the expense of memory usage which
is not a big priority. This caused a major issue, however. Due to the long length of levels, the game would cause an
integer overflow as the surface width exceeded 65535, the 16-bit unsigned integer limit. This would cause the objects
at the end of the level to render at the start.

To solve this, the rendering system was modified to render onto a surface which is maxed out at the integer limit. If
extra width is necessary, a new surface would be created. All of the surfaces are stored in a list and placed side-by-side
to make it seem as if they were 1.

# Peer Review
From the in-class exercise, this game was shared with Gabe. He gave the following suggestions:

__Practice mode__
This mode would let you set checkpoints to respawn from, allowing you to learn the level before trying to beat it
fully. This was considered, although could not be completed due to lack of time.

__Basic triggers__
Triggers are objects that could cause changes to the level. More advanced ones could do things such as move objects or
control the camera, although it was mostly basic ones that were suggested. Only 1 trigger was implemented, which is the
[background trigger](#background-trigger). However, the background trigger was implemented in a way that would allow other
triggers to be added without much extra work.

# Changelog
All changes are described in the Git commit history

# Credits
This game was heavily inspired by Geometry Dash by RobTop\
All code was created by me unless otherwise indicated.

# Note on the game
Like the original game it was inspired by, this game is designed to be learned through trial-and-error. There is intentionally
no tutorial or instructions as players learn by trying it out. Mechanics are introduced progressively to give time for the
player to learn. Due to its simple control scheme, it will usually only take a few tries at most.