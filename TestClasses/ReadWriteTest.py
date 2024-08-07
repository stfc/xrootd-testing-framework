#!/usr/bin/env python3
import sys
import yaml
from BaseTest import BaseTest
from PerformanceTest import PerformanceTest
import subprocess
import os
import time
import numpy as np
from zlib import adler32
import memory_profiler
import asyncio

class ReadWriteTest(BaseTest, PerformanceTest):
    def __init__(self, configFile=None, singleEndPoint=None, singleProt:list=None):
        super().__init__(configFile)
        self.groupedOutput = []
        self.checksums = []
        
        if singleEndPoint is not None:
            self.sitesList = singleEndPoint
        if singleProt is not None:
            self.protocols = singleProt
        

    async def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.cmds = self.genCmds(action, sourcePath, destinBaseNm, *args, timeout=timeout)
        
        tasks = [asyncio.create_task(self._run_cmd(cmd)) for cmd in self.cmds]

        await asyncio.gather(*tasks)
        
        return self.results[self.action]
        

    async def _run_cmd(self, cmd):
        Testprocess = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await Testprocess.communicate()
        await self.outputHandle(Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip())
        
        return

    async def outputHandle(self, returncode, stdout, stderr):
       
        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1].strip('\n')
            else:
                checksum = None
            self.results[self.action].append(checksum)
            
        else:
            outputs = (returncode, stdout, stderr)
            self.results[self.action].append(outputs)
        
        return


    def genTimedScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, reps=5, timeout=None):
        self.cmds = self.genCmds(action, sourcePath, destinBaseNm, *args, timeout=timeout)
            
        for cmd in self.cmds:
            self.timeOutputHandle(reps, cmd)

        return self.results[self.action]
    
    
    def timeOutputHandle(self, reps, fullCmd):
        times = []
        for i in range(reps): # no. repetitions is configurable 
            initialTime = time.time()
            Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)
            endTime = time.time()

            timeTot = endTime - initialTime
            times.append(timeTot)
        
        avgTime = float(np.mean(np.array(times)))
        fileSize = os.stat(self.sourcePath).st_size

        outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr, avgTime, fileSize)
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


    def adler32sum(self, filepath):
        BLOCKSIZE = 256*1024*1024
        asum = 1
        with open(filepath, 'rb') as f:
            while (data := f.read(BLOCKSIZE)):
                # print('read len:', len(data))
                asum = adler32(data, asum)
        return asum