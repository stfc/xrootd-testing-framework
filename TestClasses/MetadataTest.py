#!/usr/bin/env python3
import struct
import sys
import zlib
from BaseTest import BaseTest
import subprocess

class MetadataTest(BaseTest):
    def __init__(self, configFile=None):
        super().__init__(configFile)
        self.fileName = None
        self.fileType = None
        self.fileSize = None
        self.fileLocation = None
        self.fileAuthor = None
        self.chksmFormat = []
        self.toolCategories = {'xrd' : ['Path:', 'Id:', 'Size:', 'MTime:', 'CTime:', 'ATime:', 'Flags:', 'Mode:', 'Owner:', 'Group:'],
                               'gfal': ['File:', 'Size:', 'Access:', 'Access:', 'Modify:', 'Change:']}

        self.basecmd['stat'] = {'xrd' : ['xrdfs', 'endpoint', 'stat', 'dest'], 
                                'gfal': ['gfal-stat', 'endpoint', 'dest', 'args']} # Addition of 'stat' as an action for metadata tests


    def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, timeout, *args)
        
        for site, siteVal in self.config['SITES'].items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                fullCmd = self.parse(self.basecmd[self.action][tool], endpoint, self.destinPath+ext, self.args)
                if self.timeout is not None:
                    fullCmd = ['timeout', str(self.timeout)] + fullCmd
                
                Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)

                self.outputHandle(Testprocess, tool)
        
        return self.results[self.action]


    def outputHandle(self, Testprocess, tool):       

        if self.action == "checksum":
            if Testprocess.returncode == 0:
                checksum = Testprocess.stdout.split(" ")[1].strip('\n')
                print("Checksum:", checksum)
                endian = self.is_big_endian(self.sourcePath, checksum)

            else:
                checksum = None
                endian = 'No format match'
            
            self.results[self.action].append((checksum, endian))
            
        else:
            statResult = Testprocess.stdout.splitlines()
            categories = []
            for data in statResult:
                entry = list(data.split())
                if entry != []:
                    categories.append(entry[0])

            outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr, 
                    categories, self.toolCategories[tool])
            self.results[self.action].append(outputs)

        return

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
    

    def is_big_endian(self, localFile, destsum):

        # Adler32 checksum of local file:
        localHexsum = int(self.xrdadler32(localFile), 16)

        # Convert localSum to big endian
        bigEndiansum = struct.pack('>I', localHexsum).hex()

        # Convert localSum to little endian
        littleEndiansum = struct.pack('<I', localHexsum).hex()


        if destsum == bigEndiansum:
            return 'BigEndian'
        elif destsum == littleEndiansum:
            return 'LittleEndian'
        else:
            return 'No format match'


