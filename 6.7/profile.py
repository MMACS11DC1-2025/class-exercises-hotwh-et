import random
from PIL import Image, ImageDraw
import sorting
import time

# Used as an alternative to input to prevent needing to enter a value each time when running
# 0 = Direct image getpixel vs. PixelAccess class
# 1 = Direct image setpixel vs. PixelDraw class
# 2 = Selection sort
PROFILE_MODE = 2
COUNT = 2
IMAGE_DIMENSIONS = (1000, 1000)
SORT_LIST_LENGTH = 500

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
	print(f"Working with total {COUNT * SORT_LIST_LENGTH} elements")
	print("Starting selection sort")
	start = time.perf_counter()
	for i in range(COUNT):
		sort_input = [random.randint(0, 100) for i in range(SORT_LIST_LENGTH)]

		sorting.selection_sort(sort_input)
	
	end = time.perf_counter()
	print(f"Finished selection sort in {end - start}s")

match PROFILE_MODE:
	case 0:
		profile_get_pixel()
	case 1:
		profile_set_pixel()
	case 2:
		profile_selection_sort()
	case _:
		print("Invalid profile mode")