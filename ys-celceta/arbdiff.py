# Prints different arb files, ignoring the header.
import os
import sys

if len(sys.argv) != 3:
	print("usage: python arbdiff.py <first-map-dir> <second-map-dir>")
	exit(1)

PATH_1 = sys.argv[1]
PATH_2 = sys.argv[2]
map_1 = {}
map_2 = {}

for root,dirs,files in os.walk(PATH_1):
	for f in files:
		if(f.endswith(".arb")):
			map_1[f] = os.path.join(root,f)
			
for root,dirs,files in os.walk(PATH_2):
	for f in files:
		if(f.endswith(".arb")):
			map_2[f] = os.path.join(root,f)
			
for fk in map_1.keys():
	f1 = map_1[fk]
	f2 = map_2[fk]
	f = open(f1,'rb')
	f.seek(0x14)
	data_1 = f.read()
	f.close()
	f = open(f2,'rb')
	f.seek(0x14)
	data_2 = f.read()
	if(data_1 != data_2):
		print(fk)
