"""
Write an Age in 2049 program that asks your age and outputs how old you'll be 31 years from now.

Examples:

How old are you?
> 10
In 2056, you will be 41 years old!
--
How old are you?
> 25
In 2056, you will be 56 years old!
"""
from datetime import datetime

currentAge = int(input("How old are you? "))
futureAge = currentAge + (2049 - datetime.now().year)
print(f"In 2049, you will be {futureAge}")