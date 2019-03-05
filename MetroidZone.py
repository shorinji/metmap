from enum import Enum

class ZoneType(Enum):
	BRINSTAR = 1
	NORFAIR = 2
	TOURIAN = 3
	KRAID = 4
	RIDLEY = 5


class Zone:
	# From https://datacrystal.romhacking.net/wiki/Metroid:Pointer_format :
	# These values account for 
	#  (A) the fact that data is banked into RAM at $8000, 
	#  (B) the 16-byte ROM header, and 
	#  (C) the ROM bank the data is contained in.
	memoryBankDiffs = {
		ZoneType.BRINSTAR: 0x3FF0,
		ZoneType.NORFAIR: -0x10,
		ZoneType.TOURIAN: -0x4010,
		ZoneType.KRAID:    0x7FF0,
		ZoneType.RIDLEY:   0x3FF0
	}

	# FROM Editroid/LevelRom.cs: LevelBanks
	# Brinstar = 0x4000
	# Norfair  = 0x8000
	# Tourian  = 0xC000
	# Kraid    = 0x10000
	# Ridley   = 0x14000


	def __init__(self, type):
		if type in ZoneType:
			self.type = type
		else:
			raise ValueError ("Zone(): Invalid type specified")

	def getPalettePointers(self):
		return self.palettePointers

	def memoryDiff(self):
		return self.memoryBankDiffs[self.type]


