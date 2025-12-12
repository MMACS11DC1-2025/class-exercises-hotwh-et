import turtle

global iterations 
iterations = 0
def draw_tree(level, branch_length):
	global iterations
	iterations += 1
	if level > 0:
		turtle.forward(branch_length)

		turtle.left(40)
		draw_tree(level-1, branch_length / 1.61)

		turtle.right(80)

		draw_tree(level-1, branch_length / 1.61)

		turtle.left(40)
		turtle.back(branch_length)

	else:
		turtle.color("green")
		turtle.stamp()
		turtle.color("brown")

turtle.speed(0)
turtle.delay(0)
turtle.penup()
turtle.goto(0, -380)
turtle.left(90)
turtle.pendown()

turtle.color("brown")
turtle.width(3)
turtle.shape("triangle")

turtle.tracer(0)
draw_tree(15, 300)
turtle.update()
print(iterations)
turtle.done()