import math

def pos_in_circle(circle_centre: tuple[int, int], circle_radius: int, pos: tuple[int, int]):
	x, y = pos
	circle_x, circle_y = circle_centre

	x_squared = (x - circle_x) ** 2
	y_squared = (y - circle_y) ** 2

	if math.sqrt(x_squared + y_squared) < circle_radius:
		return True
	return False

def clamp(num: float, min: float, max: float):
	return min if num < min else max if num > max else num

def scale(num: float, min_old: float, max_old: float, min_new: float, max_new: float):
	return min_new + ((num - min_old) / (max_old - min_old)) * (max_new - min_new)