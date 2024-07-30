#!/usr/bin/env python3
import struct
import sys
import zlib
from BaseTest import BaseTest
import subprocess


class MetadataTest(BaseTest):
    def __init__(self):
        super().__init__()
        self.fileName = None
        self.fileType = None
        self.fileSize = None
        self.fileLocation = None
        self.fileAuthor = None

        self.chksmFormat = []

        self.toolCategories = {'xrd' : ['Path:', 'Id:', 'Size:', 'MTime:', 'CTime:', 'ATime:', 'Flags:', 'Mode:', 'Owner:', 'Group:'],
                               'gfal': ['File:', 'Size:', 'Access:', 'Access:', 'Modify:', 'Change:']}

        self.basecmd = {'stat'      : {'xrd' : ['xrdfs', 'endpoint', 'stat', 'dest'], 
                                       'gfal': ['gfal-stat', 'endpoint', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'endpoint', 'query', 'checksum', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'endpoint', 'dest', 'ADLER32']}                            
                        }


    def subprocess(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, *args)
        self.groupedOutput = []
        self.checksums = []
        
        for site, siteVal in self.sitesList.items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd

                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                fullCmd = self.parse(self.basecmd[self.action][tool], endpoint, self.destinPath+ext, self.args)
                if timeout is not None:
                    fullCmd = timeout + fullCmd

                # print("Full Command:", fullCmd)
                
                Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)
            
                statResult = Testprocess.stdout.splitlines()
                categories = []
                for data in statResult:
                    entry = list(data.split())
                    if entry != []:
                        categories.append(entry[0])
        

                outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr, 
                           categories, self.toolCategories[tool])
                self.groupedOutput.append(outputs)       

                if action == "checksum":
                    if Testprocess.returncode == 0:
                        checksum = Testprocess.stdout.split(" ")[1].strip('\n')
                        endian = self.is_big_endian(self.sourcePath, checksum)
                        
                    else:
                        checksum = None
                        endian = 'No format match'
                    
                    self.checksums.append((checksum, endian))
        
        if action == "checksum":
            return self.checksums
        else:
            return self.groupedOutput



    def parse(self, struc, endpoint, dest, args=None):
        finalCmd = [struc[0]]
        strucTmp = iter(struc[1:])

        for idx, item in enumerate(strucTmp):
            if item in locals().keys() and locals()[item] is not None:
                if item == 'endpoint' and struc[idx+2] == 'dest':
                    fullPath = endpoint + '//' + dest
                    finalCmd.append(fullPath)
                    next(strucTmp)
                elif item == 'args':
                    [finalCmd.append(arg) for arg in args]
                else:
                    finalCmd.append(locals()[item])
            elif item not in locals().keys() and isinstance(item, str):
                finalCmd.append(item)
            else:
                continue

        return finalCmd
    

    def is_big_endian(self, origFile, checksum):
        with open(origFile, 'rb') as f:
            fileContent = f.read()
        computed_checksum = zlib.crc32(fileContent)
   
        big_endiansum = struct.pack('>I', computed_checksum)
        little_endiansum = struct.pack('<I', computed_checksum)

        bytesum = bytes.fromhex(str(checksum))

        if checksum == big_endiansum:
            return 'BigEndian'
        elif checksum == little_endiansum:
            return 'LittleEndian'
        else:
            return 'No format match'


# Main metadata is stat and checksum
# Additional metadata is things like flags but are mostly irrelevent
# Flags aren't relevant in our use-case, used when transferring data from tape 
# You have a staging process between copy from pc/data centre into local disk cache (mostly echo)
# The file is then written from echo to tape pre-writing pool, then into physical tape

# Read test is specifically for the data in the file being 

# Metadata test can be called
