import sys
import struct

from INES import Header
from MetroidRoom import Room
from MetroidZone import *

overallMapBaseStart = 0x254E
overallMapBaseEnd = 0x256D


zones = {
	ZoneType.BRINSTAR: 	ZoneFactory.get(ZoneType.BRINSTAR),
	ZoneType.NORFAIR: 	ZoneFactory.get(ZoneType.NORFAIR),
	ZoneType.TOURIAN: 	ZoneFactory.get(ZoneType.TOURIAN),
	ZoneType.KRAID: 	ZoneFactory.get(ZoneType.KRAID),
	ZoneType.RIDLEY: 	ZoneFactory.get(ZoneType.RIDLEY)
}

######################################

def unpackPointer(offset, zone):
	if not zone in zones:
		raise ValueError ("Invalid argument: zone")

	data = fileContent[offset:offset + 2]
	parts = struct.unpack("BB", data)

	lowByte = parts[0]
	highByte = parts[1]

	return lowByte + (highByte * 0x100) - zones[zone].memoryDiff()


def printBrinstarRoom(roomId):

	roomDataOffset = brinstarRoomPointerValues[roomId]
	roomNumBytes = brinstarRoomPointerValues[roomId + 1] - roomDataOffset
	roomBytes = struct.unpack("B" * roomNumBytes, fileContent[roomDataOffset : roomDataOffset + roomNumBytes ])

	structureOffset = brinstarStructureData[roomId]
	structureNumBytes = brinstarStructureData[roomId + 1] - structureOffset
	structureBytes = struct.unpack("B" * structureNumBytes, fileContent[structureOffset : structureOffset + structureNumBytes ])

	print ("Room[%02x] (bytes)" % roomId)

	if 1 == 1:
		print (" data (%d):" % roomNumBytes	)
		for i in range(roomNumBytes):
			print (" %02x" % roomBytes[i], end="")
			if i == 0 or i == 16:
				print ("")
			if roomBytes[i] == 0xfd:
				print ("\n")
		print ("")

	print (" struct (%d):" % structureNumBytes, end="")
	print (" %d macros:" % structureBytes[0], end=" ")
	print (", ".join("%02x" % b for b in structureBytes[1: structureNumBytes - 1]))
	print ("")
	print (brinstarObjectDoorEnemies[roomId])


def printWholeMap():
	for i in range(32):
		row = "".join([("%02x " % idx) if (idx < 255) else '   ' for idx in mapDataRows[i]])
		row += " %d B" % len(mapDataRows[i])
		print ("%03d: " % i, end="")
		print (row)


############################################################################
############################################################################

fileContent = None

with open("metroid.nes", "rb") as file:
	fileContent = file.read()

if fileContent is None:
	print ("Failed to read metroid.nes")
	sys.exit(0)


inesHeader = Header(fileContent)

print(inesHeader)


mapDataRowOffsets = []
mapDataRows = []

bytesRead = 0

### load map for the entire game ###

# start by creating offset table
offsetIndex = 0
for offset in range(32):
	offsetBytes = offset * 0x20
	start = overallMapBaseStart + offsetBytes
	end   = overallMapBaseEnd   + offsetBytes + 1
	
	bytesRead += (end - start)
	data = fileContent[start:end]
	newRow = struct.unpack("B" * 32, data)
	
	mapDataRows.append(newRow)
	offsetIndex += 1


###################################### load brinstar

# load brinstar rooms - room pointers
brinstarRoomPointerBase = 0x6324
brinstarRoomPointerNum = 47
brinstarRoomPointerValues = []

for offsetIndex in range(brinstarRoomPointerNum):
	offset = brinstarRoomPointerBase + (2 * offsetIndex)
	roomPointer = unpackPointer(offset, ZoneType.BRINSTAR)
	brinstarRoomPointerValues.append(roomPointer)
	#print ("room[%02x] (%x - %x) => %X" % (offsetIndex, offset, offset + 1, roomPointer))
	offsetIndex += 1


# load brinstar structure - structure / object pointers
brinstarStructureObjectBase = 0x6382
brinstarStructurePointersNum = 50
brinstarStructureData = []

for offsetIndex in range(brinstarStructurePointersNum):
	offset = brinstarStructureObjectBase + (2 * offsetIndex)
	structurePointer = unpackPointer(offset, ZoneType.BRINSTAR)
	brinstarStructureData.append(structurePointer)
	#print ("struct[%02x] (%x - %x) => %X" % (offsetIndex, offset, offset + 1, structurePointer))
	offsetIndex += 1

# load brinstar objects / doors / enemies

# using hardcoded set of pointers, since they each vary in size
brinstarObjectDoorEnemyPointers = (0x6451, 0x6463), (0x6464, 0x646B), (0x646C, 0x648F), (0x6490, 0x64CA), (0x64CB, 0x64FC), (0x64FD, 0x6533), (0x6534, 0x6569), (0x656A, 0x6596), (0x6597, 0x65C8), (0x65C9, 0x65EC), (0x65ED, 0x6624), (0x6625, 0x6644), (0x6645, 0x6670), (0x6671, 0x669C), (0x669D, 0x66C0), (0x66C1, 0x66EA), (0x66EB, 0x6724), (0x6725, 0x674B), (0x674C, 0x6777), (0x6778, 0x679A), (0x679B, 0x67B2), (0x67B3, 0x67DF), (0x67E0, 0x6800), (0x6801, 0x682A), (0x682B, 0x686A), (0x686B, 0x689A), (0x689B, 0x68C0), (0x68C1, 0x68F6), (0x68F7, 0x691F), (0x6920, 0x693A), (0x693B, 0x697A), (0x697B, 0x69A6), (0x69A7, 0x69D5), (0x69D6, 0x6A05), (0x6A06, 0x6A2F), (0x6A30, 0x6A65), (0x6A66, 0x6AB3), (0x6AB4, 0x6AF5), (0x6AF6, 0x6B28), (0x6B29, 0x6B57), (0x6B58, 0x6B80), (0x6B81, 0x6BA1), (0x6BA2, 0x6BCE), (0x6BCF, 0x6C33), (0x6C34, 0x6C5C), (0x6C5D, 0x6C79), (0x6C7A, 0x6C93)
brinstarObjectDoorEnemiesNum = 47
brinstarObjectDoorEnemies = []

offsetIndex = 0
for offsets in brinstarObjectDoorEnemyPointers:
	start = offsets[0]
	end = offsets[1]
	roomBytes = end - start

	data = fileContent[start:end]
	roomData = struct.unpack("B" * roomBytes, data)

	room = Room()
	room.unpackRoom(roomData)

	brinstarObjectDoorEnemies.append(room)

	offsetIndex += 1


# printWholeMap()

#for roomId in range(0x17, 0x18):
#printBrinstarRoom(9)
#printBrinstarRoom(0x17)

# According to gfx disassembly writeup, the brinstar tiles should be located at 0x9DA0
# A hexdump shows the same data actually in the rom on address 0x19DB0
# so what is the equation?


brinstarMemDiff = zones[ZoneType.BRINSTAR].memoryDiff()
print ("%x" % (ofs - 0x8000 - brinstarMemDiff))

btsStr = fileContent[ofs : ofs + 0x10]
numBts = len(btsStr)
bts = struct.unpack("B" * numBts, btsStr)
print (" ".join(["%02x" % x for x in bts]))


print ("total address space: 0x%x" % len(fileContent))
#print (" ".join(["%02x" % x for x in brinstarRoomPointerValues[0x17]]))


#print (" ".join(["%02x" % x for x in roomData]))


