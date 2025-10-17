"""
Make An Interactive Drawing or Animation 
Explore the turtle drawing package to create an interactive drawing.
It should use a while loop.
Your program should also include at least one function you’ve made yourself 
"""
import math
import random
import turtle

t = turtle.Turtle()

t.speed(10)
turtle.delay(0.05)

global maxRadius
maxRadius = 100

def draw_branch(t, depth=1):
	for i in range(depth):
		t.left(random.randrange(-180, 180))
		t.forward(random.randint(0, round(minWidth / 2 / depth)))

	t.penup()
	global maxRadius
	radius = random.randrange(0, maxRadius)
	t.forward(radius)
	t.left(90)
	t.pendown()
	t.begin_fill()
	t.circle(radius)
	t.end_fill()

while True:
	minWidth = min(turtle.window_width(), turtle.window_height())

	t.penup()
	t.goto(0, 0)
	t.pendown()
	colour = (random.random(), random.random(), random.random())
	t.color(colour)

	depth = 0
	while True:
		try:
			depth = int(input("Depth: "))
		except ValueError:
			continue
		break

	draw_branch(t, depth)