from enum import Enum

class ZoneType(Enum):
	BRINSTAR = 1
	NORFAIR = 2
	TOURIAN = 3
	KRAID = 4
	RIDLEY = 5


class Zone:
	zoneMemoryOffsets = {
		ZoneType.BRINSTAR: 0x3FF0,
		ZoneType.NORFAIR: -0x10,
		ZoneType.TOURIAN: -0x4010,
		ZoneType.KRAID:    0x7FF0,
		ZoneType.RIDLEY:   0x3FF0
	}

	def __init__(self, type):
		print (type)
		if type in ZoneType:
			print ("yes")
			self.type = type
		else:
			print ("no")

	def memoryDiff(self):
		return self.zoneMemoryOffsets[self.type]


class ZoneFactory:
	def get(zoneType):
		return Zone(zoneType)