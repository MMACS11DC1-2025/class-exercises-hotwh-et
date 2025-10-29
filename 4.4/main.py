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

t.speed(0)
turtle.delay(0)
t.hideturtle()
turtle.tracer(0)

class KeyboardThread(threading.Thread):
    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input("Input: "))

def random_colour():
	return (random.random(), random.random(), random.random())
	# return (1,1,1)

class Ball:
	def __init__(self, pos, radius, colour=None):
		self.pos = pos
		self.radius = radius
		self.vector = [0.0, 0.0, 0.0]
		self.colour = colour if colour is not None else random_colour()
		self.totalLength = radius

	def draw(self, t):
		count = 0
		self.pos[0] += self.vector[0] * SETTINGS["speed"]
		self.pos[1] += self.vector[1] * SETTINGS["speed"]
		self.pos[2] += self.vector[2] * SETTINGS["speed"]
		t.penup()
		t.color(self.colour)
		t.goto((self.pos[0], self.pos[1]))
		for i in range(int(SETTINGS["branches"])):
			value = self.drawBranch(i * (360 / SETTINGS["branches"]) + self.pos[2], self.radius)
			count += value[0]
			self.totalLength = value[1]
		return count
	
	def drawBranch(self, direction, length):
		count = 0
		totalLength = 0
		if (length <= SETTINGS["min_branch_length"]):
			return (1, 0)
		t.setheading(direction)
		t.pendown()
		t.forward(length)
		
		angleDifference = SETTINGS["branch_angle_range"] / (SETTINGS["branches"] - 1)
		for i in range(int(SETTINGS["branches"])):
			value = self.drawBranch(direction - (SETTINGS["branch_angle_range"] / 2) + (i*angleDifference), length/SETTINGS["decline_rate"])
			count += value[0]
			totalLength = value[1]

		t.penup()
		t.setheading(direction)
		t.backward(length)

		return (count, totalLength + length)

	
	def setVector(self, vector):
		self.vector = vector
	
	def getPos(self):
		return self.pos
	
	def getRadius(self):
		return self.radius
	
	def getVector(self):
		return self.vector
	
	def getTotalLength(self):
		return self.totalLength

balls = []

def spawnBall(radius, pos=None, vector=None):
	if not pos:
		pos = [0, 0, 0]
	if not vector:
		vector = [random.randrange(-1000, 1000)/1e2, random.randrange(-1000, 1000)/1e2, random.randrange(-10, 10)]
	ball = Ball(pos, radius)
	ball.setVector(vector)
	balls.append(ball)

def handleInput(input):
	if input:
		changedSetting = False
		for setting in SETTINGS.keys():
			if input.lower().startswith(setting.lower().replace("_", " ")):
				SETTINGS[setting] = float(re.sub("[^\\d.]", "", input))
				changedSetting = True
				break
		if not changedSetting:
			radius = 0
			try:
				radius = min(abs(int(input)), max(turtle.screensize()[0], turtle.screensize()[1]))
				spawnBall(radius)
			except ValueError:
				pass
	print(f"Total Recursion Count: {totalCount:,}    | FPS: {fps:.3f}")

keyboardThread = KeyboardThread(handleInput)
while True:
	frameInterval = 1 / SETTINGS["max_fps"]
	if time.perf_counter() < lastFrameTime + frameInterval:
		continue
	t.clear()
	t.width(SETTINGS["width"])
	for ball in balls:
		totalCount += ball.draw(t)
		ballPos = ball.getPos()
		ballRadius = ball.getTotalLength()
		ballVector = ball.getVector()

		if ballPos[0] + ballRadius >= turtle.window_width() / 2:
			ball.setVector((-abs(ballVector[0]), ballVector[1], ballVector[2]))
		elif ballPos[0] - ballRadius <= turtle.window_width() / -2:
			ball.setVector((abs(ballVector[0]), ballVector[1], ballVector[2]))
		if ballPos[1] + ballRadius >= turtle.window_height() / 2:
			ball.setVector((ballVector[0], -abs(ballVector[1]), ballVector[2]))
		elif ballPos[1] - ballRadius <= turtle.window_height() / -2:
			ball.setVector((ballVector[0], abs(ballVector[1]), ballVector[2]))
	turtle.update()
	fps = 1 / (time.perf_counter() - lastFrameTime)
	lastFrameTime = time.perf_counter()