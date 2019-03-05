
from MetroidZone import *


class Brinstar(Zone):

	memoryOffset = 0x3FF0

	palettePointers = {
		"background1": 0x6284,
		"background2": 0x6288,
		"background3": 0x628C,
		"background4": 0x6290,

		"background alt1": 0x62C0,
		"background alt2": 0x62C4,
		"background alt3": 0x62C8,
		"background alt4": 0x62CC,

		"sprite1": 0x6294,
		"sprite2": 0x6298,
		"sprite3": 0x629C,
		"sprite4": 0x62A0
	}

	def __init__(self):
		super().__init__(ZoneType.BRINSTAR)