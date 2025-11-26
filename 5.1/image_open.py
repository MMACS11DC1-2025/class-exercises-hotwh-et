from PIL import Image
import time

startTime = time.perf_counter()

colours = {
	"yellow": (255, 255, 0),
	"red": (255, 0, 0),
	"green": (0, 255, 0),
	"blue": (0, 0, 255),
	"white": (255, 255, 255),
	"black": (0, 0, 0),
	"magenta": (255, 0, 255),
}

def colour(r, g, b):
	tolerance = 105
	for colour, values in colours.items():
		if (values[0] - tolerance <= r <= values[0] + tolerance
				and values[1] - tolerance <= g <= values[1] + tolerance
				and values[2] - tolerance <= b <= values[2] + tolerance):
			return colour
	
	return "Unknown"

image_green = Image.open("./5.1/kid-green.jpg")
image_beach = Image.open("./5.1/beach.jpg")
image_jelly_beans = Image.open("./5.1/jelly_beans.jpg")

chosenImage = image_jelly_beans
# chosenPixels = chosenImage.load()

counter = {}

for x in range(chosenImage.width):
	for y in range(chosenImage.height):
		pixel = chosenImage.getpixel((x, y))
		result = colour(pixel[0], pixel[1], pixel[2])
		counter[result] = counter.get(result, 0) + 1
		if (result == "yellow"):
			chosenImage.putpixel((x, y), (255, 255, 255))

endTime = time.perf_counter()

print(counter)
print(f"Finished in {endTime - startTime:5f}s")
chosenImage.show()
while True:
	pass