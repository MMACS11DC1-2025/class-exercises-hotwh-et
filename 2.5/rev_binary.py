input = "19003 24385 3486"

decimals = input.split(" ")

for decimal in decimals:
	binary = "0"*32
	
	remaining = int(decimal)

	while remaining > 0:
		lastExponent = 0
		exponent = 0

		while 2**(lastExponent + 1) <= remaining:
			lastExponent += 1
		
		exponent = lastExponent
		
		remaining = remaining - 2**exponent
		binary = binary[:-(exponent+1)] + "1" + ("0" * (exponent))
	
	fmtBinary = binary.lstrip("0")

	print(fmtBinary)