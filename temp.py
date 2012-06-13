"""
def shuffle(s):
		
	if s:
		random.seed()
		anagram = ""
		while s:
			randNumber = random.getrandbits(s.__len__())	
			randNumber = randNumber % s.__len__()
			anagram = anagram + s[randNumber]
			if s.__len__() > 1:
				s = s[:randNumber] + s[randNumber+1:]
			else:
				s = ""
		print "shuffled string: ", anagram
	else:
		print "input is not a valid string, abort"
		quit()	
"""

if __name__ == "__main__":
"""	print "string input: ", sys.argv[1]
	if int(sys.argv[2]):
		for i in range(int(sys.argv[2])):
			shuffle(sys.argv[1])
	else:
		print "invalid argument for iterations: ", sys.argv[2]
		quit()
"""
