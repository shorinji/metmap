import struct

class Header:
	def __init__(self, fileContent):
		header = struct.unpack("B" * 16, fileContent[:16])
		fingerprint = header[:4]
		if not (fingerprint[0] == 0x4E and fingerprint[1] == 0x45 and fingerprint[2] == 0x53 and fingerprint[3] == 0x1A):
			raise ValueError ("Invalid ROM file")

		self.prgRomSize = header[4]
		self.chrRomSize = header[5]
		self.flags6 = header[6]
		self.flags7 = header[7]
		self.chrRamSize = header[8]
		self.flags9 = header[9]
		self.flags10 = header[10]

		self.mapper = (self.flags7 & 0xF0) | (self.flags6 >> 4)



	def __repr__(self):
		s = "Header:\n" 
		s += " PRG ROM size: %d kB\n" % (self.prgRomSize * 16)
		s += " CHR ROM size: %d kB\n" % (self.chrRomSize * 8)
		s += " CHR RAM size: %d kB\n" % (self.chrRamSize * 8)

		mirroring = "vertical" if (self.flags6 & 1) else "horzontal"
		flags = ""
		if self.flags6 & 2:
			flags += "PRG-RAM"

		if self.flags6 & 4:
			flags += ", 512-byte trainer"
			numTrainers = 1
		else:
			numTrainers = 0

		if self.flags6 & 8:
			flags += ", Ignore Mirroring"

		s += "Flags6: (0x%x) mirroring:%s %s\n" % (self.flags6, mirroring, flags)

		flags = ""
		if self.flags7 & 1:
			flags += "VS Unisystem"

		if self.flags7 & 2:
			flags += ", PlayChoice-10"

		if self.flags7 & 4:
			flags += ", NES 2.0 format"

		s += "Flags7: (0x%x) %s\n" % (self.flags7, flags)

		tvSystem = "PAL" if (self.flags9 & 1) else "NTSC"
		s += ("Flags9: (0x%x) TV-system: %s\n" % (self.flags9, tvSystem))

		s += "Mapper: %d\n" % self.mapper

		prgRomStart = 16 + (numTrainers * 512)
		prgRomEnd = prgRomStart + (self.prgRomSize * 16384)
		s += "PRG-ROM starts at: 0x%04x\n" % prgRomStart
		s += "PRG-ROM ends at: 0x%04x\n" % prgRomEnd

		return s