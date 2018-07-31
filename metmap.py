import sys
import struct

from MetroidRoom import *

overallMapBaseStart = 0x254E
overallMapBaseEnd = 0x256D

zoneMemoryOffsets = {
	'brinstar': 0x3FF0,
	'norfair': -0x10,
	'tourian': -0x4010,
	'kraid':    0x7FF0,
	'ridley':   0x3FF0
}


######################################

def unpackPointer(offset, zone):
	data = fileContent[offset:offset + 2]
	parts = struct.unpack("BB", data)

	lowByte = parts[0]
	highByte = parts[1]

	return lowByte + (highByte * 0x100) - zoneMemoryOffsets[zone]


def printBrinstarRoom(roomId):

	roomDataOffset = brinstarRoomPointerValues[roomId]
	roomNumBytes = brinstarRoomPointerValues[roomId + 1] - roomDataOffset
	fmt = "".join(["B" for x in range(roomNumBytes)])
	roomBytes = struct.unpack(fmt, fileContent[roomDataOffset : roomDataOffset + roomNumBytes ])

	structureOffset = brinstarStructureData[roomId]
	structureNumBytes = brinstarStructureData[roomId + 1] - structureOffset
	fmt = "".join(["B" for x in range(structureNumBytes)])
	structureBytes = struct.unpack(fmt, fileContent[structureOffset : structureOffset + structureNumBytes ])

	room = brinstarRooms[roomId]

	print "Room[%02x] (bytes)" % roomId

	if 1 == 1:
		print " data (%d):" % roomNumBytes	
		for i in range(roomNumBytes):
			print (" %02x" % roomBytes[i]),
			if i == 0 or i == 16:
				print ""
			if roomBytes[i] == 0xfd:
				print "\n"
		print ""

	print " struct (%d):" % structureNumBytes,
	print " %d macros:" % structureBytes[0], "",
	print ", ".join("%02x" % b for b in structureBytes[1: structureNumBytes - 1])
	print ""

	print room


######################################

fileContent = None

with open("metroid.nes", "rb") as file:
	fileContent = file.read()

if fileContent is None:
	print "Failed to read metroid.nes"
	sys.exit(0)

###################################### load overall map


mapDataRowOffsets = []
mapDataRows = []

bytesRead = 0
for offset in range(32):
	offsetBytes = offset * 0x20
	start = overallMapBaseStart + offsetBytes
	end   = overallMapBaseEnd   + offsetBytes
	addressSpan = (start, end)

	#print "reading 0x%4X - 0x%4X" % (start, end)
	mapDataRowOffsets.append(addressSpan)
	bytesRead += ((end + 1) - start)

print "Read %d bytes in total" % bytesRead


	
offsetIndex = 0
for offsets in mapDataRowOffsets:
	start = offsets[0]
	end = offsets[1] + 1

	data = fileContent[start:end]

	newRow = struct.unpack("B" * 32, data)
	#print type(newRow[0])
	#print "[%d] " % (offsetIndex), newRow
	
	mapDataRows.append(newRow)
	offsetIndex += 1

#print "mapDataRowOffsets contains %d rows" % len(mapDataRowOffsets)
#print "mapDataRows contains %d rows" % len(mapDataRows)

#blankRoom = u'\033[0m   \033[0m'
blankRoom = '   '

for i in range(32):
	print ("%03d: " % i),
	row = "".join([("%02x " % idx) if (idx < 255) else blankRoom for idx in mapDataRows[i]])
	#row = "".join([("%02x " % idx) for idx in mapDataRows[i]])
	row += " %d B" % len(mapDataRows[i])
	print row



###################################### load brinstar

brinstarRoomPointerBase = 0x6324
brinstarStructureObjectBase = 0x6382

brinstarNumRoomPointers = 47
brinstarNumStructurePointers = 50


brinstarRoomPointerOffsets = [brinstarRoomPointerBase + (2 * i) for i in range(brinstarNumRoomPointers)]
brinstarRoomPointerValues = []

brinstarStructureObjectOffsets = [brinstarStructureObjectBase + (2 * i) for i in range(brinstarNumStructurePointers)]
brinstarStructureData = []

brinstarRoomPointers = (0x6451, 0x6463), (0x6464, 0x646B), (0x646C, 0x648F), (0x6490, 0x64CA), (0x64CB, 0x64FC), (0x64FD, 0x6533), (0x6534, 0x6569), (0x656A, 0x6596), (0x6597, 0x65C8), (0x65C9, 0x65EC), (0x65ED, 0x6624), (0x6625, 0x6644), (0x6645, 0x6670), (0x6671, 0x669C), (0x669D, 0x66C0), (0x66C1, 0x66EA), (0x66EB, 0x6724), (0x6725, 0x674B), (0x674C, 0x6777), (0x6778, 0x679A), (0x679B, 0x67B2), (0x67B3, 0x67DF), (0x67E0, 0x6800), (0x6801, 0x682A), (0x682B, 0x686A), (0x686B, 0x689A), (0x689B, 0x68C0), (0x68C1, 0x68F6), (0x68F7, 0x691F), (0x6920, 0x693A), (0x693B, 0x697A), (0x697B, 0x69A6), (0x69A7, 0x69D5), (0x69D6, 0x6A05), (0x6A06, 0x6A2F), (0x6A30, 0x6A65), (0x6A66, 0x6AB3), (0x6AB4, 0x6AF5), (0x6AF6, 0x6B28), (0x6B29, 0x6B57), (0x6B58, 0x6B80), (0x6B81, 0x6BA1), (0x6BA2, 0x6BCE), (0x6BCF, 0x6C33), (0x6C34, 0x6C5C), (0x6C5D, 0x6C79), (0x6C7A, 0x6C93)
brinstarRooms = []

# load brinstar map
offsetIndex = 0
for offset in brinstarRoomPointerOffsets:

	roomPointer = unpackPointer(offset, 'brinstar')

	#print "room[%02x] (%x - %x) => %X" % (offsetIndex, offset, offset + 1, roomPointer)

	brinstarRoomPointerValues.append(roomPointer)
	offsetIndex += 1

# load brinstar object/structure
offsetIndex = 0
for offset in brinstarStructureObjectOffsets:
	structurePointer = unpackPointer(offset, 'brinstar')
	
	#print "struct[%02x] (%x - %x) => %X" % (offsetIndex, offset, offset + 1, structurePointer)

	brinstarStructureData.append(structurePointer)
	offsetIndex += 1


# load brinstar rooms
offsetIndex = 0
for offsets in brinstarRoomPointers:
	start = offsets[0]
	end = offsets[1]
	roomBytes = end - start

	data = fileContent[start:end]
	
	roomData = struct.unpack("B" * roomBytes, data)

	room = Room()
	room.unpackRoom(roomData)

	brinstarRooms.append(room)

	offsetIndex += 1


#for roomId in range(0x17, 0x18):
printBrinstarRoom(9)
#printBrinstarRoom(0x17)

# 0x19DB0
ofs = 0x19DB0 #- zoneMemoryOffsets["brinstar"]

print "%x" % (ofs - 0x8000 - zoneMemoryOffsets["brinstar"])

btsStr = fileContent[ofs : ofs + 0x10]
numBts = len(btsStr)
bts = struct.unpack("B" * numBts, btsStr)
print " ".join(["%02x" % x for x in bts])


print "total address space: 0x%x" % len(fileContent)
#print (" ".join(["%02x" % x for x in brinstarRoomPointerValues[0x17]]))


#print (" ".join(["%02x" % x for x in roomData]))


