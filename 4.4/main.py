"""
Make An Interactive Drawing or Animation 
Explore the turtle drawing package to create an interactive drawing.
It should use a while loop.
Your program should also include at least one function you’ve made yourself 
"""
import random
import threading
import time
import turtle
import re

SETTINGS = {
	"max_fps": 60,
	"speed": 1,
	"width": 3,
	"branch_angle_range": 90,
	"branches": 5,
	"min_branch_length": 20,
	"decline_rate": 1.9,
}

totalCount = 0
lastFrameTime = 0
fps = 0

t = turtle.Turtle()

# Change turtle settings to increase draw speed
t.hideturtle()
t.speed(0)
turtle.delay(0)
turtle.tracer(0)

# Use a different thread for handling input
# Extends class from threading module
class KeyboardThread(threading.Thread):
    def __init__(self, inputCallback = None, name='keyboard-input-thread'):
        self.inputCallback = inputCallback
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
		# Repeatedly accept input and pass it as an argument to the callback function
        while True:
            self.inputCallback(input("Input: "))

# Utility function to generate a random colour
def random_colour():
	return (random.random(), random.random(), random.random())

# Ball class representing a fractal ball
# Explained in more detail in README.md
class Ball:
	def __init__(self, pos, radius, vector, colour=None):
		self.pos = pos
		self.radius = radius
		self.vector = vector
		self.colour = colour if colour is not None else random_colour()
		self.totalLength = radius

	# Method to be called every draw loop
	def draw(self, t):
		count = 0
		# Use the vector multiplied by set speed and add it to the position to move the ball
		self.pos[0] += self.vector[0] * SETTINGS["speed"]
		self.pos[1] += self.vector[1] * SETTINGS["speed"]
		self.pos[2] += self.vector[2] * SETTINGS["speed"]
		t.penup()
		t.color(self.colour)
		t.goto((self.pos[0], self.pos[1]))
		# Loop for each branch
		for i in range(int(SETTINGS["branches"])):
			# Call the recursive function and evenly divide each branch across the 360 degrees of a circle
			value = self.drawBranch(t, i * (360 / SETTINGS["branches"]) + self.pos[2], self.radius)
			count += value[0]
			self.totalLength = value[1]
		return count
	
	# Recursive function
	# Explained in more detail in README.md
	def drawBranch(self, t, direction, length):
		count = 0
		totalLength = 0
		# Base case: if length is <= set min length
		if (length <= SETTINGS["min_branch_length"]):
			return (1, 0)
		t.setheading(direction)
		t.pendown()
		t.forward(length)
		
		# The angle difference in between each branch
		angleDifference = SETTINGS["branch_angle_range"] / (int(SETTINGS["branches"]) - 1)
		# Loop for each branch
		for i in range(int(SETTINGS["branches"])):
			# Call the recursive function and evenly divide each branch across the set angle range
			# Decrease the length by the set decline rate
			value = self.drawBranch(t, direction - (SETTINGS["branch_angle_range"] / 2) + (i*angleDifference), length/SETTINGS["decline_rate"])
			count += value[0]
			totalLength = value[1]

		t.penup()
		t.setheading(direction)
		t.backward(length)

		return (count, totalLength + length)

	# Various getter and setter methods
	def setVector(self, vector):
		self.vector = vector
	
	def getPos(self):
		return self.pos
	
	def getRadius(self):
		return self.radius
	
	def getVector(self):
		return self.vector
	
	# Total length used for collision calculation
	def getTotalLength(self):
		return self.totalLength

# All balls are added to this list
balls = []

def spawnBall(radius, pos=None, vector=None):
	# Set default values if argument not passed
	if not pos:
		pos = [0, 0, 0]
	if not vector:
		# Randomly generate a vector
		# The division is required to generate a decimal
		vector = [random.randrange(-1000, 1000)/1e2, random.randrange(-1000, 1000)/1e2, random.randrange(-10, 10)]
	ball = Ball(pos, radius, vector)
	balls.append(ball)

def handleInput(input):
	if input:
		changedSetting = False
		for setting in SETTINGS.keys():
			# For each key, replace the underscore with a space, then check if the input is prefixed by it
			if input.lower().startswith(setting.lower().replace("_", " ")):
				convertedInput = 0
				try:
					# Use regex to remove any non numeric or decimal characters
					convertedInput = float(re.sub("[^\\d.]", "", input))
				except ValueError:
					print("Invalid setting value!")
					return
				# Extra check is necessary as branches must be greater than 1
				if setting == "branches":
					if convertedInput < 2:
						print("Branches must be at least 2!")
						return
				elif setting == "max_fps":
					if convertedInput < 1:
						print("Max FPS must be at least 1!")
						return
				elif setting == "decline_rate":
					if convertedInput <= 0:
						print("Decline rate must be greater than 0!")
						return

				SETTINGS[setting] = convertedInput
				changedSetting = True
				break
		if not changedSetting:
			radius = 0
			try:
				# Clamp the input to the screen size
				radius = min(abs(int(input)), max(turtle.screensize()[0], turtle.screensize()[1]))
				spawnBall(radius)
			except ValueError:
				print("Invalid ball radius or setting name!")
				return
	# Print useful information
	print(f"Total Recursion Count: {totalCount:,}    | FPS: {fps:.3f}")

keyboardThread = KeyboardThread(handleInput)

# Main loop
while True:
	# Check if loop is running too early according to set max FPS
	frameInterval = 1 / SETTINGS["max_fps"]
	currentFrameTime = time.perf_counter()
	if currentFrameTime < lastFrameTime + frameInterval:
		continue

	t.clear()
	t.width(SETTINGS["width"])
	# Loop through each ball in the list and draw it
	for ball in balls:
		totalCount += ball.draw(t)
		ballPos = ball.getPos()
		ballRadius = ball.getTotalLength()
		ballVector = ball.getVector()

		# Check if the balls are outside of the screen boundaries and apply an opposing vector if it is
		if ballPos[0] + ballRadius >= turtle.window_width() / 2:
			ball.setVector((-abs(ballVector[0]), ballVector[1], ballVector[2]))
		elif ballPos[0] - ballRadius <= turtle.window_width() / -2:
			ball.setVector((abs(ballVector[0]), ballVector[1], ballVector[2]))
		if ballPos[1] + ballRadius >= turtle.window_height() / 2:
			ball.setVector((ballVector[0], -abs(ballVector[1]), ballVector[2]))
		elif ballPos[1] - ballRadius <= turtle.window_height() / -2:
			ball.setVector((ballVector[0], abs(ballVector[1]), ballVector[2]))
	
	# Automatic updating is turned off by setting tracer to 0
	# Must update the drawing after each frame
	turtle.update()
	fps = 1 / (currentFrameTime - lastFrameTime)
	lastFrameTime = currentFrameTime