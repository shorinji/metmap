
from MetroidZone import *
from MetroidBrinstar import Brinstar


class ZoneFactory:
	
	def get(zoneType):
		if zoneType == ZoneType.BRINSTAR:
			return Brinstar()
		return Zone(zoneType)