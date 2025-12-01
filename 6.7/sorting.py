import random


def selection_sort(comparing_list, output_list=None):
	if output_list == None:
		output_list = comparing_list

	current_index = 0
	for i in range(len(comparing_list) - 1):
		current_minimum = comparing_list[i]
		current_minimum_index = i
		for j in range(len(comparing_list) - 1 - current_index):
			if comparing_list[j + current_index] < current_minimum:
				current_minimum = comparing_list[j + current_index]
				current_minimum_index = j + current_index

		comparing_list.insert(0, comparing_list.pop(current_minimum_index))
		output_list.insert(0, output_list.pop(current_minimum_index))
	
	return output_list


if __name__ == "__main__":
	sort_input = []
	for i in range(10):
		sort_input.append(random.randint(0, 100))
	print("Testing selection sort")
	print(f"Giving input: {sort_input}")
	sort_output = selection_sort(sort_input)
	print(f"Returned output: {sort_output}")