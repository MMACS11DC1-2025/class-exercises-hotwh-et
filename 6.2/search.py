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

file = open("6.2/spotify.csv", encoding="utf-8")
junk = file.readline()

drake_data = []

for line in file:
	items = line.strip().split(",")
	artist = str(items[-1])
	songtitle = str(items[-2])
	danceability = float(items[1])
	
	if artist == "Drake":
		drake_data.append([danceability, songtitle, artist])
	
	drake_data = selection_sort(drake_data)[::-1][:5]

print("Dance score \tSong")
for item in drake_data:
	print(str(item[0]) + "\t\t" + item[1] + " by " + item[2])