"""
Machines are good at crunching numbers - faster and more accurately than most 
humans! Create a small program that calculates something useful to you 
(making you smile is useful). It should take user input, at use at least one of the 
number operators we saw in class: + / * . You may modify one of your previous 
exercises to include calculations, if you wish.

Remember to design your algorithm in English first, then translate it to Python 
code. Test as you go!
"""

input1 = input("Please provide the first number: ")
input2 = input("Please provide the operation (+-*/%^): ")
input3 = input("Please provide the second number: ")

num1 = 0
num2 = 0

try:
	num1 = float(input1)
	num2 = float(input3)
except:
	print("Invalid input! You must enter a number.")
	exit()

result = 0

match input2:
	case "+":
		result = num1 + num2
	case "-":
		result = num1 - num2
	case "*":
		result = num1 * num2
	case "/":
		if (num2 == 0):
			result = "undefined"
		else:
			result = num1 / num2
	case "%":
		result = num1 % num2
	case "^":
		result = num1 ** num2
	case _:
		print("Invalid input! That operator is not recognized.")
		exit()

print(f"Your result is {result}")