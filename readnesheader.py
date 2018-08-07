import sys
import os.path
from INES import Header

if len(sys.argv) < 1:
	print("usage: readines.py rom-name")
	sys.exit(1)

romFileName = sys.argv[1]

if not os.path.exists(romFileName):
	print("usage: {0:s} romname.nes".format(sys.argv[0]))
	sys.exit(1)

fileContent = None
with open(romFileName, "rb") as file:
	fileContent = file.read()

if fileContent is None:
	print ("Failed to read {0:s}.nes".format(romFileName))
	sys.exit(0)


inesHeader = Header(fileContent)

print(inesHeader)
