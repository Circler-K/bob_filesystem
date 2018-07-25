import struct
import sys
def read_sectors(fd, sector,count =  1):
	fd.seek(sector*512) # 섹터에 512를 곱하는 이유는 섹터의 크기가 512이라서인가 그리고  섹터는 0부터 시작이다.
	tmp_data = fd.read(count*512)
	return tmp_data

def chk_end_part(tmp_data):
	for i in tmp_data:
		if i != 0x00:
			return 0
	return 1

def main():
	f = open("gpt_128.dd","rb")
	f.seek(2*512)
	while(1):
		partition_dat = f.read(128)
		if chk_end_part(partition_dat):
			print("END")
			exit(0)
		first_LBA = struct.unpack_from("<I",partition_dat,32)[0]
		last_LBA = struct.unpack_from("<I",partition_dat,40)[0]
		print("===================================")
		print(first_LBA)
		print(last_LBA-first_LBA+1)

if __name__ == '__main__':
	main()