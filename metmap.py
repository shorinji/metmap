import sys
import struct
import pygame
from pygame.locals import *

from INES import Header
from MetroidRoom import Room
from MetroidZone import *
from MetroidBrinstar import *
from ZoneFactory import ZoneFactory
overallMapBaseStart = 0x254E
overallMapBaseEnd = 0x256D

macroDefs = {
	ZoneType.BRINSTAR: 	{ "offset":  0x6F00, "len": 260, "table": None },
	ZoneType.NORFAIR: 	{ "offset":  0xAEFC, "len": 248, "table": None },
	ZoneType.TOURIAN: 	{ "offset":  0xEE59, "len": 216, "table": None },
	ZoneType.KRAID:   	{ "offset": 0x12C42, "len": 164, "table": None },
	ZoneType.RIDLEY:    { "offset": 0x16B33, "len": 132, "table": None }
}


zones = {
	ZoneType.BRINSTAR: 	ZoneFactory.get(ZoneType.BRINSTAR),
	ZoneType.NORFAIR: 	ZoneFactory.get(ZoneType.NORFAIR),
	ZoneType.TOURIAN: 	ZoneFactory.get(ZoneType.TOURIAN),
	ZoneType.KRAID: 	ZoneFactory.get(ZoneType.KRAID),
	ZoneType.RIDLEY: 	ZoneFactory.get(ZoneType.RIDLEY)
}

# black, cyan, dark blue, dark sea grean
# dark blue: 		Color(0x1b2cf0)
# cyan: 			Color(0x5991ff)
# dark sea green: 	Color(0x008089)
boringBrinstarPalette = [Color(0), Color(0X1B2CF0FF), Color(0X5991FFFF) , Color(0X008089FF)]


######################################

def loadMacroTable(zone):
	if not zone in macroDefs:
		raise ValueError("Invalid zone specified")

	if fileContent is None:
		raise ValueError("rom file must be loaded before macros can be loaded")

	macroDefsEntry = macroDefs[zone]
	macrosOffset = macroDefsEntry["offset"]
	macrosLen = macroDefsEntry["len"]
	data = fileContent[macrosOffset : macrosOffset + macrosLen ]
	macros = struct.unpack("B" * macrosLen, data)
	macroDefsEntry["table"] = macros

	if zone == ZoneType.BRINSTAR:
		print("BRINSTAR MACROS:")
		print(macroDefsEntry["table"])


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

	structureOffset = brinstarStructurePointers[roomId]
	structureNumBytes = brinstarStructurePointers[roomId + 1] - structureOffset
	structureBytes = struct.unpack("B" * structureNumBytes, fileContent[structureOffset : structureOffset + structureNumBytes ])

	print ("Room[%02x]:" % roomId)

	if 1 == 1:
		print (" room pointer data (%d):" % roomNumBytes	)
		for i in range(roomNumBytes):
			print (" %02x" % roomBytes[i], end="")
			if roomBytes[i] == 0xfd:
				print ("")
		print ("")

	print (" structure (%dB):" % structureNumBytes)
	print ("  macros (%d):" % structureBytes[0], end=" ")
	print (", ".join("%02x" % b for b in structureBytes[1: structureNumBytes - 1]))
	# multiply macro num * 4 to find index in MacroTbl	
	print ("")
	print (brinstarObjectDoorEnemies[roomId])


def printWholeMap():
	for i in range(32):
		row = "".join([("%02x " % idx) if (idx < 255) else '   ' for idx in mapDataRows[i]])
		row += " %d B" % len(mapDataRows[i])
		print ("%03d: " % i, end="")
		print (row)


# loop over 16 bytes to unpack one 8x8 pixel tile
def unpackTilePixels(offset):

	tileBytes = fileContent[offset : offset + 16]

	tilePixels = []
	for i in range(8):

		byte1 = tileBytes[i]
		byte2 = tileBytes[i + 8]

		bits0 = ((byte1 & 0b10000000) >> 6) | ((byte2 & 0b10000000) >> 7)
		bits1 = ((byte1 & 0b01000000) >> 5) | ((byte2 & 0b01000000) >> 6)
		bits2 = ((byte1 & 0b00100000) >> 4) | ((byte2 & 0b00100000) >> 5)
		bits3 = ((byte1 & 0b00010000) >> 3) | ((byte2 & 0b00010000) >> 4)
		bits4 = ((byte1 & 0b00001000) >> 2) | ((byte2 & 0b00001000) >> 3)
		bits5 = ((byte1 & 0b00000100) >> 1) | ((byte2 & 0b00000100) >> 2)
		bits6 = ((byte1 & 0b00000010)     ) | ((byte2 & 0b00000010) >> 1)
		bits7 = ((byte1 & 0b00000001) << 1) | ((byte2 & 0b00000001))

		tilePixels.extend([bits0, bits1, bits2, bits3, bits4, bits5, bits6, bits7])

	return tilePixels


