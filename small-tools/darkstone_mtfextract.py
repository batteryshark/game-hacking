'''
Darkstone MTF extractor.

Usage: python3 darkstone_mtfextract.py DATA.MTF

Unpacks into the current directory. Layout: uint32 file count, then per file
a length-prefixed name, uint32 offset and uint32 size. Entries are copied
out as stored.
'''
import os
import sys
import struct


fp = open(sys.argv[1],"rb")
fileSize = os.path.getsize(sys.argv[1])

numfilestr = struct.unpack_from("I",fp.read(4))
numfiles = numfilestr[0]
print("Numfiles: %d"%numfilestr[0])
for x in range(0,numfiles):
	strlenstr = struct.unpack("I",fp.read(4))
	strlen = strlenstr[0]
	filestr = bytes(fp.read(strlen))
	filestr = filestr.decode()
	fileoffsetd = struct.unpack("I",fp.read(4))
	filesized = struct.unpack("I",fp.read(4))
	fileoffset = fileoffsetd[0]
	filesize = filesized[0]
	print("File ",x," Name:",filestr," Offset: ",fileoffsetd[0]," Size:",filesized[0])
	# Names in the archive use backslashes; create the folders they imply.
	outpath = os.path.join(*filestr.rstrip(' \t\r\n\0').split('\\'))
	outdir = os.path.dirname(outpath)
	if(outdir != "" and os.path.exists(outdir) != True):
		os.makedirs(outdir)
	outfile = open(outpath,"wb")
	curpos = fp.tell();
	fp.seek(fileoffset,0)
	buff = fp.read(filesize)
	outfile.write(buff)
	outfile.close()
	fp.seek(curpos,0)
	
print("DONE!")
