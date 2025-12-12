import random
import time

# Assumes the list is sorted
# Will not work as intended if not
# Returns -1 if target could not be found
def binary_search(search_target, target):
	min_index = 0
	max_index = len(search_target) - 1
	while min_index <= max_index:
		current_index = int((max_index + min_index) / 2)
		if search_target[current_index] == target:
			return current_index
		elif search_target[current_index] < target:
			min_index = current_index + 1
		elif search_target[current_index] > target:
			max_index = current_index - 1
	return None

if __name__ == "__main__":
	search_input = []
	last_num = 0
	for i in range(10):
		increment = random.randint(0, 10)
		search_input.append(last_num + increment)
		last_num += increment
	target = random.choice(search_input)
	print("Testing binary search")
	print(f"Giving input: {search_input}\tLooking for: {target}")
	start_time = time.perf_counter()
	search_output = binary_search(search_input, target)
	end_time = time.perf_counter()
	print(f"Returned output: {search_output}")
	print(f"Verified to be {"correct" if search_input[search_output] == target else "incorrect"}")
	print(f"Finished in {end_time - start_time:f}s")