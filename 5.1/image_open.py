from PIL import Image

colours = {
	"red": (255, 0, 0),
	"green": (0, 255, 0),
	"blue": (0, 0, 255),
	"white": (255, 255, 255),
	"black": (0, 0, 0),
	"yellow": (255, 255, 0),
	"magenta": (255, 0, 255),
}

def colour(r, g, b):
	for colour, values in colours.items():
		if (values[0] - 25 <= r <= values[0] + 25
				and values[1] - 25 <= g <= values[1] + 25
				and values[2] - 25 <= b <= values[2] + 25):
			return colour
	
	return "Unknown"

image_green = Image.open("./5.1/kid-green.jpg")
image_beach = Image.open("./5.1/beach.jpg")

chosenImage = image_beach
chosenPixels = chosenImage.load()

pixel = chosenPixels[0,225]

counter = {}

for x in range(chosenImage.width):
	for y in range(chosenImage.height):
		pixel = chosenPixels[x, y]
		result = colour(pixel[0], pixel[1], pixel[2])
		counter[result] = counter.get(result, 0) + 1

print(counter)