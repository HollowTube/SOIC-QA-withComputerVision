def convertToArray(foo):
	return [int(x) for x in foo.split(",")]
def readFile(filename):
	parameterList = open(filename,"r")
	list = []
	for line in parameterList:
		if line[0] is not '#' and line is not '\n':
			list.append(line[:-1])
	print(list)
	binThresholdPin = int(list[0])
	binThresholdLetter = int(list[1])
	
	#ROIs in the format of (x1,y1,x2,y2)
	topPinRow = convertToArray(list[2])
	botPinRow = convertToArray(list[3])
	centerLettering = convertToArray(list[4])
	BLPin = convertToArray(list[5])
	URPin =convertToArray(list[6])
	#Pin spacing parameters
	maxPinDist = int(list[7])
	minPinDist = int(list[8])

	print(URPin)


readFile("20Pins.txt")
convertToArray('1,2,3,4')
