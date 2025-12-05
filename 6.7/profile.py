from PIL import Image
import time
count = 20

img = Image.open("./6.7/images/stocks.png")
print(f"Starting direct image getpixel")
start = time.perf_counter()
for i in range(count):
	for x in range(img.width):
		for y in range(img.height):
			img.getpixel((x, y))

end = time.perf_counter()
print(f"Finished direct image getpixel in {end - start}s")

load = img.load()
print(f"Starting loaded pixel access")
start = time.perf_counter()
for i in range(count):
	for x in range(img.width):
		for y in range(img.height):
			load[x, y]

end = time.perf_counter()
print(f"Finished loaded pixel access in {end - start}s")