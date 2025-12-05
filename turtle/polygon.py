import math
import time
import turtle

t = turtle.Turtle()

t.speed(10)

radius = 50

while True:
	sides = int(input("Number of sides: "))
	angle = 180 - ((sides - 2) * 180) / sides

	sideLength = (2*math.pi*radius) / sides

	t.penup()
	t.goto(0, 0)
	t.setheading(90)
	t.forward(radius)
	t.left(angle)
	t.pendown()
	for i in range(sides):
		t.forward(sideLength)
		t.left(angle)
		t.forward(sideLength)