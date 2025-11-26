def is_light(pixel):
	r, g, b = pixel
	average = (r + g + b) / 3
	return average >= 128

assert not is_light((127, 127, 127))
assert not is_light((255, 128, 0))
assert is_light((255, 255, 255))
assert not is_light((0, 0, 0))

print("Tests succeeded")