def unpackTiles(baseAddress, numBytes):
	numTiles = int(numBytes / 16)
	tiles = {}
	byteIndex = 0
	for tileIndex in range(numTiles):
		tiles[tileIndex] = unpackTilePixels(baseAddress + byteIndex)		
		byteIndex += 16
	return tiles



def drawScaledPixel(outputBaseX, outputBaseY, color, scale, surface):
	# scale up and draw
	for yOffset in range(scale):
		for xOffset in range(scale):
			pos = (outputBaseX + xOffset, outputBaseY + yOffset)
			surface.set_at(pos, color)


# draws a tile scaled onto a surface
def drawTile(tileData, surface):

	scale = blitTileScale

	s = ""
	# for each vertical and horizontal pixel in tile
	for y in range(tileLength):
		for x in range(tileLength):
			
			colorIndex = tileData[(tileLength * y) + x]
			color = boringBrinstarPalette[colorIndex]
			
			outputBaseX = (x * scale)
			outputBaseY = (y * scale)

			drawScaledPixel(outputBaseX, outputBaseY, color, scale, surface)


def printBrinstarStructure(roomId=None):

	for i in range(len(brinstarStructurePointers)):
		if (not roomId is None) and not roomId == i:
			continue

		print ("struct[%02x]: " % i, end=" ")

		currentOffset = 0
		ptr = brinstarStructurePointers[i]
		bt = fileContent[ptr + currentOffset]

		while not bt == 0xFF:
			print ("%02x" % bt, end=" ")

			currentOffset += 1
			ptr = brinstarStructurePointers[i]
			bt = fileContent[ptr + currentOffset]
		print("FF")


############################################################################
############################################################################

fileContent = None

with open("metroid.nes", "rb") as file:
	fileContent = file.read()

if fileContent is None:
	print ("Failed to read metroid.nes")
	sys.exit(0)


for zone in zones.keys():
	loadMacroTable(zone)

nesRomHeader = Header(fileContent)
#print(nesRomHeader)

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

for roomOffset in range(0, brinstarRoomPointerNum * 2, 2):
	offset = brinstarRoomPointerBase + roomOffset
	roomPointer = unpackPointer(offset, ZoneType.BRINSTAR)
	brinstarRoomPointerValues.append(roomPointer)


# load brinstar structure - structure / object pointers
brinstarStructureObjectBase = 0x6382
brinstarStructurePointersNum = 50
brinstarStructurePointers = []

for structureOffset in range(0, brinstarStructurePointersNum * 2, 2):
	offset = brinstarStructureObjectBase + structureOffset
	structurePointer = unpackPointer(offset, ZoneType.BRINSTAR)
	brinstarStructurePointers.append(structurePointer)


#printBrinstarStructure()

# load brinstar objects / doors / enemies

# using hardcoded set of pointers, since they each vary in size
brinstarObjectDoorEnemyPointers = (0x6451, 0x6463), (0x6464, 0x646B), (0x646C, 0x648F), (0x6490, 0x64CA), (0x64CB, 0x64FC), (0x64FD, 0x6533), (0x6534, 0x6569), (0x656A, 0x6596), (0x6597, 0x65C8), (0x65C9, 0x65EC), (0x65ED, 0x6624), (0x6625, 0x6644), (0x6645, 0x6670), (0x6671, 0x669C), (0x669D, 0x66C0), (0x66C1, 0x66EA), (0x66EB, 0x6724), (0x6725, 0x674B), (0x674C, 0x6777), (0x6778, 0x679A), (0x679B, 0x67B2), (0x67B3, 0x67DF), (0x67E0, 0x6800), (0x6801, 0x682A), (0x682B, 0x686A), (0x686B, 0x689A), (0x689B, 0x68C0), (0x68C1, 0x68F6), (0x68F7, 0x691F), (0x6920, 0x693A), (0x693B, 0x697A), (0x697B, 0x69A6), (0x69A7, 0x69D5), (0x69D6, 0x6A05), (0x6A06, 0x6A2F), (0x6A30, 0x6A65), (0x6A66, 0x6AB3), (0x6AB4, 0x6AF5), (0x6AF6, 0x6B28), (0x6B29, 0x6B57), (0x6B58, 0x6B80), (0x6B81, 0x6BA1), (0x6BA2, 0x6BCE), (0x6BCF, 0x6C33), (0x6C34, 0x6C5C), (0x6C5D, 0x6C79), (0x6C7A, 0x6C93)
brinstarObjectDoorEnemiesNum = 47
brinstarObjectDoorEnemies = []

