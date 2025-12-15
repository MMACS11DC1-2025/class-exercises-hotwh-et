import random

def selection_sort(comparing_list, output_list=None):
	if output_list == None:
		output_list = comparing_list

	sorted_comparing_list = comparing_list.copy()
	sorted_output_list = output_list.copy()
	for i in range(len(sorted_comparing_list) - 1):
		current_minimum = sorted_comparing_list[i]
		current_minimum_index = i
		for j in range(len(sorted_comparing_list) - 1 - i):
			if sorted_comparing_list[j + i + 1] < current_minimum:
				current_minimum = sorted_comparing_list[j + i + 1]
				current_minimum_index = j + i + 1

		sorted_comparing_list[i], sorted_comparing_list[current_minimum_index] = sorted_comparing_list[current_minimum_index], sorted_comparing_list[i]
		sorted_output_list[i], sorted_output_list[current_minimum_index] = sorted_output_list[current_minimum_index], sorted_output_list[i]

	return sorted_output_list

def selection_sort_tuples(comparing_list, comparing_tuple_index):
	sorted_comparing_list = comparing_list.copy()

	for i in range(len(sorted_comparing_list) - 1):
		current_minimum = sorted_comparing_list[i][comparing_tuple_index]
		current_minimum_index = i
		for j in range(len(sorted_comparing_list) - 1 - i):
			if sorted_comparing_list[j + i + 1][comparing_tuple_index] < current_minimum:
				current_minimum = sorted_comparing_list[j + i + 1][comparing_tuple_index]
				current_minimum_index = j + i + 1

		sorted_comparing_list[i], sorted_comparing_list[current_minimum_index] = sorted_comparing_list[current_minimum_index], sorted_comparing_list[i]

	return sorted_comparing_list


if __name__ == "__main__":
	sort_input = []
	for i in range(10):
		sort_input.append(random.randint(0, 100))
	print("Testing selection sort")
	print(f"Giving input: {sort_input}")
	sort_output = selection_sort(sort_input)
	print(f"Returned output: {sort_output}")
	success = True
	last_item = 0
	for item in sort_output:
		if item < last_item:
			success = False
			break
		last_item = item
	if success:
		print("Test passed")
	else:
		print("Test failed")

	sort_input = []
	for i in range(10):
		sort_input.append((random.randint(0, 100), random.randint(0, 100)))
	print("Testing selection sort with tuples")
	print(f"Giving input: {sort_input}")
	sort_output = selection_sort_tuples(sort_input, 0)
	print(f"Returned output: {sort_output}")
	success = True
	last_item = (0, 0)
	for item in sort_output:
		if item[0] < last_item[0]:
			success = False
			break
		last_item = item
	if success:
		print("Test passed")
	else:
		print("Test failed")
