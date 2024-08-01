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

class ReadWriteTest(BaseTest, PerformanceTest):
    def __init__(self, configFile=None, singleEndPoint=None, singleProt:list=None):
        super().__init__(configFile)
        self.groupedOutput = []
        self.checksums = []
        
        if singleEndPoint is not None:
            self.sitesList = singleEndPoint
        if singleProt is not None:
            self.protocols = singleProt
            
    
    def genScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, timeout, *args)

        #Read-write tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. Otherwise the protocol we use is gfal-copy
        #create a combination of each protocol, server and root (i.e. a 'scenario')
        
        for site, siteVal in self.config['SITES'].items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                # Command changes depending on self.action
                fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                if self.timeout is not None:
                    fullCmd = ['timeout', str(self.timeout)] + fullCmd

                print("Full cmd:", fullCmd)
                continue
                
                Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)
                self.outputHandle(Testprocess)

        return self.results[self.action]
        

    def outputHandle(self, Testprocess):
       
        if self.action == "checksum":
            if Testprocess.returncode == 0:
                checksum = Testprocess.stdout.split(" ")[1].strip('\n')
            else:
                checksum = None
            self.results[self.action].append(checksum)
            
        else:
            outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr)
            self.groupedOutput.append(outputs)
            self.results[self.action].append(outputs)
        
        return


    def genTimedScenarios(self, action:str, sourcePath=None, destinBaseNm=None, *args, reps=5, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, timeout, *args)
                      
        for site, siteVal in self.config['SITES'].items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                if self.timeout is not None:
                    fullCmd = self.timeout + fullCmd
                self.timeOutputHandle(reps, fullCmd)

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