offsetIndex = 0
odePtrs = []
for offsets in brinstarObjectDoorEnemyPointers:
	start = offsets[0]
	end = offsets[1]
	roomNumBytes = end - start
	odePtrs.append((start, end))
	data = fileContent[start:end]
	roomData = struct.unpack("B" * roomNumBytes, data)

	room = Room()
	room.unpackRoom(offsetIndex, roomData)
	brinstarObjectDoorEnemies.append(room)

	offsetIndex += 1

printBrinstarRoom(9)

brinstarMemDiff = zones[ZoneType.BRINSTAR].memoryDiff()

#hexdumpval = 0x19DB0 #- zoneMemoryOffsets["brinstar"]
#dasmval = 0x9Da0

#print ()

#room9addr = 0x65C9
#room9size = 0x23
#data = fileContent[room9addr : room9addr + room9size]
#room9bytes = struct.unpack("B" * room9size, data)
#print ("Number 9:", " ".join(["%02x" % x for x in room9bytes]))




#print ("Macros:")
#currentAddr = macrosOffset
#for b in macros:
#	if currentAddr % 4 == 0:
#		print ("\n%04X: " % (currentAddr), end="")
#	print ("%02X " % b, end="")
#	currentAddr += 1
#print("")

# brinstar structure data is normally between 6C94 and 6EFF
room9structOffset = brinstarStructurePointers[9]
room9numBytes = brinstarStructurePointers[10] - room9structOffset
room9structBytes = fileContent[room9structOffset + 1 : room9structOffset + room9numBytes - 1]

print("room9 structure bytes: %d" % room9numBytes)
brinstarMacros = macroDefs[ZoneType.BRINSTAR]["table"] 

room9macros = {}
print("macros:")
i = 0
for structByte in room9structBytes:
	macroIndex = structByte * 4
	macroValues = brinstarMacros[macroIndex : macroIndex + 4]
	print (("[%x] [%02x] tiles: [" % (i, structByte)), (", ".join(["%02X" % x for x in macroValues])), "]")
	room9macros[structByte] = macroValues
	i += 1



# TILES

# According to gfx disassembly, the brinstar tiles should be at 0x9DA0, but a hexdump shows the 
# same data actually in the rom file on address 0x19DB0
# So add this to addresses below to find actual data:
gfxOffset = 0x10010


# addresses from disassembly
samusAndGearPatternsStart 		= 0x8000
samusAndGearPatternsEnd 		= 0x89A0

introAndEndTilePatternsStart 	= 0x89A0
introAndEndTilePatternsEnd 		= 0x8AA0

titleScreenTilePatternsStart 	= 0x8BE0
titleScreenTilePatternsEnd 		= 0x90E0

suitlessSamusTilePatternsStart 	= 0x90E0
suitlessSamusTilePatternsEnd 	= 0x98F0

exclamationPointTileStart 		= 0x9890
exclamationPointTileEnd 		= 0x98A0

brinstarRoomTilePatternsStart 	= 0x9DA0
brinstarRoomTilePatternsEnd 	= 0xA6F0

norfairRoomTilePatternsStart 	= 0xA6F0
norfairRoomTilePatternsEnd 		= 0xA9C0

tourianRoomTilePatternsStart 	= 0xA9C0
tourianRoomTilePatternsEnd 		= 0xB4B0

fontsTilePatternsStart 			= 0xB4C0
fontsTilePatternsEnd 			= 0xB8C0


addr = brinstarRoomTilePatternsStart + gfxOffset
numTileBytes = brinstarRoomTilePatternsEnd - brinstarRoomTilePatternsStart

#addr = samusAndGearPatternsStart + gfxOffset
#numTileBytes = fontsTilePatternsEnd - samusAndGearPatternsStart


unpackedTiles = unpackTiles(addr, numTileBytes)


#room9tiles = [[25] * 32] * 30
#print(room9tiles)

scale = 2


WIDTH = 256 	# in original pixels = 32 8px tiles
HEIGHT = 240 	# in original pixels = 30 8px tiles


WINDOW_WIDTH = WIDTH * scale
WINDOW_HEIGHT = HEIGHT * scale

# window is actually displayed as 1024x960 on my osx, probably due to some "smart GUI scaling"

