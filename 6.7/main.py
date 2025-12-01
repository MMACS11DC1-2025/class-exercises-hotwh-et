import time
from PIL import Image, ImageDraw
import os

from cv2 import sort
from numpy import matrix
from pyparsing import col
import img_functions
import sorting

files = os.listdir("./6.7/images")

component_colours = [
	(255, 255, 255),
	(0, 0, 0),
	(255, 0, 0),
	(0, 255, 0),
	(0, 0, 255),
	(255, 255, 0),
	(255, 0, 255),
	(0, 255, 255),
]

class ImageLabelMatrix:
	def __init__(self, image: Image.Image):
		self.matrix = []
		for x in range(image.width):
			self.matrix.append([])
			for y in range(image.height):
				self.matrix[x].append(None)
		# self.matrix = [[None] * image.height] * image.width
	
	def getPixel(self, x, y):
		return self.matrix[x][y]

	def setPixel(self, x, y, value):
		self.matrix[x][y] = value

def is_foreground(colour, background=0, threshold=25):
	return abs(colour - background) >= threshold

for file in files:
	start_time = time.perf_counter()
	print(f"Started analyzing {file}")

	original_image = Image.open(f"./6.7/images/{file}")

	greyscale_image = img_functions.greyscale(original_image)
	ccl_input_image = greyscale_image.copy()

	nextLabel = 1
	labelMatrix = ImageLabelMatrix(ccl_input_image)

	pixelQueue = []
	currentLabel = 0

	# greyscale_image.save("output.png")
	
	average_colour_sum = 0
	min_colour = float("inf")
	max_colour = float("-inf")

	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			current_colour = ccl_input_image.getpixel((x, y))
			average_colour_sum += current_colour
			min_colour = min(min_colour, current_colour)
			max_colour = max(max_colour, current_colour)

	average_colour = average_colour_sum / (ccl_input_image.width * ccl_input_image.height)
	colour_range = max_colour - min_colour
	foreground_threshold = colour_range * 0.2

	label_counts = {}

	# labelMatrix.setPixel(0, 0, currentLabel)
	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			if (is_foreground(ccl_input_image.getpixel((x, y)), average_colour, foreground_threshold)
	   			and labelMatrix.getPixel(x, y) == None):

				labelMatrix.setPixel(x, y, currentLabel)
				label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
				pixelQueue.append((x, y))

				while len(pixelQueue) > 0:
					# print(pixelQueue)
					targetPixel = pixelQueue.pop(0)
					
					neighbourPixels = []
					for i in range(-1, 2):
						for j in range(-1, 2):
							currentX = targetPixel[0] + i
							currentY = targetPixel[1] + j
							# print(f"{currentX},{currentY}")
							if (0 <= currentX < ccl_input_image.width
								and 0 <= currentY < ccl_input_image.height):
								if (is_foreground(ccl_input_image.getpixel((currentX, currentY)), average_colour, foreground_threshold)
									and labelMatrix.getPixel(currentX, currentY) == None):
									# print(f"Added to queue {labelMatrix.getPixel(currentX, currentY)}")
									labelMatrix.setPixel(currentX, currentY, currentLabel)
									label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
									pixelQueue.append((currentX, currentY))

				currentLabel += 1
		
	print(label_counts)
	labeled_image = Image.new("RGB", (ccl_input_image.width, ccl_input_image.height))
	
	for x in range(labeled_image.width):
		for y in range(labeled_image.height):
			# Even though documentation says it is slow, it is has been tested to be 2-3 times faster than ImageDraw
			labeled_image.putpixel((x, y), component_colours[(labelMatrix.getPixel(x, y) or 0) % len(component_colours)])
	
	# output_image = labeled_image.copy()
	output_image = labeled_image.copy()
	output_image.save(f"./6.7/output/{file}")
	greyscale_image.save(f"./6.7/output/gs-{file}")

	end_time = time.perf_counter()
	print(f"Finished in {end_time - start_time}s")
