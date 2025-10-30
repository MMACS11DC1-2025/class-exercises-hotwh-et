# Recursive Fractal Generator
When you first run the program, it will be a blank canvas. Nothing will happen until you spawn something with an input.

## Note on Performance
Due to there being too many configurable settings, it is impractical to list the limits for every scenario. Where applicable, a range will be given as a guideline. However, going past it may not always cause issues, depending on your other settings and the number of balls.

## Inputs
### Spawning a fractal ball
Spawn a fractal ball by simply putting a number in the input. This number will be the length of the first branch.\
```
Input: 50
```

### Configuring settings
You can change the settings by typing its name (case-insensitive) followed by the value. All settings are numbers, with decimals supported (note that some settings will truncate the decimals)

For example, the following input will set the speed to 2:
```
Input: speed 2
```

All of the following settings are available to be changed:
- Max FPS
- Speed
- Width
- Branch angle range
- Branches
- Min branch length
- Decline rate

__Max FPS__\
This is simply a cap on FPS, and does not actually change the performance. This is meant to prevent fluctuations in FPS when changing settings

__Speed__\
This a multiplier to the vector, and does not impact the performance

__Width__\
This defines the width of the stroke, and makes no impact to the radius of the balls. It should not make a noticeable impact to performance

__Branch angle range__\
This is the total angle that the child branches will span. It should not make a noticeable impact to performance

__Branches__\
This defines how many branches will grow at each layer. This makes a big impact on performance. It is recommended to keep this value from 2-5.

__Min branch length__\
This is the minimum branch length before it stops branching out. It is recommended to keep this value from 20-50

__Decline rate__\
This is the rate at which the branch length will decline by. For example if the rate is 2, the length of the child branches will be 1/2 of their parent branch. It is recommended to keep this value from 1.7-3