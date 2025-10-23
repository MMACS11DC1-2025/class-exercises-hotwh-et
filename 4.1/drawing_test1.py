"""
Make An Interactive Drawing or Animation 
Explore the turtle drawing package to create an interactive drawing.
It should use a while loop.
Your program should also include at least one function you’ve made yourself 
"""
import turtle

global drawing
drawing = True
speed = 50

def draw(t, x, y):
	t.goto(x, y)

def draw_vertical(t, y):
	draw(t, t.pos()[0], y)

def draw_horizontal(t, x):
	draw(t, x, t.pos()[1])

def toggle_drawing(t):
	global drawing
	drawing = not drawing
	if drawing:
		t.pendown()
	else:
		t.penup()

t = turtle.Turtle()
t.speed(0)
t.hideturtle()

# turtle.getcanvas().bind("<Motion>", partial(motion, t))
# turtle.getcanvas().bind("<ButtonPress>", partial(set_dragging, True))
# turtle.getcanvas().bind("<ButtonRelease>", partial(set_dragging, False))

turtle.onkey(lambda *_args: (draw_vertical(t, t.pos()[1] + speed)), "Up")
turtle.onkey(lambda *_args: (draw_vertical(t, t.pos()[1] - speed)), "Down")
turtle.onkey(lambda *_args: (draw_horizontal(t, t.pos()[0] - speed)), "Left")
turtle.onkey(lambda *_args: (draw_horizontal(t, t.pos()[0] + speed)), "Right")
turtle.onkey(lambda *_args: (toggle_drawing(t)), "space")
turtle.listen()

turtle.done()