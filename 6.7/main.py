import time
from PIL import Image, ImageDraw
import os
import img_functions
import search
import sorting

if not os.path.exists("./6.7/images"):
	print("You must have images in the path: \"./6.7/images\"")
	exit()

files = os.listdir("./6.7/images")
if not os.path.exists("./6.7/output"):
	os.mkdir("./6.7/output")

# This class is used to manage the storage of the image labels
# It stores the labels in a list of lists, representing a matrix of labels
# with a default value of None. Labels are numerical values representing their group id
class ImageLabelMatrix:
	def __init__(self, image: Image.Image):
		self.matrix = []
		self.group_pixels = {}
		for x in range(image.width):
			self.matrix.append([])
			self.matrix[x] = [None for y in range(image.height)]
	
	def getPixel(self, x, y):
		return self.matrix[x][y]

	def setPixel(self, x, y, value):
		self.matrix[x][y] = value
		self.group_pixels[value] = self.group_pixels.get(value, [])
		self.group_pixels[value].append((x, y))
	
	def getGroupPixels(self, group):
		return self.group_pixels[group]

# Utility function to check if colour is different from background
def is_foreground(colour, background=0, threshold=25):
	return abs(colour - background) >= threshold

total_time = 0
total_pixels = 0
image_scores_list = []

# These dicts store the images to be shown on request by the user
# Format = {filename: image}
original_images = {}
isolated_chart_images = {}

for file in files:
	start_time = time.perf_counter()
	print(f"Started analyzing {file}")

	# This is primarily designed to prevent analyzing directories
	if not os.path.isfile(os.path.join("./6.7/images", file)):
		print("This is not a file. Skipping")
		print("-"*10)
		continue
	original_image = Image.open(f"./6.7/images/{file}")
	original_images[file] = original_image
	pixels = original_image.width * original_image.height
	print(f"Contains {pixels:,} pixels")
	total_pixels += pixels

	greyscale_image = img_functions.greyscale(original_image.convert("RGB"))
	ccl_input_image = greyscale_image.copy()
	ccl_input_image_loaded = ccl_input_image.load()

	nextLabel = 1
	labelMatrix = ImageLabelMatrix(ccl_input_image)

	average_colour_sum = 0
	min_colour = float("inf")
	max_colour = float("-inf")

	# Get average colour which is used to detect foreground pixels
	# Also get colour range so colour tolerance is based on colour variance
	for x in range(ccl_input_image.width):
		for y in range(ccl_input_image.height):
			current_colour = ccl_input_image_loaded[x, y]
			average_colour_sum += current_colour
			min_colour = min(min_colour, current_colour)
			max_colour = max(max_colour, current_colour)

	average_colour = average_colour_sum / (ccl_input_image.width * ccl_input_image.height)
	colour_range = max_colour - min_colour
	foreground_threshold = colour_range * 0.2

	currentLabel = 0
	label_counts = {}

	# Loop over every pixel and use CCL algorithm to label pixels
	# Excludes the outline of the image, as it often contains a solid colour border which breaks graph detection
	for x in range(2, ccl_input_image.width - 2):
		for y in range(2, ccl_input_image.height - 2):
			if (is_foreground(ccl_input_image_loaded[x, y], average_colour, foreground_threshold)
	   				and labelMatrix.getPixel(x, y) == None):
				pixelQueue = []

				labelMatrix.setPixel(x, y, currentLabel)
				label_counts[currentLabel] = label_counts.get(currentLabel, 0) + 1
				pixelQueue.append((x, y))

				while len(pixelQueue) > 0:
					targetPixel = pixelQueue.pop(0)
					
					# Check neighbour pixels using start and stop parameters
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

		
				currentLabel += 1

	sorted_label_counts = list(sorting.selection_sort_tuples(list(label_counts.items()), 1))[::-1]

	# After groups have been identified, determine which is the chart's line
	group_widths = []
	group_heights = []
	for (group, _) in sorted_label_counts[:3]:
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

	# sorted_group_widths_group = reversed(sorting.selection_sort(list(map(lambda group_width : group_width[1], group_widths)), list(map(lambda group_width : group_width[0], group_widths))))
	sorted_group_widths_group = [widths[0] for widths in sorting.selection_sort_tuples(group_widths, 1)]
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
	
	# Target group refers to the line
	target_group = None
	max_height_group = None
	max_height = float("-inf")
	for i in range(len(filtered_groups)):
		group = filtered_groups[i][0]

		for (group_compare, height) in group_heights:
			if (group == group_compare):
				filtered_groups[i] = (group, (filtered_groups[i][1][0], height))

				if height > max_height:
					max_height_group = group
					max_height = height
				break
		
	target_group = max_height_group

	labeled_image = Image.new("RGB", (ccl_input_image.width, ccl_input_image.height))
	labeled_image_draw = ImageDraw.Draw(labeled_image)
	target_starting_pixels = []
	target_ending_pixels = []
	for pixel in labelMatrix.getGroupPixels(target_group):
		if pixel[0] < (target_starting_pixels[0][0] if len(target_starting_pixels) > 0 else float("inf")):
			target_starting_pixels.clear()
			target_starting_pixels.append(pixel)
		elif pixel[0] == target_starting_pixels[0][0]:
			target_starting_pixels.append(pixel)

		if pixel[0] > (target_ending_pixels[0][0] if len(target_ending_pixels) > 0 else float("-inf")):
			target_ending_pixels.clear()
			target_ending_pixels.append(pixel)
		elif pixel[0] == target_ending_pixels[0][0]:
			target_ending_pixels.append(pixel)

		# Create an image to show the target group
		labeled_image_draw.point(pixel, (255, 255, 255))
	
	for pixel in target_starting_pixels:
		labeled_image_draw.point(pixel, (0, 255, 0))
	for pixel in target_ending_pixels:
		labeled_image_draw.point(pixel, (255, 0, 0))
	
	starting_pixels_heights = list(map(lambda pixel : pixel[1], target_starting_pixels))
	ending_pixels_heights = list(map(lambda pixel : pixel[1], target_ending_pixels))
	average_start = ccl_input_image.height - (sum(starting_pixels_heights) / len(target_starting_pixels))
	average_end = ccl_input_image.height - (sum(ending_pixels_heights) / len(target_ending_pixels))
	change_fraction = (average_end / average_start) - 1
	
	# print(f"Start: {average_start}")
	# print(f"End: {average_end}")
	print(f"Percent change: {change_fraction * 100}%")

	image_scores_list.append((file, change_fraction))

	output_image = labeled_image.copy()
	output_image.save(f"./6.7/output/{file}")
	isolated_chart_images[file] = output_image

	end_time = time.perf_counter()
	total_time += end_time - start_time
	print(f"Finished in {end_time - start_time}s")
	print("-"*10)

