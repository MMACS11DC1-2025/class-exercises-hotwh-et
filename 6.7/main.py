import time
from PIL import Image, ImageDraw
import os
import img_functions

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
	matrix = []

	def __init__(self, image: Image.Image):
		self.matrix = [[None] * image.height] * image.width
	
	def getPixel(self, x, y):
		return self.matrix[x][y]

	def setPixel(self, x, y, value):
		self.matrix[x][y] = value

for file in files:
	start_time = time.perf_counter()
	print(f"Started analyzing {file}")

	original_image = Image.open(f"./6.7/images/{file}")

	binarized_image = img_functions.greyscale(original_image)
	ccl_input_image = binarized_image.copy()

	nextLabel: int = 1
	labelMatrix = ImageLabelMatrix(ccl_input_image)

	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			labelMatrix.setPixel(x, y, 0)
	

	labeled_image = Image.new("RGB", (ccl_input_image.width, ccl_input_image.height))
	
	for x in range(labeled_image.width):
		for y in range(labeled_image.height):
			# Even though documentation says it is slow, it is has been tested to be 2-3 times faster than ImageDraw
			labeled_image.putpixel((x, y), component_colours[labelMatrix.getPixel(x, y) or 0])
	
	output_image = labeled_image.copy()
	output_image.save(f"./6.7/output/{file}")

	end_time = time.perf_counter()
	print(f"Finished in {end_time - start_time}s")