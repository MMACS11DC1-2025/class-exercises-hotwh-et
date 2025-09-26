responsesDict = {}

with open("./2.4/responses.csv", "r") as file:
	headers = file.readline().strip()
	headersList = headers.split(",")
	responses = file.read().strip().split("\n")
	nameIndex = headersList.index("Name")
	for response in responses:
		responseList = response.strip().split(",")
		if responseList[nameIndex] == "Ethan Wong":
			print(response)
			break