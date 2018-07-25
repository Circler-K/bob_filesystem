import struct
import sys

def main():
	global current_sector, current_sector_size,f, ebr_start_sector
	filename = "mbr_128.dd"
	f = open(filename,"rb")
	current_sector = 0
	data = read_sectors(f,current_sector)
	if chk_mbr_sign(data) != 1:
		print("이 파티션은 MBR이 아님")

	partition_dat = data[446:446+64]
	table1 = partition_dat[0:16]
	table2 = partition_dat[16:32]
	table3 = partition_dat[32:48]
	table4 = partition_dat[48:64] # EBR시작주소 여기서 부터는 다시 짜야한다. ㅎㅎ

	print_table_entry(table1)
	print_table_entry(table2)
	print_table_entry(table3) 
	current_sector = struct.unpack_from("<I",table4,8)[0]
	ebr_start_sector = current_sector
	parse_EBR_entry()

def read_sectors(fd, sector,count =  1):
	fd.seek(sector*512)
	# 섹터에 512를 곱하는 이유는 섹터의 크기가 512이라서인가 그리고  섹터는 0부터 시작이다.
	tmp_data = fd.read(count*512)
	return tmp_data

def chk_mbr_sign(tmp_data):
	# MBR이면 1 아니면 0
	if tmp_data[-2] != 0x55 and tmp_data[-1] != 0xAA:
		print("이 파티션은 MBR이 아님")
		return 0
	return 1

def chk_ebr_end(data_list):
	for i in data_list:
		if i != 0x00:
			return 0
	return 1

def print_table_entry(table):
	print("================================")
	print("starting LBA :",struct.unpack_from("<I",table,8)[0],"* 512 =",struct.unpack_from("<I",table,8)[0]*512," and HEX is",hex(struct.unpack_from("<I",table,8)[0]*512))
	print("size :",struct.unpack_from("<I",table,12)[0],"* 512 =",512*struct.unpack_from("<I",table,12)[0])

def parse_EBR_entry():
	global current_sector, current_sector_size,f, ebr_start_sector
	data = read_sectors(f,current_sector)
	if chk_mbr_sign(data) != 1:
		print("이 파티션은 MBR이 아님")

	partition_dat = data[446:446+64]
	table1 = partition_dat[0:16]
	table2 = partition_dat[16:32]
	table3 = partition_dat[32:48]
	table4 = partition_dat[48:64] # EBR시작주소 여기서 부터는 다시 짜야한다. ㅎㅎ
	if chk_ebr_end(table2):
		print("================================")
		print("starting LBA :",current_sector+ struct.unpack_from("<I",table1,8)[0],"* 512 =",(current_sector+ struct.unpack_from("<I",table1,8)[0])*512," and HEX is",hex((current_sector+ struct.unpack_from("<I",table1,8)[0])*512))
		print("size :",struct.unpack_from("<I",table1,12)[0],"* 512 =",512*struct.unpack_from("<I",table1,12)[0])
		print("END EBR")
		exit(0)

	print("================================")
	print("starting LBA :",current_sector+ struct.unpack_from("<I",table1,8)[0],"* 512 =",(current_sector+ struct.unpack_from("<I",table1,8)[0])*512," and HEX is",hex((current_sector+ struct.unpack_from("<I",table1,8)[0])*512))
	print("size :",struct.unpack_from("<I",table1,12)[0],"* 512 =",512*struct.unpack_from("<I",table1,12)[0])
	current_sector = ebr_start_sector + struct.unpack_from("<I",table2,8)[0]
	print(current_sector)
	parse_EBR_entry()

if __name__ == '__main__':
	main()



'''
import sys
import os
import struct

def process_image(f,sectors):
        f.seek(sectors * 512)
        data = f.read(512)
        partition = data[446:446+64]

        table = [ partition[0:16] , partition[16:32],partition[32:48],partition[48:64]]
 
        for i in range(0,4):
                if table[i][4] == 0:
                        return 0;
                if table[i][4] == 7:
                        print("=======================================")
                        print("Starting LBA : ", (sectors + struct.unpack_from("<I", table[i], 8)[0])*512)
                        print("size : ", struct.unpack_from("<I", table[i], 12)[0] * 512)
                if table[i][4] == 5:
                        return process_image(f,sectors + struct.unpack_from("<I", table[i], 8)[0])
                        

filename = 'mbr_128.dd'
f = open(filename,"rb")
process_image(f,0)
print('================================')


#  ㅓ베이스 포인터를 기준으로 움직인다.

'''