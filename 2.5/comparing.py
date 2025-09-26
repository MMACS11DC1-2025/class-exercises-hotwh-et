"""
Create a program that uses comparison operators (< > <= >=).
You must use the class' datafile, 'responses.csv' and analyze it
    to make at least 2 interesting observations.
You may use user input to add interactivity to the program.
You must design your algorithm in English first, then translate it to Python code.
Test as you go! Describe in your comments what steps you took to test your code.
"""
responsesDict = {}
similarities = {}

with open("./2.4/responses.csv", "r") as file:
	headers = file.readline().strip()
	headersList = headers.split(",")
	responses = file.read().strip().split("\n")
	nameIndex = headersList.index("Name")
	for response in responses:
		responseList = response.strip().split(",")
		responsesDict[responseList[nameIndex]] = dict(zip(headersList[nameIndex+1:], responseList[nameIndex+1:]))

person = input("Enter the name of the person to check: ").strip().title()

if not person in responsesDict.keys():
	print("That person is not in the data!")
	exit()

personData = responsesDict[person]


for personCompareName, personCompareData in responsesDict.items():
	if personCompareName == person:
		continue
	similarities[personCompareName] = 0
	for question, personResponse in personData.items():
		if personCompareData[question].strip().lower() == personResponse.strip().lower():
			similarities[personCompareName] += 1

sortedSimilarities = sorted(similarities, key=lambda name: similarities[name], reverse=True)

for i in range(len(similarities)):
	print(f"#{i+1} {sortedSimilarities[i]}: {similarities[sortedSimilarities[i]]}")

print()

for i in range(len(similarities)):
	if similarities[sortedSimilarities[i]] > 5:
		print(f"You answered more than 5 questions the same as {sortedSimilarities[i]}!")
	elif similarities[sortedSimilarities[i]] > 3:
		print(f"You answered more than 3 questions the same as {sortedSimilarities[i]}!")