"""
Create a program that uses comparison operators (< > <= >=).
You must use the class' datafile, 'responses.csv' and analyze it
    to make at least 2 interesting observations.
You may use user input to add interactivity to the program.
You must design your algorithm in English first, then translate it to Python code.
Test as you go! Describe in your comments what steps you took to test your code.
"""
import random

# Variables that will be used throughout the program
responsesDict = {} # {name:{question:response}}
responseOptions = {} # {question:[responses]}
questions = [] # [questions]

# Function to ask questions from a list of options.
# Handles invalid input by taking input again
def askQuestion(question, questionOptions):
	print(question)
	# Print each option from the given list
	for i in range(len(questionOptions)):
		print(f"{i+1}: {list(questionOptions)[i]}")
	
	responseIndex = 0

	valid = False
	# Loop until input is valid
	while not valid:
		response = input()
		try:
			responseInt = int(response)
			responseIndex = responseInt-1
			if responseInt <= len(questions) and responseIndex >= 0:
				valid = True
				break
			else:
				raise IndexError
		except:
			# Catches input not being an integer or input being out of bounds
			print("That is not a valid option!")
	
	print()
	
	return questionOptions[responseIndex]

# Open the data file
with open("./2.4/responses.csv", "r") as file:
	# Get the headers as a list
	headersList = file.readline().strip().split(",")
	# Get the responses
	responses = file.read().strip().split("\n")
	# Get the index of the "Name" field to avoid getting and preceding field(s)
	nameIndex = headersList.index("Name")
	# Get the questions by getting every header after the "Name" field
	questions = headersList[nameIndex+1:]
	# Initialize the responseOptions variable with an empty array for each question
	for question in questions:
		responseOptions[question] = []
	# For every response, add the relevant data to the lists and dicts
	for response in responses:
		# Split the response line into individual responses to each question
		responseList = response.strip().split(",")
		individualResponses = responseList[nameIndex+1:]
		responsesDict[responseList[nameIndex]] = dict(zip(questions, individualResponses))
		# For each individual response, add the response to the responseOptions list if not already present
		for i in range(len(individualResponses)):
			if responseList[nameIndex+1+i] not in responseOptions[questions[i]]:
				responseOptions[questions[i]].append(responseList[nameIndex+1+i])

# Sort the responseOptions
for question, answers in responseOptions.items():
	responseOptions[question] = sorted(answers)

# Print the intro message
print("="*50)
print("Pick a question and answer it.")
print("Based on your answer, I will predict your answer to another question!")
print("="*50)

# Ask for the question
requestedQuestion = askQuestion("Pick a question to answer (Enter the number on the left)", questions)

# Ask for the answer
chosenResponse = askQuestion("Pick your answer (Enter the number on the left)", responseOptions[requestedQuestion])

# Find similar people
similarPeople = []
for person, personData in responsesDict.items():
	if personData[requestedQuestion] == chosenResponse:
		similarPeople.append(person)

# Ask for the second question
requestedQuestion2 = askQuestion("Pick a question and I will predict your answer (Enter the number on the left)", questions)

# Get the answers of the similar people for the question and store their counts
similarPeopleAnswersCounter = {}
for person in similarPeople:
	personData = responsesDict[person]
	answer = personData[requestedQuestion2]
	similarPeopleAnswersCounter[answer] = similarPeopleAnswersCounter.get(answer, 0) + 1

# Separate the responses and weight them according to how common they are
predictionOptions = []
predictionWeights = []
for option, count in similarPeopleAnswersCounter.items():
	predictionOptions.append(option)
	# Make more common responses exponentially more likely than rarer responses
	# The exponent can be configured. Higher numbers make the common responses more common
	predictionWeights.append(count ** 1.2)

# Choose a random response from the similar people's answers using calculated weights
predictedAnswer = random.choices(predictionOptions, weights=predictionWeights)[0]
print(f"I predict your answer is {predictedAnswer}!")