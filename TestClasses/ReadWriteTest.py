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
        super().__init__()
        self.groupedOutput = []
        self.checksums = []

        if configFile is not None:
            with open(configFile) as config:
                try:
                    sites = yaml.safe_load(config)
                    self.sitesList = sites['SITES']
                except yaml.YAMLError as exc:
                    print(exc)
        
        if singleEndPoint is not None:
            self.sitesList = singleEndPoint
        if singleProt is not None:
            self.protocols = singleProt
        #sys.exit()

    
    def subprocess(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, *args)
        self.groupedOutput = [] # May not need this to be an instance/class variable
        self.checksums = []

        #Read-write tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. Otherwise the protocol we use is gfal-copy
        #create a combination of each protocol, server and root

        if action == 'load': self.sitesList = self.redirect
        if timeout is not None:
            timeout = ['timeout', str(timeout)]
        
        for site, siteVal in self.sitesList.items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                if timeout is not None:
                    fullCmd = timeout + fullCmd

                print("Full Command:", fullCmd, "\n Others:", endpoint, ext, self.destinPath)
                
                Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)

                outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr)
                self.groupedOutput.append(outputs)

                if action == "checksum":
                    if Testprocess.returncode == 0:
                        checksum = Testprocess.stdout.split(" ")[1].strip('\n')
                    else:
                        checksum = None
                    self.checksums.append(checksum)
        
        if action == "checksum":
            return self.checksums
        else:
            return self.groupedOutput

    def timed(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, *args)
        self.groupedOutput = [] # May not need this to be an instance/class variable
        self.checksums = []

        #Read-write tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. Otherwise the protocol we use is gfal-copy
        #create a combination of each protocol, server and root

        if action == 'load': self.sitesList = self.redirect
        if timeout is not None:
            timeout = ['timeout', str(timeout)]
        
        for site, siteVal in self.sitesList.items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.cmds[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                if timeout is not None:
                    fullCmd = timeout + fullCmd
                
                times = []    
                for i in range(5): # May make no. repetitions configurable 
                    initialTime = time.time()
                    Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)
                    endTime = time.time()

                    timeTot = endTime - initialTime
                    times.append(timeTot)
                
                avgTime = float(np.mean(np.array(times)))


                outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr, avgTime)
                self.groupedOutput.append(outputs)

                #print(self.groupedOutput)

        return self.groupedOutput


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
    
    def xrdadler32(self, filePath):
        cmd = ['/usr/bin/xrdadler32', os.path.expanduser(filePath)]
        Testprocess = subprocess.run(cmd, capture_output=True, text=True)     
        
        self.stdout = Testprocess.stdout
        self.stderr = Testprocess.returncode
        checksum = Testprocess.stdout.split(" ")[0]
        print('Output:', self.stdout, "Error:", self.stderr)
        
        return checksum