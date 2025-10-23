responsesDict = {}
responseCounter = {}

with open("./2.4/responses.csv", "r") as file:
	headers = file.readline().strip()
	headersList = headers.split(",")
	responses = file.read().strip().split("\n")
	nameIndex = headersList.index("Name")
	for response in responses:
		responseList = response.strip().split(",")
		responsesDict[responseList[nameIndex]] = dict(zip(headersList[nameIndex+1:], responseList[nameIndex+1:]))


for responses in responsesDict.values():
	for question, answer in responses.items():
		responseCounts = responseCounter.get(question, {})
		responseCounts[answer] = responseCounts.get(answer, 0) + 1
		responseCounter[question] = responseCounts

sortedCounter = {}
for question, responses in responseCounter.items():
	sortedAnswer = sorted(responses, key=lambda number: responses[number], reverse=True)
	sortedCount = sorted(responses.values(), reverse=True)
	sortedCounter[question] = dict(zip(sortedAnswer, sortedCount))

print("Which question would you like data on? (Enter the number)")
for i in range(len(sortedCounter.keys())):
	print(f"{i+1}: {list(sortedCounter.keys())[i]}")

requestedQuestionIndex = 0

valid = False
while not valid:
	requestedQuestionInput = input()
	try:
		requestedQuestionIndex = int(requestedQuestionInput)-1
		if requestedQuestionIndex+1 <= len(sortedCounter) and requestedQuestionIndex >= 0:
			valid = True
		else:
			raise Exception("Index not found")
	except:
		print("That is not a valid option!")

requestedQuestion = list(sortedCounter.keys())[requestedQuestionIndex]
requestedQuestionAnswers = sortedCounter[requestedQuestion]

for i in range(len(requestedQuestionAnswers)):
	print(f"#{i+1} - {list(requestedQuestionAnswers.keys())[i]}: {list(requestedQuestionAnswers.values())[i]} votes")