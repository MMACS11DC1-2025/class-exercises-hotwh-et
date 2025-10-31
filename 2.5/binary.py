code = "01010101 01101110 01100100 01100101 01110010 00100000 01011001 01101111 01110101 01110010 00100000 01010011 01100101 01100001 01110100 100101000111011 101111101000001 110110011110"

bytes = code.split(" ")

for byte in bytes:
	number = 0
	for i in range(len(byte)):
		value = 2**(len(byte)-1-i) if byte[i] == "1" else 0
		number += value
	print(f"{number:<5} {chr(number)}")
