import math


def pos_in_circle(circle_centre: tuple[int, int], circle_radius: int, pos: tuple[int, int]):
	x, y = pos
	circle_x, circle_y = circle_centre

	x_squared = (x - circle_x) ** 2
	y_squared = (y - circle_y) ** 2

	if math.sqrt(x_squared + y_squared) < circle_radius:
		return True
	return False