#!/usr/bin/env python3
from functools import wraps
import re
import sys
from BaseTest import BaseTest
import subprocess
import os
import time
import numpy as np
from zlib import adler32
import asyncio

class ReadWriteTest(BaseTest):
    def __init__(self, configFile=None, createFiles=False, root=True, https=True, davs=True):
        super().__init__(configFile, createFiles, root=root, https=https, davs=davs)       
        
    ''' Calls method to setup, generate and asynchronously run commands, and format the outputs. Returns dictionary of results'''    
    async def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs):
        self._genCmds(action=action, sourcePath=sourcePath, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, timeout=timeout, XROOTD_ECHO=XROOTD_ECHO, INT_MANAGER=INT_MANAGER, **readvArgs)
        self._store_local_file_bytes()

        if action == 'load' and XROOTD_ECHO or INT_MANAGER is True:
            tasks = [await self._run_cmd_sync(idx) for idx in range(len(self.cmds))]
        else:
            tasks = [asyncio.create_task(self._run_cmd(idx, **readvArgs)) for idx in range(len(self.cmds))]
            await asyncio.gather(*tasks)
        
        await self.outputHandle()

        self._vector_read_src(**readvArgs) # Runs only if action = readv
        self._teardown() 
        
        return self.results[self.action]
        
    ''' Runs each command, passes output to self.outputHandle'''
    async def _run_cmd(self, idx, **readvArgs): #running each command: create the local copy:
        # print(f"Command {idx}: {self.cmds[idx]['cmd']}")

        # When action is readv, perform a vector read using XrdClient
        if self.action == 'readv':
            returncode, stdout, stderr = self._vector_read_dest(self.cmds[idx]['cmd'], **readvArgs)
            await self.outputHandle(idx, returncode, stdout, stderr, **readvArgs)
            return

        # Otherwise, run the command using subprocess
        tempFiles = await self._gen_file_copy(idx, self.cmds[idx]['localFileCopy'])

        Testprocess = await asyncio.create_subprocess_exec(
        *self.cmds[idx]['cmd'],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
            
        stdout, stderr = await Testprocess.communicate()

        returncode, stdout, stderr = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip()                        
        await self.outputHandle(idx, returncode, stdout, stderr)
        await self._del_file_copy(idx, tempFiles, self.cmds[idx]['localFileCopy'])
        
        return

    ''' Formats and processes output based on the action type'''
    async def outputHandle(self, idx=None, returncode=None, stdout=None, stderr=None, **readvArgs):
        
        # Process the entire results as a whole rather than by idx
        if idx is None: 
            # Group the output checksums according to the length of self.destinBaseNm
            if self.action == "checksum" and len(self.destinBaseNm)> 1:
                grp = len(self.destinBaseNm)            
                cmdOuts = [tuple(self.results[self.action]['cmdOuts'][i:i + grp]) for i in range(0, len(self.results[self.action]['cmdOuts']), grp)]
                checksums = [tuple(self.results[self.action]['destsums'][i:i + grp]) for i in range(0, len(self.results[self.action]['destsums']), grp)]

                self.results[self.action]['cmdOuts'] = tuple(cmdOuts)
                self.results[self.action]['destsums'] = tuple(checksums)

            elif self.action == 'bulk-copy' and len(self.sourcePath)> 1:
                grp = len(self.sourcePath)
                cmdOuts = [tuple(self.results[self.action]['cmdOuts'][i:i + grp]) for i in range(0, len(self.results[self.action]['cmdOuts']), grp)]
                self.results[self.action]['cmdOuts'] = tuple(cmdOuts)
            return


        self.results[self.action]['IDs'][idx] = self.cmds[idx]['IDs']

        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1]
            else:
                checksum = None
            self.results[self.action]['destsums'][idx] = checksum
            outputs = stderr

        elif self.action == "load":
            stdout, stderr, redirSites = self._load_output(idx, stdout, stderr)
            outputs = (returncode, stdout, stderr)
            self.results[self.action]['redirects'][idx] = tuple(redirSites)
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

    ''' Parses the verbose output from load/redirection and returns list of sites that operation was redirected to'''
    def _load_output(self, idx, stdout, stderr, cmd=None):
        if cmd is None:
            cmd = self.cmds[idx]['cmd']
        redirSites = []
        if 'xrdcp' in cmd:
            outputs = stderr.splitlines()
            for i in range(len(outputs)):
                if 'Redirect trace-back:' in outputs[i] and 'Redirected from:' in outputs[i+1]:
                    redirsite = outputs[i+1].split('://')
                    redirsite = redirsite[-1].split(':')[0]
                    redirSites.append(redirsite)
        
                elif 'Close returned from localhost with:' in outputs[i]:
                    stderr = outputs[i]
                elif 'Destroying MsgHandler:' in outputs[i]:
                    stderr = outputs[i:i+3]
                
        elif 'gfal-copy' in cmd:
            outputs = stdout.splitlines()
            for i in range(len(outputs)):
                if 'HTTP/1.1 307 Temporary Redirect' in outputs[i] and 'Location:' in outputs[i+4]:
                    redirsite = outputs[i+4].split('://')
                    redirsite = redirsite[-1].split(':')[0]
                    redirSites.append(redirsite)
                else:
                    continue
            stdout = outputs[-4:-1]
        
        return stdout, stderr, redirSites

    ''' Calls method to setup, generate and asynchronously run timed repetitions of commands, and format the outputs. Returns dictionary of results'''
    async def genTimedScenarios(self, action:str, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=3, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs):
        self._genCmds(action=action, sourcePath=sourcePath, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, reps=reps, timeout=timeout, XROOTD_ECHO=XROOTD_ECHO, INT_MANAGER=INT_MANAGER, **readvArgs)
        self._store_local_file_bytes()

        if action == 'load' and XROOTD_ECHO or INT_MANAGER is True:
            tasks = [await self._run_timed_cmd(reps, idx) for idx in range(len(self.cmds))]
        else:
            tasks = [asyncio.create_task(self._run_timed_cmd(reps, idx, **readvArgs)) for idx in range(len(self.cmds))]
            await asyncio.gather(*tasks)

        await self.timeOutputHandle()

        self._vector_read_src(**readvArgs) # Runs only if action = readv
        self._teardown()
     
        return self.results[self.action]
        
    ''' Used to run a single timed repetition of a command. Returns subprocess outputs and timeTaken'''
    async def _run_single_cmd(self, reps, idx, times, r, **readvArgs):

        # When action is readv, perform a vector read using XrdClient
        if self.action == 'readv':
            initialTime = time.time()
            returncode, stdout, stderr = self._vector_read_dest(self.cmds[idx]['cmd'][r], **readvArgs)
            endTime = time.time()
            
        # Otherwise, use subprocess to run the command
        else:

            initialTime = time.time()

            Testprocess = await asyncio.create_subprocess_exec(
            *self.cmds[idx]['cmd'][r],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
                
            stdout, stderr = await Testprocess.communicate()
            endTime = time.time()
            
        timeTaken = endTime - initialTime
        returncode, stdout, stderr = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip() 

        return returncode, stdout, stderr, timeTaken
        
    ''' Asynchronously runs the repetitions (_run_single_cmd) of the current command, obtains the average time, and passes outputs to self.timeOutputHandle'''
    async def _run_timed_cmd(self, reps, idx, **readvArgs):
        times = np.full(reps, np.nan)
        tempFiles = await self._gen_file_copy(idx, self.cmds[idx]['localFileCopy']) 

        if self.action == 'load':
            results = [await self._run_single_cmd(reps, idx, times, r, **readvArgs) for r in range(reps)]

        else:
            tasks = [asyncio.create_task(self._run_single_cmd(reps, idx, times, r, **readvArgs)) for r in range(reps)]
            results = await asyncio.gather(*tasks)

        returncode, stdout, stderr = results[-1][0], results[-1][1], results[-1][2]
        for r in range(reps):
            timeTaken = results[r][3]
            times[r] = timeTaken
        
        avgTime = np.mean(times, dtype=np.float64)
    
        await self.timeOutputHandle(idx, reps, returncode, stdout, stderr, avgTime, **readvArgs)
        await self._del_file_copy(idx, tempFiles, self.cmds[idx]['localFileCopy'])
       
        return

    ''' Formats and processes output based on the action type for the timed outputs'''
    async def timeOutputHandle(self, idx=None, reps=None, returncode=None, stdout=None, stderr=None, avgTime=None, **readvArgs):

        # Process the entire results keys as a whole rather than by idx
        if idx is None: 
            # Group the output checksums according to the length of self.destinBaseNm
            if self.action == 'checksum' and len(self.destinBaseNm)> 1:
                grp = len(self.destinBaseNm)            
                checksums = [tuple(self.results[self.action]['destsums'][i:i + grp]) for i in range(0, len(self.results[self.action]['destsums']), grp)]
                cmdOuts = [tuple(self.results[self.action]['cmdOuts'][i:i + grp]) for i in range(0, len(self.results[self.action]['cmdOuts']), grp)]

                self.results[self.action]['destsums'] = tuple(checksums)
                self.results[self.action]['cmdOuts'] = tuple(cmdOuts)

            elif self.action == 'bulk-copy' and len(self.sourcePath)> 1:
                grp = len(self.sourcePath)
                cmdOuts = [tuple(self.results[self.action]['cmdOuts'][i:i + grp]) for i in range(0, len(self.results[self.action]['cmdOuts']), grp)]
                self.results[self.action]['cmdOuts'] = tuple(cmdOuts)

            return
        
        self.results[self.action]['IDs'][idx] = self.cmds[idx]['IDs']

        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1]
            else:
                checksum = None
            self.results[self.action]['destsums'][idx] = checksum
            outputs = stderr

        elif self.action == "load":
            stdout, stderr, redirSites = self._load_output(idx, stdout, stderr, cmd=self.cmds[idx]['cmd'][-1])
            outputs = (returncode, stdout, stderr, avgTime)
            self.results[self.action]['redirects'][idx] = tuple(redirSites)
        else:
            outputs = (returncode, stdout, stderr, avgTime)
   
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


   
    