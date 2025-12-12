"""
Exercises:
Write recursive functions for each of the following problems:
"""

# Exercise 0: Factorial
# Remember that n! is defined as n * (n-1)! and 0! is 1
def factorial(n):
	if n < 1:
		raise SyntaxError
	if n == 1:
		return 1
	return n * factorial(n-1)

print("="*10)
print("Factorial")
print("="*10)

print(factorial(1)) # Expected output: 1
print(factorial(2)) # Expected output: 2
print(factorial(3)) # Expected output: 6
print(factorial(4)) # Expected output: 24
print(factorial(5)) # Expected output: 120

# Exercise 1: Power Function
# Create a function called power(x, y) that calculates x raised to the power of y (x^y).
# Remember that x^y is defined as x * x^(y-1) and x^0 is 1.

def power(x, y):
	if y == 0:
		return 1
	return x * power(x, y-1)

# Test cases
print("="*10)
print("Power")
print("="*10)

print(power(2, 3))  # Expected output: 8
print(power(5, 0))  # Expected output: 1
print(power(3, 2))  # Expected output: 9

# Exercise 2: Sum of Integers
# Write a function named sum_list_recursive(numbers, index) that
# takes a list of integers and an index and returns their sum.
# Remember that the sum of a list is the first item plus the sum of the rest of the list.

def sum_list_recursive_helper(numbers, index):
	if (index == len(numbers)):
		return 0
	return numbers[index] + sum_list_recursive_helper(numbers, index+1)

def sum_list(numbers):
	if len(numbers) > 0:
		return sum_list_recursive_helper(numbers, 0)
	return 0

# Test cases
print("="*10)
print("Sum list")
print("="*10)

print(sum_list([1, 2, 3, 4]))   # Expected output: 10
print(sum_list([-1, 1, 2]))     # Expected output: 2
print(sum_list([5, 10, 15]))    # Expected output: 30

# Exercise 3: Count Vowels
# Develop a function called count_vowels(string) to count the number of vowels in the provided string.
# You can assume the string will be entirely lowercase.
# Remember that the count of vowels in a string is the number of vowels (0 or 1) in the first character
# plus the number of vowels in the rest of the string.
# NOTE: you will also need to implement a recursive helper, like in exercise 2.

vowels = "aeiou"
def count_vowels_recursive_helper(word, index):
	if (index == len(word)):
		return 0
	return (1 if word[index] in vowels else 0) + count_vowels_recursive_helper(word, index+1)

def count_vowels(word):
	return count_vowels_recursive_helper(word, 0)

# Test cases
print("="*10)
print("Count vowels")
print("="*10)

print(count_vowels("hello"))     # Expected output: 2
print(count_vowels("python"))    # Expected output: 1
print(count_vowels("aeiou"))     # Expected output: 5

# Exercise 4: Reverse String
# Implement a function named reverse_string(s) that returns the reversed version of the string.
# Remember that the reverse of a string is the last character, concatenated with the reverse of
# the rest of the string.
# NOTE: You might need a recursive helper like in exercises 2 and 3.

def reverse_string_recursive_helper(word, index):
	if (-index-1 == len(word)):
		return ""
	return word[index] + reverse_string_recursive_helper(word, index-1)

def reverse_string(word):
	return reverse_string_recursive_helper(word, -1)

# Test cases
print("="*10)
print("Reverse string")
print("="*10)

print(reverse_string("hello"))    # Expected output: "olleh"
print(reverse_string(""))         # Expected output: ""
print(reverse_string("Python"))   # Expected output: "nohtyP"
