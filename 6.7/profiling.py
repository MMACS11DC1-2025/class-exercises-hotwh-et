import random
from PIL import Image, ImageDraw
import sorting
import time

# Used as an alternative to input to prevent needing to enter a value each time when running
# 0 = Direct image getpixel vs. PixelAccess class
# 1 = Direct image setpixel vs. PixelDraw class
# 2 = Selection sort
# 3 = List comprehension vs. map
# 4 = List reversing
# 5 = List move (swap vs pop and insert)
PROFILE_MODE = 6
COUNT = int(1e8)
IMAGE_DIMENSIONS = (1000, 1000)
LIST_LENGTH = int(1e6)

def profile_get_pixel():
	img = Image.new("RGB", IMAGE_DIMENSIONS)

	print(f"Working with total {img.width * img.height * COUNT:,} pixels")
	print("Starting direct image getpixel")
	start = time.perf_counter()
	for i in range(COUNT):
		for x in range(img.width):
			for y in range(img.height):
				img.getpixel((x, y))

	end = time.perf_counter()
	print(f"Finished direct image getpixel in {end - start}s")

	load = img.load()
	print("Starting loaded pixel access")
	start = time.perf_counter()
	for i in range(COUNT):
		for x in range(img.width):
			for y in range(img.height):
				load[x, y]

	end = time.perf_counter()
	print(f"Finished loaded pixel access in {end - start}s")

def profile_set_pixel():
	img = Image.new("RGB", IMAGE_DIMENSIONS)
	img2 = img.copy()

	print(f"Working with total {img.width * img.height * COUNT:,} pixels")
	print("Starting direct image putpixel")
	start = time.perf_counter()
	for i in range(COUNT):
		for x in range(img.width):
			for y in range(img.height):
				img.putpixel((x, y), (255, 255, 255))

	end = time.perf_counter()
	print(f"Finished direct image putpixel in {end - start}s")

	img.show()

	drawing = ImageDraw.Draw(img2)
	print("Starting pixel draw")
	start = time.perf_counter()
	for i in range(COUNT):
		for x in range(img.width):
			for y in range(img.height):
				drawing.point((x, y), (255, 255, 255))

	end = time.perf_counter()
	print(f"Finished pixel draw in {end - start}s")

	img2.show()

	time.sleep(10)

def profile_selection_sort():
	print(f"Working with total {COUNT * LIST_LENGTH} elements")
	print("Starting selection sort")
	start = time.perf_counter()
	for i in range(COUNT):
		sort_input = [random.randint(0, 100) for i in range(LIST_LENGTH)]

		sorting.selection_sort(sort_input)
	
	end = time.perf_counter()
	print(f"Finished selection sort in {end - start}s")

def profile_list_loop():
	list_input = [(i, random.random()) for i in range(LIST_LENGTH)]
	print(f"Created input with {LIST_LENGTH:,} elements")

	print("Starting list comprehension")
	start = time.perf_counter()
	[item[1] for item in list_input]
	end = time.perf_counter()
	print(f"Finished list comprehension in {end - start:f}s")

	print("Starting list map")
	start = time.perf_counter()
	list(map(lambda item : item[1], list_input))
	end = time.perf_counter()
	print(f"Finished list map in {end - start:f}s")

def profile_list_reverse():
	list_input = [i for i in range(LIST_LENGTH)]

	print(f"Created input with {LIST_LENGTH:,} elements")

	print("Starting list [::-1]")
	start = time.perf_counter()
	list_input[::-1]
	end = time.perf_counter()
	print(f"Finished list [::-1] in {end - start:f}s")

	print("Starting list reversed")
	start = time.perf_counter()
	reversed(list_input)
	end = time.perf_counter()
	print(f"Finished list reversed in {end - start:f}s")

	print("Starting list reversed to list")
	start = time.perf_counter()
	list(reversed(list_input))
	end = time.perf_counter()
	print(f"Finished list reversed to list in {end - start:f}s")

	# list_copy = list_input.copy()
	print("Starting list reverse")
	start = time.perf_counter()
	list_input.reverse()
	end = time.perf_counter()
	print(f"Finished list reverse in {end - start:f}s")

def profile_list_move():
	list_input = [i for i in range(LIST_LENGTH)]

	print(f"Created input with {LIST_LENGTH:,} elements")

	print("Starting list pop and insert")
	list_copy = list_input.copy()
	start = time.perf_counter()
	for i in range(COUNT):
		list_copy.insert(0, list_copy.pop())
	end = time.perf_counter()
	print(f"Finished list pop and insert in {end - start:f}s")

	print("Starting list swap")
	list_copy = list_input.copy()
	start = time.perf_counter()
	for i in range(COUNT):
		list_copy[0], list_copy[len(list_copy) - 1] = list_copy[len(list_copy) - 1], list_copy[0]
	end = time.perf_counter()
	print(f"Finished list swap in {end - start:f}s")

def profile_min_max_2():
	num1 = random.random()
	num2 = random.random()
	print("Starting min() function with 2 arguments")

	start = time.perf_counter()
	for i in range(COUNT):
		min(num1, num2)
	end = time.perf_counter()
	print(f"Finished min() function with 2 arguments in {end - start:f}s")

	print("Starting max() function with 2 arguments")

	start = time.perf_counter()
	for i in range(COUNT):
		max(num1, num2)
	end = time.perf_counter()
	print(f"Finished max() function with 2 arguments in {end - start:f}s")

	print("Starting min with ternary")

	start = time.perf_counter()
	for i in range(COUNT):
		num1 if num1 < num2 else num2
	end = time.perf_counter()
	print(f"Finished min with ternary in {end - start:f}s")

	print("Starting max with ternary")

	start = time.perf_counter()
	for i in range(COUNT):
		num1 if num1 > num2 else num2
	end = time.perf_counter()
	print(f"Finished max with ternary in {end - start:f}s")


match PROFILE_MODE:
	case 0:
		profile_get_pixel()
	case 1:
		profile_set_pixel()
	case 2:
		profile_selection_sort()
	case 3:
		profile_list_loop()
	case 4:
		profile_list_reverse()
	case 5:
		profile_list_move()
	case 6:
		profile_min_max_2()
	case _:
		print("Invalid profile mode")