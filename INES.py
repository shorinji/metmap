import struct

class Header:
	def __init__(self, fileContent):
		header = struct.unpack("B" * 16, fileContent[:16])
		formatTag = header[:4]
		if not (formatTag[0] == 0x4E and formatTag[1] == 0x45 and formatTag[2] == 0x53 and formatTag[3] == 0x1A):
			raise ValueError ("Invalid ROM file")

		self.prgRomSize = header[4]
		self.chrRomSize = header[5]
		self.chrRamSize = header[8]

	def __repr__(self):
		s = "Header:\n" 
		s += " PRG ROM size: %d x 16kB\n" % self.prgRomSize
		s += " CHR ROM size: %d x 8kB\n" % self.chrRomSize
		s += " CHR RAM size: %d x 8kB\n" % self.chrRamSize
		return s