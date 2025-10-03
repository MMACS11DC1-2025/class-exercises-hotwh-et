"""
Create a program that uses comparison operators (< > <= >=).
You must use the class' datafile, 'responses.csv' and analyze it
    to make at least 2 interesting observations.
You may use user input to add interactivity to the program.
You must design your algorithm in English first, then translate it to Python code.
Test as you go! Describe in your comments what steps you took to test your code.
"""
'''
Give the user a list of questions and let them choose one.
For whichever they choose, give them a list of options and let them choose one.
Using their answer, find people who answered the same question with the same answer.
Give the user a list of questions and let them choose one.
Using the obtained list of similar people, find their responses to this second question.
Choose a random response out of these responses, and tell it to the user.
'''
import random

# Variables that will be used throughout the program
responsesDict = {} # {name:{question:response}}
responseOptions = {} # {question:[responses]}
questions = [] # [questions]

# Function to ask questions from a list of options.
# Handles invalid input by taking input again
'''
Tests
When inputting "1", the function returns the first value from the array
When inputting "2", the function returns the second value from the array
When inputting "0", it prints "That is not a valid option!" and takes input again
When inputting "lorem", it prints "That is not a valid option!" and takes input again
When inputting "" (nothing), it prints "That is not a valid option!" and takes input again
'''
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
		except (ValueError, IndexError):
			# Catches input not being an integer or input being out of bounds
			print("That is not a valid option!")
	
	print()
	
	return questionOptions[responseIndex]

# Open the data file
'''
Tests
If the file exists and is in a valid format, the data is processed and the program continues
If the file does not exist, it prints an error and an explanation message then exits
If the file is not in CSV format, it prints an error and an explanation message then exits
If the file has no questions, it prints an error and an explanation message then exits
If the file has no data, it prints an error and an explanation message then exits
'''
try:
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
except OSError:
	print("There was an error opening the data file.")
	print("Does the file exist at \"./2.4/responses.csv\"?")
	exit()
except (ValueError, IndexError):
	print("There was an error processing the data file.")
	print("Is the data in valid CSV format with headers, and contains a \"Name\" header?")
	exit()

# Data validation, explained in tests block above
if (len(questions) <= 0):
	print("There were no questions found in the file.")
	print("Are the questions present in the CSV file?")
	exit()
respondentNames = list(responsesDict.keys())
if (len(respondentNames) <= 0 or respondentNames[0] == ""):
	print("There was no data found in the file.")
	print("Is the data present in the CSV file?")
	exit()

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