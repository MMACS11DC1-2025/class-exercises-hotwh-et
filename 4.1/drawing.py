"""
Make An Interactive Drawing or Animation 
Explore the turtle drawing package to create an interactive drawing.
It should use a while loop.
Your program should also include at least one function you’ve made yourself 
"""
import random
import threading
import turtle
import re

global speed
speed = 1

t = turtle.Turtle()

t.speed(0)
turtle.delay(0)
t.hideturtle()
turtle.tracer(0)

turtle.Screen().bgcolor("red")

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name, daemon=True)
        self.start()

    def run(self):
        while True:
            self.input_cbk(input())

def random_colour():
	return (random.random(), random.random(), random.random())
	# return (1,1,1)

class Ball:
	def __init__(self, pos, radius, colour=None):
		self.pos = pos
		self.radius = radius
		self.vector = [0.0, 0.0]
		self.colour = colour if colour is not None else random_colour()

	def draw(self, t):
		self.pos[0] += self.vector[0]
		self.pos[1] += self.vector[1]
		t.penup()
		t.goto((self.pos[0] + self.radius, self.pos[1]))
		t.setheading(90)
		t.color(self.colour)
		t.pendown()
		t.begin_fill()
		t.circle(self.radius)
		t.end_fill()
	
	def setVector(self, vector):
		self.vector = vector
	
	def getPos(self):
		return self.pos
	
	def getRadius(self):
		return self.radius
	
	def getVector(self):
		return self.vector

balls = []

def spawnBall(radius, pos=None, vector=None):
	global speed
	if not pos:
		pos = [0, 0]
	if not vector:
		vector = [random.randrange(-1000, 1000)/1e3 * speed, random.randrange(-1000, 1000)/1e3 * speed]
	ball = Ball(pos, radius)
	ball.setVector(vector)
	balls.append(ball)

def handleInput(input):
	if input:
		if input.lower().startswith("speed "):
			global speed
			speed = int(re.sub("[^\\d]", "", input))
		else:
			radius = 0
			try:
				radius = min(abs(int(input)), max(turtle.screensize()[0], turtle.screensize()[1]))
			except ValueError:
				return
			spawnBall(radius)

keyboardThread = KeyboardThread(handleInput)
while True:
	# spawnBall(5, [random.randrange(round(turtle.window_width() / -2), round(turtle.window_width() / 2)), random.randrange(round(turtle.window_height() / -2), round(turtle.window_height() / 2))])
	t.clear()
	for ball in balls:
		ball.draw(t)
		ballPos = ball.getPos()
		ballRadius = ball.getRadius()
		ballVector = ball.getVector()

		if ballPos[0] + ballRadius >= turtle.window_width() / 2:
			ball.setVector((-abs(ballVector[0]), ballVector[1]))
		elif ballPos[0] - ballRadius <= turtle.window_width() / -2:
			ball.setVector((abs(ballVector[0]), ballVector[1]))
		if ballPos[1] + ballRadius >= turtle.window_height() / 2:
			ball.setVector((ballVector[0], -abs(ballVector[1])))
		elif ballPos[1] - ballRadius <= turtle.window_height() / -2:
			ball.setVector((ballVector[0], abs(ballVector[1])))
	turtle.update()