'''
	BFPKTool - A 'packed' format utility for Castlevania: Lords of Shadow 1/2
									2014 - rFx

	Usage: python3 BFPKTool.py d target.packed

	Version 3 archives have an AES-256-CBC encrypted file table. The key is
	not part of this file: put it, as 64 hex digits, in the BFPK_V3_KEY
	environment variable. Reading version 3 also needs pycryptodome.
'''

PROJECT_VERSION = 0.75
import io,os,sys,struct,zlib,binascii

def usage():
	print("Usage: %s d target.packed" % sys.argv[0])
	exit(1)

def fatal(msg):
	print(msg)
	exit(1)

BFPK_VERSION = {
	0:"RAW",
	1:"ZLIB",
	2:"MULTI_ZLIB",
	3:"ENCRYPTED"

}

def get_v3_key():
	key_hex = os.environ.get("BFPK_V3_KEY","")
	try:
		key = binascii.unhexlify(key_hex)
	except (binascii.Error,ValueError):
		key = b""
	if(len(key) != 32):
		fatal("This archive has an encrypted file table. Set BFPK_V3_KEY to the 32-byte key as 64 hex digits.")
	return key

def gen_file_table(f,num_files,version):
	curr_file = 0
	file_table = []
	while curr_file < num_files:
		#Read size of file path.

		fname_sz = struct.unpack("<I",f.read(4))[0]

		fname = f.read(fname_sz).decode("ascii").replace("\\","/")

		file_size = struct.unpack("<I",f.read(4))[0]
		file_offset = struct.unpack("<I",f.read(4))[0]
		if(version != "ENCRYPTED" and version != "ENCRYPTED_RAW"):
			deleted = struct.unpack("<I",f.read(4))[0]
		else:
			deleted = 0
		curr_file +=1
		file_table.append({"path":fname,"offset":file_offset,"size":file_size,"deleted":deleted})
	return file_table


def dump_packed_file(inpath):
	print("Dumping %s..." % inpath)
	f = open(inpath,"rb")
	magic = f.read(4)

	if(magic != b"BFPK"):
		fatal("%s is not a valid BPFK file." % inpath)

	version = struct.unpack("B",f.read(1))[0]

	if(not version in BFPK_VERSION.keys()):
		fatal("%s has an unsupported archive version." % inpath)

	version = BFPK_VERSION[version]
	version_alt = struct.unpack("B",f.read(1))[0]
	if(version == "MULTI_ZLIB" and version_alt == 0):
		version = "ENCRYPTED_RAW"
	padding = f.read(2)
	if(version == "ENCRYPTED" or version == "ENCRYPTED_RAW"):
		#Decrypt File Table
		from Crypto.Cipher import AES
		ftable_sz = struct.unpack("<I",f.read(4))[0]
		ftable_iv = f.read(16)
		file_table_bin = f.read(ftable_sz)
		aes = AES.new(get_v3_key(), AES.MODE_CBC, ftable_iv)
		file_table_bin = aes.decrypt(file_table_bin)
		num_files = struct.unpack("<I",file_table_bin[:4])[0]
		file_table = gen_file_table(io.BytesIO(file_table_bin[4:]),num_files,version)

	else:
		if(version == "MULTI_ZLIB"):
			max_page_size = struct.unpack("<I",f.read(4))[0]
		num_files = struct.unpack("<I",f.read(4))[0]
		file_table = gen_file_table(f,num_files,version)
	#Make Root Directory
	root_dir,root_ext = os.path.splitext(inpath)
	if(not os.path.exists(root_dir)):
		os.makedirs(root_dir)

	#Process File table
	for cf in file_table:
		print("%s" % cf["path"])
		# Deleted entries do not point to valid payload data.
		if(cf["deleted"] == 1):

			continue
		parent_dir,fname = os.path.split(cf["path"])
		if(parent_dir != ""):
			if(not os.path.exists(os.path.join(root_dir,parent_dir))):
				os.makedirs(os.path.join(root_dir,parent_dir))
		g = open(os.path.join(root_dir,cf["path"]),"wb")
		f.seek(cf["offset"],0)
		if(version == "RAW" or version == "ENCRYPTED_RAW"):
			g.write(f.read(cf["size"]))
		if(version == "ZLIB" or version == "ENCRYPTED"):
			comp_sz = struct.unpack("<I",f.read(4))[0]
			g.write(zlib.decompress(f.read(comp_sz)))
		if(version == "MULTI_ZLIB"):
			total_chunks_sz = struct.unpack("<I",f.read(4))[0]
			curr_offset = 0
			while(curr_offset < total_chunks_sz):
				comp_sz = struct.unpack("<I",f.read(4))[0]
				g.write(zlib.decompress(f.read(comp_sz)))
				#We can't count the compressed size value.
				curr_offset += (comp_sz + 4)


		g.close()

	f.close()

if(__name__=="__main__"):
	print("BFPKTool v %s" % PROJECT_VERSION)
	if(len(sys.argv) != 3):
		usage()
	if(not os.path.exists(sys.argv[2])):
		usage()
	opcode = sys.argv[1]
	if(opcode == "c"):
		fatal("Creating archives was never implemented.")
	if(opcode != "d"):
		usage()

	dump_packed_file(sys.argv[2])
