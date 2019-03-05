
class Room:

	def __init__(self):
		self.colorAttribute = 0
		self.roomObjects = []


	def getRoomObjects(self):
		return self.roomObjects

	def unpackRoom(self, offsetIndex, roomData):
		roomBytes = len(roomData)

		index = 0
		self.colorAttribute = roomData[index]
		self.roomObjects = []
		self.enemyData = []

		#print " ", " ".join(["%02x" % x for x in roomData[index:]])	

		index += 1
		atEndOfData = (index >= roomBytes) or (roomData[index] == 0xFD) or (roomData[index] == 0xFF)

		# read room object data
		while not atEndOfData:
			obj = roomData[index : index + 3]
			#print " ", (" ".join([ "%02x" % x for x in obj ]))

			self.roomObjects.append(obj)
			
			index += 3
			atEndOfData = (index >= roomBytes) or (roomData[index] == 0xFD) or (roomData[index] == 0xFF)

		if index >= roomBytes or roomData[index] == 0xFF:
			return

		if roomData[index] == 0xFD:
			index += 1

		# read door data
		self.doors = []
		while index < roomBytes and roomData[index] == 0x02:
			doorByte = roomData[index + 1]

			highNibble = doorByte >> 4
			lowNibble = doorByte & 0xF

			doorType = ""

			if lowNibble == 0:
				doorType = "red"
			elif lowNibble == 1:
				doorType = "blue"
			elif lowNibble == 2:
				doorType = "purple/yellow"
			else:
				doorType = "unknown(%x)" % lowNibble

			if highNibble == 0xB:
				side = "left"
			elif highNibble == 0xA:
				side = "right"
			else:
				print ("unknown door data (02 %02x)" % doorByte)
				continue

			self.doors.append({"side": side, "type": doorType })
			index += 2

		# read enemy data
		self.enemyData = []
		while not (index >= (roomBytes - 2) or roomData[index] == 0xFF):
			enemyBytes = roomData[index : index + 4]
			self.enemyData.append({ "sprite": enemyBytes[0], "type": enemyBytes[1], "location": enemyBytes[2] })
			index += 3

	def oneObjectToString(self, obj):
		return "(%02x %02x %02x)" % obj

	def roomObjectsToString(self):
		s = ""
		i = 0
		for obj in self.roomObjects:
			pos = obj[0]
			ptr = obj[1]
			attr = obj[2]

			x = pos & 0xF
			y = pos >> 4
			s += "  [%d] " % i
			s += " tile: (%2d, %2d), obj: 0x%02x, palette: 0x%02x\n" % (x, y, ptr, attr)
			i += 1

		return s

	def __repr__(self):
		s = " room palette: %d\n" % self.colorAttribute
		s += " room objects:\n"
		s += self.roomObjectsToString()
		#s += " ".join([self.oneObjectToString(obj) for obj in self.roomObjects]) 
		s += "\n"
		s += " enemies:\n"
		i = 0
		for e in self.enemyData:
			pos = e["location"]
			x = pos & 0xF
			y = pos >> 4
			s += "  [%d]  " % i
			s += "sprite: %02x, type: %02x tile: (%d, %d)\n" % (e["sprite"], e["type"], x, y)
			i += 1
		s += "\n"
		return s