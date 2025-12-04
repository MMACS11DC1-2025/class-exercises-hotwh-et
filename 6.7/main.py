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
	ccl_input_image_loaded = ccl_input_image.load()

	nextLabel = 1
	labelMatrix = ImageLabelMatrix(ccl_input_image)

	pixelQueue = []
	currentLabel = 0

	average_colour_sum = 0
	min_colour = float("inf")
	max_colour = float("-inf")

	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			current_colour = ccl_input_image_loaded[x, y]
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
			if (is_foreground(ccl_input_image_loaded[x, y], average_colour, foreground_threshold)
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
								if (is_foreground(ccl_input_image_loaded[currentX, currentY], average_colour, foreground_threshold)
									and labelMatrix.getPixel(currentX, currentY) == None):
									labelMatrix.setPixel(currentX, currentY, currentLabel)
									label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
									pixelQueue.append((currentX, currentY))

									labeled_image.putpixel((currentX, currentY), component_colours[currentLabel % len(component_colours)])

				currentLabel += 1
		

	sorted_label_counts = list(zip(sorting.selection_sort(list(label_counts.values()), list(label_counts.keys())), sorting.selection_sort(list(label_counts.values()))))
	sorted_label_counts.reverse()

	# After groups have been identified, determine which is the chart's line
	group_widths = []
	group_heights = []
	for (group, _) in sorted_label_counts[:5]:
		group_pixels = labelMatrix.getGroupPixels(group)
		min_x = float("inf")
		max_x = float("-inf")
		for (x, _) in group_pixels:
			min_x = min(min_x, x)
			max_x = max(max_x, x)
		group_widths.append((group, max_x - min_x))

		min_y = float("inf")
		max_y = float("-inf")
		for (_, y) in group_pixels:
			min_y = min(min_y, y)
			max_y = max(max_y, y)
		group_heights.append((group, max_y - min_y))

	sorted_group_widths_group = reversed(sorting.selection_sort(list(map(lambda group_width : group_width[1], group_widths)), list(map(lambda group_width : group_width[0], group_widths))))
	sorted_group_widths_width = reversed(sorting.selection_sort(list(map(lambda group_width : group_width[1], group_widths))))
	sorted_group_widths = list(zip(sorted_group_widths_group, sorted_group_widths_width))

	filtered_groups = []
	last_width = None
	for (group, width) in sorted_group_widths:
		if (last_width is None 
	  		or width >= last_width / 2):
			filtered_groups.append((group, (width, None)))
			last_width = width
		else:
			break
	
	filtered_group_heights = []
	for i in range(len(filtered_groups)):
		group = filtered_groups[i][0]
		for (group_compare, height) in group_heights:
			if (group == group_compare):
				print(f"Assigned {height} to {group}")
				filtered_groups[i] = (group, (filtered_groups[i][1][0], height))
				break

	print(filtered_groups)
	output_image = labeled_image.copy()
	output_image.save(f"./6.7/output/{file}")

	end_time = time.perf_counter()
	total_time += end_time - start_time
	print(f"Finished in {end_time - start_time}s")

print(f"Finished image analysis in {total_time:,}s for {total_pixels:,} pixels")