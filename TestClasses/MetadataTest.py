#!/usr/bin/env python3
import asyncio
import os
import struct
import sys
import zlib
from BaseTest import BaseTest
import subprocess

class MetadataTest(BaseTest):
    def __init__(self, configFile=None, createFiles=False, root=True, https=True, davs=True):
        super().__init__(configFile, createFiles, root=root, https=https, davs=davs)
        self.toolCategories = {'xrd' : ['Path:', 'Id:', 'Size:', 'MTime:', 'CTime:', 'ATime:', 'Flags:', 'Mode:', 'Owner:', 'Group:'],
                               'gfal': ['File:', 'Size:', 'Access:', 'Access:', 'Modify:', 'Change:']}
        del self.basecmd['load']
        del self.basecmd['readv']
        self.basecmd['stat'] = {'xrd' : ['xrdfs', 'endpoint', 'stat', 'dest'], 
                                'gfal': ['gfal-stat', 'endpoint', 'dest', 'args']} # Addition of 'stat' as an action for metadata tests


    ''' Checks inputs for MetadataTest.genScenarios within BaseTest.setup method (Override)'''
    def _handle_inputs(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, gfalArgs=None, reps=None):
        if action not in self.basecmd.keys():
            raise ValueError(f'"{action}" is not a valid action')
        elif action=='copy':
            if sourcePath is None:
                raise ValueError('Please provide a sourcePath')
        elif action=='delete':
            if reps is not None:
                if sourcePath is None:
                    raise ValueError('Please provide a sourcePath for timed deletion')
            else:
                if sourcePath is not None:    
                    raise ValueError('Action "delete" does not take sourcePath as argument')
                if destinBaseNm is None:
                    raise ValueError('Please provide a destinBaseNm')
        elif action=='checksum':
            if sourcePath is None:
                raise ValueError('Please provide a sourcePaths')
            if destinBaseNm is None:
                raise ValueError('Please provide a destinBaseNms')
        elif action=='bulk-copy':
            if sourcePath is None:
                raise ValueError('Please provide one or more sourcePaths')
        elif action=='bulk-delete':
            if reps is not None:
                if sourcePath is None:
                    raise ValueError('Please provide one or more sourcePaths for timed deletions')
            else:
                if sourcePath is not None:
                    raise ValueError('Action "bulk-delete" does not take sourcePath as argument')
                if destinBaseNm is None:
                    raise ValueError('Please provide one or more destinBaseNms')
    
        return

    ''' Calls method to setup, generate and asynchronously run commands, and format the outputs. Returns dictionary of results'''
    async def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, timeout=None,  XROOTD_ECHO=False, INT_MANAGER=False):
        self._genCmds(action=action, sourcePath=sourcePath, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, timeout=timeout, XROOTD_ECHO=XROOTD_ECHO, INT_MANAGER=INT_MANAGER)
        self._store_local_file_bytes()
        
        if XROOTD_ECHO or INT_MANAGER is True:
            tasks = [await self._run_cmd_sync(idx) for idx in range(len(self.cmds))]
        else:
            tasks = [asyncio.create_task(self._run_cmd(idx)) for idx in range(len(self.cmds))]
            await asyncio.gather(*tasks)

        await self.outputHandle()
        self._teardown()

        return self.results[self.action]
        
    ''' Runs each command, passes output to self.outputHandle'''
    async def _run_cmd(self, idx):
        # get tool from cmd:
        if 'gfal' in self.cmds[idx]['cmd'][2]:
            tool = 'gfal'
        else:
            tool = 'xrd'

        tempFiles = await self._gen_file_copy(idx, self.cmds[idx]['localFileCopy'])

        Testprocess = await asyncio.create_subprocess_exec(
        *self.cmds[idx]['cmd'],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
            
        stdout, stderr = await Testprocess.communicate()

        returncode, stdout, stderr = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip()                        
        await self.outputHandle(idx, returncode, stdout, stderr, tool)
        await self._del_file_copy(idx, tempFiles, self.cmds[idx]['localFileCopy'])
        
        return
    
    ''' Formats and processes output based on the action type'''
    async def outputHandle(self, idx=None, returncode=None, stdout=None, stderr=None, tool=None):
        # Process the results keys as a whole rather than by idx
        if idx is None: 
            # Group the output checksums according to the length of self.destinBaseNm
            if self.action == 'checksum' and len(self.destinBaseNm)> 1:
                grp = len(self.destinBaseNm)            
                cmdOuts = [tuple(self.results[self.action]['cmdOuts'][i:i + grp]) for i in range(0, len(self.results[self.action]['cmdOuts']), grp)]
                checksums = [tuple(self.results[self.action]['destsums'][i:i + grp]) for i in range(0, len(self.results[self.action]['destsums']), grp)]

                self.results[self.action]['cmdOuts'] = tuple(cmdOuts)
                self.results[self.action]['destsums'] = tuple(checksums)
            return

        self.results[self.action]['IDs'][idx] = self.cmds[idx]['IDs']
        
        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1].strip('\n')
                for localFile in self.sourcePath:
                    endian = self.is_big_endian(localFile, checksum)

            else:
                checksum = None
                endian = 'No destination checksum to compare'
            self.results[self.action]['destsums'][idx] = (checksum, endian)
            outputs = stderr

        elif self.action == 'stat':
            statResult = stdout.splitlines()
            categories = []
            for data in statResult:
                entry = list(data.split())
                if entry != []:
                    categories.append(entry[0])

            outputs = (returncode, stdout, stderr, 
                    categories, self.toolCategories[tool])
        else:
            outputs = (returncode, stdout, stderr)

        # Storing the source file(s) checksum(s)
        if self.sourcePath is not None and 'srcsums' in self.results[self.action].keys():
            srcsums = [] 
            lenSrc = len(self.sourcePath) # Skips checksumming transfer.txt file if present
            for localFile in self.cmds[idx]['localFileCopy'][:lenSrc]:
                srcsum = self.xrdadler32(localFile)
                srcsums.append(srcsum)
            if len(srcsums) == 1:
                self.results[self.action]['srcsums'][idx] = srcsums[0]
            else:
                self.results[self.action]['srcsums'][idx] = tuple(srcsums)

            
        self.results[self.action]['cmdOuts'][idx] = outputs

        return
        
    ''' Converts checksum of local file to big and little endian, compares both to destination file's checksum to determine type'''
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