pygame.init()
#print(pygame.display.Info())

pygame.display.init()
screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT], SWSURFACE | DOUBLEBUF)

#print("Window should have size %d x %d" % (WINDOW_WIDTH, WINDOW_HEIGHT))
#print("And get: ", screen.get_size())
#print("wm: ", pygame.display.get_wm_info())

tileLength = 8
tileSize = (tileLength, tileLength)

blitTileScale = scale 

tileLengthScaled = tileLength * blitTileScale
tileSizeScaled = (tileLengthScaled, tileLengthScaled)

blitSource = pygame.Surface(tileSizeScaled)
blitDestBase = pygame.Rect((0,0), tileSizeScaled)

colorBackground = Color("brown")

shouldRenderMap = True

room9objectsEtc = brinstarObjectDoorEnemies[9].getRoomObjects()
#print(room9objectsEtc)


room9tiles = []
for y in range(30):
	row = []
	for x in range(32):
		row.append(0)
	room9tiles.append(row)

	#print(room9tiles)

	#room9tiles[  y  ][  x  ] = macroBase
	#room9tiles[  y  ][x + 1] = macroBase + 1
	#room9tiles[y + 1][  x  ] = macroBase + 2
	#room9tiles[y + 1][x + 1] = macroBase + 3

printBrinstarStructure(9)


#i = 11
#room9tiles[3][0] = 0xff
#room9tiles[  10  ][  10  ] = i + 3
#room9tiles[  10  ][10 + 1] = i + 2
#room9tiles[10 + 1][  10  ] = i + 1
#room9tiles[10 + 1][10 + 1] = i

#print(room9tiles)
#sys.exit()
	#print ("obj %x at tile (%d,%d)" % (obj[1], x, y))



while 1:
	for event in pygame.event.get():
		if event.type == QUIT:
			sys.exit(0)

	screen.fill(Color("blue"))

	if shouldRenderMap:
		tileIndex = 0
		s = ""
		for y in range(30):
			for x in range(32):

				# draw tile at position (x, y)

				# 1. find tile to draw

				# top-left, top-right, bottom-left, and bottom-right

				tileIndex = room9tiles[y][x]

				s += "%02x " % tileIndex

				#m = room9macros[0x8]

				#mBase = (1 * 16) + 5
				#m = [mBase, mBase + 1, mBase + 2, mBase + 3]

				#if   x == 10 and y == 10:		tileIndex = m[0]
				#elif x == 11 and y == 10:		tileIndex = m[1]
				#elif x == 10 and y == 11:		tileIndex = m[2]
				#elif x == 11 and y == 11:		tileIndex = m[3]
				#else:							continue

				#print("[%d][%d] = 0x%x" % (x, y, tileIndex))
				#xm = x % 2
				#ym = y % 2
				
				#topLeft 	= (xm == 0 and ym == 0)
				#bottomLeft 	= (xm == 0 and ym == 1)
				#topRight 	= (xm == 1 and ym == 0)
				#bottomRight	= (xm == 1 and ym == 1)

				#if topLeft:
				#	tileIndex = m[0]
				#elif bottomLeft:
				#	tileIndex = m[1]
				#elif topRight:
				#	tileIndex = m[2]
				#else:
				#	tileIndex = m[3]


				# room9tiles[y][x]

				#for b in room9structBytes:
				#	i = b * 4
				#	macroValues = brinstarMacros[i : i + 4]
				#	print ((" [%02x] tiles: [" % b), (", ".join(["%02X" % x for x in macroValues])), "]")
				#	room9macros[b] = macroValues


				#print("tile: %d" % tileIndex)

				if tileIndex >= len(unpackedTiles):
					#print("tileIndex=0x%x out of bounds!" % tileIndex)
					#tileIndex = 0
					continue

				if tileIndex == 0:
					#tileIndex = 1
					continue


				# 2. find pixels for tile
				tile = unpackedTiles[tileIndex]


				# 3. clear surface used for tile drawing
				blitSource.fill(colorBackground)
				
				# 4. draw the tile
				drawTile(tile, blitSource)
				blitDest = blitDestBase.move(x * tileLengthScaled, y * tileLengthScaled)
				
				# 5. update screen buffer
				screen.blit(blitSource, blitDest)
			s += "\n"

		print(s)

	else:
		screen.fill(colorBackground)
		blitSource.fill(Color("blue"))
		blitDest = blitDestBase.move(100, 100)
		screen.blit(blitSource, blitDest)

	# 6. redraw
	pygame.display.flip()
	pygame.time.delay(500)


