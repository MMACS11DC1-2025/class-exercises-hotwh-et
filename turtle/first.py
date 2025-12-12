import turtle
import random
t = turtle.Turtle()

t.speed(0)


while True:
	minWidth = min(turtle.window_width(), turtle.window_height())

	t.penup()
	t.goto(0, 0)
	t.pendown()
	colour = (random.random(), random.random(), random.random())
	t.color(colour)

	for i in range(2):
		t.left(random.randrange(-180, 180))
		t.forward(random.randint(0, round(minWidth / 2)))

	t.penup()
	radius = random.randrange(0, 100)
	t.forward(radius)
	t.left(90)
	t.pendown()
	t.begin_fill()
	t.circle(radius)
	t.end_fill()


turtle.done()