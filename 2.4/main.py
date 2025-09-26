responsesDict = {}
similarityScores = {}

with open("./2.4/responses.csv", "r") as file:
	headers = file.readline().strip()
	headersList = headers.split(",")
	responses = file.read().strip().split("\n")
	nameIndex = headersList.index("Name")
	for response in responses:
		responseList = response.strip().split(",")
		responsesDict[responseList[nameIndex]] = dict(zip(headersList[nameIndex+1:], responseList[nameIndex+1:]))