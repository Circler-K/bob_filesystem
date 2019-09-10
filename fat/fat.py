'''
FAT32 파일 시스템을 분석해서 루트 디렉토리의 디렉토리 목록을 출력하는 파서를 만드시오

지난 과제를 제출한 Github에 FAT32 폴더를 만들고 fat32.py 를 추가하시오

1] 입력
- FAT32 DD 이미지

2] 디렉토리 목록 출력 결과
name : lfn 이 있으면 롱파일 네임 없으면 sfn의 이름을 쓰시오. 인코딩해서 출력해야 합니다.
Lfn 항목 자체는 출력되지 않고 연관된 sfn에 이름만 바꿔줘야 합니다.
출력항목 이름 파일 디렉토리 여부 시작 클러스터(상위하위 합쳐서) 파일사이즈, 지워졋는지 여부
실제로 Fat 테이블을 읽어서 처리해야 합니다

4] 제출 포맷 
제목 [BOB7] 제품보안 이름_github.

제출했다고 메일을 작성하시오 GitHub 링크를 보내주세요

5] 제출일자

8/9일 00시 까지
'''
import sys
import codecs
import struct

def bin2hex(binarr):
    return bytes(binarr).hex()
def hex2str(hex_str,encode):
    hx = codecs.decode(hex_str,"hex")
    return codecs.decode(hx,encode)

def read_sector(fd, sector, BytesPerSector=512 , count=1):
    fd.seek(sector*BytesPerSector)
    return fd.read(count*BytesPerSector)

#file_name = sys.argv[1]
file_name = "fat32_2.dd"

filesystem = open(file_name,"rb")

data = read_sector(filesystem,0)

if data[-2] != 0x55 and data[-1] != 0xAA:
    print("부트레코드가 아닙니다.")

partition_header = data


SectorPerCluster = struct.unpack_from("<B",partition_header,13)[0] #B는 unsigned char
RootDirCluster =  struct.unpack_from("<I",partition_header,44)[0]

BytesPerSector = struct.unpack_from("<H",partition_header,11)[0] #H는 unsigned short
ReservedSector = struct.unpack_from("<H",partition_header,14)[0]
NumberOfFat32 = struct.unpack_from("<B",partition_header,16)[0]
Fat32Size =  struct.unpack_from("<I",partition_header,36)[0]


RootDirSector = (ReservedSector + Fat32Size*NumberOfFat32)
RootDir = read_sector(filesystem,RootDirSector,BytesPerSector,SectorPerCluster)

LFN = []
for i in range(16*SectorPerCluster):

    DirEntry = RootDir[i*32:(i+1)*32]
    EntryAttr = DirEntry[11]

    if EntryAttr ==0x0F:
        LFN.insert(0,bin2hex(DirEntry[1:11]) + bin2hex(DirEntry[14:26]) + bin2hex(DirEntry[28:32]))
        LFN[0] = hex2str( LFN[0],"utf-16-le").replace("\uffff","")
    elif EntryAttr != 0x00:
        FileName = "?" + hex2str(bin2hex(DirEntry[2:8]), "euc-kr") if DirEntry[0] == 0xe5 else hex2str(bin2hex(DirEntry[0:8]), "euc-kr")
        FileName = FileName.strip()
        if DirEntry[0]==0xe5:
            print("[지워짐]",end="")
        if EntryAttr & 0x10:
            print("[폴더]",end="")
        if EntryAttr & 0x20:
            print("[파일]", end="")
            FileName = FileName.strip() + "." + hex2str(bin2hex(DirEntry[8:11]), "euc-kr")
            filesize = struct.unpack_from("<I",DirEntry,28)[0]
            print("[파일사이즈:%d]"%(filesize),end="")

        LongName = ''.join(LFN)
        FileName = FileName if len(FileName[2:-2]) > len(LongName) else LongName


        print(FileName,end=" ")

        if EntryAttr & 0x01:
            print("[읽기전용]",end="")
        if EntryAttr & 0x02:
            print("[숨겨짐]",end="")
        if EntryAttr & 0x04:
            print("[운영체제]",end="")
        if EntryAttr & 0x08:
            print("[볼륨레이블]",end="")
        
        FChigh = struct.unpack_from("<H",DirEntry,20)[0]*256
        FClow = struct.unpack_from("<H",DirEntry,26)[0]
        print("[시작 클러스터 : %s]"%(FChigh+FClow))
        LFN=[]
        print("\n")
    else:
        break

