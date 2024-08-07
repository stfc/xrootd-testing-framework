#!/usr/bin/env python3
import asyncio
import struct
import sys
import zlib
from BaseTest import BaseTest
import subprocess

class MetadataTest(BaseTest):
    def __init__(self, configFile=None):
        super().__init__(configFile)
        self.chksmFormat = []
        self.toolCategories = {'xrd' : ['Path:', 'Id:', 'Size:', 'MTime:', 'CTime:', 'ATime:', 'Flags:', 'Mode:', 'Owner:', 'Group:'],
                               'gfal': ['File:', 'Size:', 'Access:', 'Access:', 'Modify:', 'Change:']}

        self.basecmd['stat'] = {'xrd' : ['xrdfs', 'endpoint', 'stat', 'dest'], 
                                'gfal': ['gfal-stat', 'endpoint', 'dest', 'args']} # Addition of 'stat' as an action for metadata tests


    async def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.cmds = self.genCmds(action, sourcePath, destinBaseNm, *args, timeout=timeout)
            
        tasks = [asyncio.create_task(self._run_cmd(cmd)) for cmd in self.cmds]

        await asyncio.gather(*tasks)

        return self.results[self.action]
        
    async def _run_cmd(self, cmd):
        # get tool from cmd:
        if 'gfal' in cmd[1]:
            tool = 'gfal'
        else:
            tool = 'xrd'

        Testprocess = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await Testprocess.communicate()
        await self.outputHandle(Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip(), tool)
        
        return

    async def outputHandle(self, returncode, stdout, stderr, tool):       
        
        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1].strip('\n')
                print("Checksum:", checksum)
                endian = self.is_big_endian(self.sourcePath, checksum)

            else:
                checksum = None
                endian = 'No format match'
            
            self.results[self.action].append((checksum, endian))
            
        else:
            statResult = stdout.splitlines()
            categories = []
            for data in statResult:
                entry = list(data.split())
                if entry != []:
                    categories.append(entry[0])

            outputs = (returncode, stdout, stderr, 
                    categories, self.toolCategories[tool])
            self.results[self.action].append(outputs)

        return

    def parse(self, struc, src, endpoint, dest, args=None):
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


