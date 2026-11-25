'''
Clocktower Text Injector by rFx

Usage: python3 ctti.py [CT_J.ADO [CT_J.ADT [ct_txt_proc.txt [CT.ADO [CT.ADT]]]]]

Reads the original script pair and an edited text dump (same layout as the
one cttd.py writes), then writes a new CT.ADO with the replaced strings and
a new CT.ADT with every scene offset moved by the bytes gained or lost
before it.
'''
import os,sys,struct,binascii

def arg(n,default):
	return sys.argv[n] if len(sys.argv) > n else default

ADO_IN = arg(1,"CT_J.ADO")
ADT_IN = arg(2,"CT_J.ADT")
TXT_IN = arg(3,"ct_txt_proc.txt")
ADO_OUT = arg(4,"CT.ADO")
ADT_OUT = arg(5,"CT.ADT")

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

# ADT entries are not plain file offsets: every 0x8000 bytes of ADO data
# takes up 0x10000 of ADT address space.
def get_real_offset(offset):
	#Get High Value
	high_val = offset & 0xFFFF0000
	high_val //= 2
	low_val = offset & 0xFFFF
	return high_val+low_val
def get_fake_offset(offset):
	#Get High Value
	mult = int(offset / 0x8000)
	shft_val = 0x8000 * mult

	low_val = offset & 0xFFFF

	return offset + shft_val


f = open(ADO_IN,"rb")
data = f.read()
f.close()

offset_vals = []
f = open(TXT_IN,"rb")
lines = f.readlines()
f.close()
o,l,s = lines[0].split(b"\t",2)
first_offset = int(o,16)
newdata = data[:first_offset]

for i in range(0,len(lines)):
	line = lines[i]
	offset, osl, instr = line.split(b"\t",2)
	offset = int(offset,16)

	instr = instr.rstrip(b'\n')

	instr = instr.replace(b"[NEWLINE]",b"\x0a")
	#Fix the ASCII characters.
	instr = instr.decode("SHIFT-JIS")
	newstr = ""
	for char in instr:
		if(is_ascii(char)):
			newstr+=char+'\x00'
		else:
			newstr+=char
	instr = newstr
	instr = instr.encode("SHIFT-JIS")
	newstrlen = len(instr)
	osl = int(osl)
	strldiff = newstrlen - osl

	#Replace the data
	if(i < len(lines)-1):
		nextline = lines[i+1]
		nextoffset,nsl,nstr = nextline.split(b"\t",2)
		offset_vals.append({"offset":offset,"val":strldiff})
		nextoffset = int(nextoffset,16)

		newdata += instr+data[offset+osl:nextoffset]
	else:
		#End of last string to EOF
		offset_vals.append({"offset":offset,"val":strldiff})
		newdata += instr + data[offset+osl:]

#Write new ADO File.
g = open(ADO_OUT,"wb")
g.write(newdata)
g.close()

#Fix up the ADT file.
f = open(ADT_IN,"rb")
datat = f.read()
f.close()
g = open(ADT_OUT,"wb")

for i in range(0,len(datat),4):
	cur_offset = get_real_offset(struct.unpack("<I",datat[i:i+4])[0])
	final_adj = 0
	for offset in offset_vals:

		if(cur_offset > offset["offset"]):
			final_adj += offset["val"]
	g.write(struct.pack("<I",get_fake_offset(cur_offset + final_adj)))
g.close()
