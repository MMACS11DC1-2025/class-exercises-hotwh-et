import time
from PIL import Image
import os

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
		self.group_pixels = {}
		for x in range(image.width):
			self.matrix.append([])
			for y in range(image.height):
				self.matrix[x].append(None)
		# self.matrix = [[None] * image.height] * image.width
	
	def getPixel(self, x, y):
		return self.matrix[x][y]

	def setPixel(self, x, y, value):
		self.matrix[x][y] = value
		self.group_pixels[value] = self.group_pixels.get(value, [])
		self.group_pixels[value].append((x, y))
	
	def getGroupPixels(self, group):
		return self.group_pixels[group]


def is_foreground(colour, background=0, threshold=25):
	return abs(colour - background) >= threshold

total_time = 0
total_pixels = 0
for file in files:
	start_time = time.perf_counter()
	print(f"Started analyzing {file}")

	original_image = Image.open(f"./6.7/images/{file}")
	pixels = original_image.width * original_image.height
	print(f"Contains {pixels:,} pixels")
	total_pixels += pixels

	greyscale_image = img_functions.greyscale(original_image)
	ccl_input_image = greyscale_image.copy()

	nextLabel = 1
	labelMatrix = ImageLabelMatrix(ccl_input_image)

	pixelQueue = []
	currentLabel = 0

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
	labeled_image = Image.new("RGB", (ccl_input_image.width, ccl_input_image.height))

	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			if (is_foreground(ccl_input_image.getpixel((x, y)), average_colour, foreground_threshold)
	   			and labelMatrix.getPixel(x, y) == None):

				labelMatrix.setPixel(x, y, currentLabel)
				label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
				pixelQueue.append((x, y))

				labeled_image.putpixel((x, y), component_colours[currentLabel % len(component_colours)])

				while len(pixelQueue) > 0:
					targetPixel = pixelQueue.pop(0)
					
					neighbourPixels = []
					for i in range(-1, 2):
						for j in range(-1, 2):
							currentX = targetPixel[0] + i
							currentY = targetPixel[1] + j
							if (0 <= currentX < ccl_input_image.width
								and 0 <= currentY < ccl_input_image.height):
								if (is_foreground(ccl_input_image.getpixel((currentX, currentY)), average_colour, foreground_threshold)
									and labelMatrix.getPixel(currentX, currentY) == None):
									labelMatrix.setPixel(currentX, currentY, currentLabel)
									label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
									pixelQueue.append((currentX, currentY))

									labeled_image.putpixel((currentX, currentY), component_colours[currentLabel % len(component_colours)])

				currentLabel += 1
		

	sorted_label_counts = list(zip(sorting.selection_sort(list(label_counts.values()), list(label_counts.keys())), sorting.selection_sort(list(label_counts.values()))))
	sorted_label_counts.reverse()
	# print(sorted_label_counts)

	group_width_dict = []
	for (group, _) in sorted_label_counts:
		group_pixels = labelMatrix.getGroupPixels(group)
		# print(f"Group {group}: {group_pixels}")
		min_x = float("inf")
		max_x = float("-inf")
		for (x, _) in group_pixels:
			min_x = min(min_x, x)
			max_x = max(max_x, x)
		group_width_dict.append((group, max_x - min_x))

	print(group_width_dict)
	output_image = labeled_image.copy()
	output_image.save(f"./6.7/output/{file}")

	end_time = time.perf_counter()
	total_time += end_time - start_time
	print(f"Finished in {end_time - start_time}s")

print(f"Finished image analysis in {total_time:,}s for {total_pixels:,} pixels")