'''
 CTD - Clocktower Text Dumper by rFx

 Usage: python3 cttd.py [CT_J.ADO [ct_txt.txt]]

 Writes one line per MSGOUT string: offset, original byte length, text.
 The text column is Shift-JIS, exactly as stored in the game minus padding.
'''

import os,sys,struct,binascii

ADO_FILENAME = sys.argv[1] if len(sys.argv) > 1 else "CT_J.ADO"
TXT_FILENAME = sys.argv[2] if len(sys.argv) > 2 else "ct_txt.txt"

f = open(ADO_FILENAME,"rb")
data = f.read()
f.close()
g = open(TXT_FILENAME,"wb")
for i in range(0,len(data)-1):
	if(data[i:i+2] == b'\x33\xff'):
		#We have to skip 6 because of the opcodes and values we don't care about changing.
		i+=6
		str_offset = i
		str_end = data[i:].index(b'\xff') -1
		newstr = data[i:i+str_end]
		strlen = len(newstr)
		newstr = newstr.replace(b"\x0a\x00",b"[NEWLINE]")
		#The game puts nulls after any ASCII character, we need to remove those.
		newstr = newstr.replace(b"\x00",b"")
		g.write(("%#x\t%d\t" % (str_offset,strlen)).encode("ascii"))
		g.write(newstr)
		g.write(b"\n")

g.close()
