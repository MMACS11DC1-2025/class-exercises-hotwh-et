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

		popped = sorted_comparing_list.pop(current_minimum_index)
		sorted_comparing_list.insert(i, popped)
		sorted_output_list.insert(i, sorted_output_list.pop(current_minimum_index))

	return sorted_output_list


if __name__ == "__main__":
	sort_input = []
	for i in range(10):
		sort_input.append(random.randint(0, 100))
	print("Testing selection sort")
	print(f"Giving input: {sort_input}")
	sort_output = selection_sort(sort_input)
	print(f"Returned output: {sort_output}")