print()
print(f"Finished image analysis in {total_time:,}s for {total_pixels:,} pixels")
print(f"Average pixels per second: {total_pixels / total_time:,.3f}")
print()

start_time = time.perf_counter()
print("Sorting scores...")
image_filenames = list(map(lambda score : score[0], image_scores_list))
image_scores = list(map(lambda score : score[1], image_scores_list))
image_scores_sorted = list(zip(
	sorting.selection_sort(image_scores, image_filenames),
	sorting.selection_sort(image_scores)
))[::-1]
end_time = time.perf_counter()
total_time += end_time - start_time
print(f"Finished sorting in {end_time - start_time}s")

print()
print("="*50)
print()
print("Final scores (only top 5 are shown)")
print("-"*10)
print(f"{"Filename":<30s}{"Score":>8}")
print()
for filename, score in image_scores_sorted[:5]:
	print(f"{filename:<30s}{" " if score >= 0 else ""}{score * 100:.3f}%")
print()
print("="*50)

print(f"Finished all work in {total_time}s")

search_image_filenames = list(map(lambda score_tuple : score_tuple[0], image_scores_sorted[::-1]))
search_image_scores = list(map(lambda score_tuple : round(score_tuple[1] * 100, 3), image_scores_sorted[::-1]))
while True:
	print()
	response = input("For which score would you like to see the graph? (enter \"exit\" to exit) ").strip().strip("%").lower()
	if response == "exit":
		break

	response_num = None
	try:
		response_num = float(response)
	except ValueError:
		print("That is not a number!")
		continue

	if response_num is None:
		continue

	searched_image_index = search.binary_search(search_image_scores, response_num)
	if searched_image_index is None or searched_image_index > len(image_scores_list):
		print("Could not find an image with that score!")
		continue

	filename = search_image_filenames[searched_image_index]

	print("-"*10)
	print(f"This score is for {filename}")
	print("Which image would you like to see?")
	print('Type "1" for the original image, "2" for the isolated chart, or anything else to cancel')
	response = input("Input: ").strip().lower()

	match response:
		case "1":
			original_images[filename].show()
		case "2":
			isolated_chart_images[filename].show()
		case _:
			continue
	
	print("Opening file...")