from PIL import Image
import matplotlib.pyplot as plt

colours = {
	"red": (255, 0, 0),
	"green": (0, 255, 0),
	"blue": (0, 0, 255),
	"white": (255, 255, 255),
	"black": (0, 0, 0),
	"yellow": (255, 255, 0),
	"magenta": (255, 0, 255),
}

def chroma_key(originalImage, targetColour):
	newImage = originalImage.copy()
	tolerance = 100

	for x in range(newImage.width):
		for y in range(newImage.height):
			pixel = newImage.getpixel((x, y))
			r = pixel[0]
			g = pixel[1]
			b = pixel[2]
			if (colours[targetColour][0] - tolerance <= r <= colours[targetColour][0] + tolerance
					and colours[targetColour][1] - tolerance <= g <= colours[targetColour][1] + tolerance
					and colours[targetColour][2] - tolerance <= b <= colours[targetColour][2] + tolerance):
				newImage.putpixel((x, y), (0, 0, 0, 0))
			elif check_adjacent_pixels(originalImage, targetColour, x, y, tolerance, int(tolerance*3)):
				newImage.putpixel((x, y), (0, 0, 0, 0))

	return newImage

def check_adjacent_pixels(image, targetColour, x, y, originalTolerance, tolerance=100):
	pixels_to_check = [
		(x - 1, y - 1),
		(x - 1, y),
		(x - 1, y + 1),
		(x, y - 1),
		(x, y + 1),
		(x + 1, y - 1),
		(x - 1, y),
		(x - 1, y + 1),
	]

	pixel = image.getpixel((x, y))
	r = pixel[0]
	g = pixel[1]
	b = pixel[2]

	if (colours[targetColour][0] - tolerance <= r <= colours[targetColour][0] + tolerance
			and colours[targetColour][1] - tolerance <= g <= colours[targetColour][1] + tolerance
			and colours[targetColour][2] - tolerance <= b <= colours[targetColour][2] + tolerance):		
		for (x, y) in pixels_to_check:
			if x < 0 or y < 0 or x >= image.width or y >= image.height:
				continue
			pixel = image.getpixel((x, y))
			r = pixel[0]
			g = pixel[1]
			b = pixel[2]
			if (colours[targetColour][0] - originalTolerance <= r <= colours[targetColour][0] + originalTolerance
					and colours[targetColour][1] - originalTolerance <= g <= colours[targetColour][1] + originalTolerance
					and colours[targetColour][2] - originalTolerance <= b <= colours[targetColour][2] + originalTolerance):
				return True
	return False


image_green = Image.open("./5.1/kid-green.jpg")
image_beach = Image.open("./5.1/beach_real.jpg")

chosenImage = image_green

chosenImage = chosenImage.convert("RGBA")
transparentImage = chroma_key(chosenImage, "green")

layeredImage = image_beach.convert("RGBA")
layeredImage.alpha_composite(transparentImage)

plt.imshow(layeredImage)
plt.show()