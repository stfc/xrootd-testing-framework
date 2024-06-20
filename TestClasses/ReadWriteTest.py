#!/usr/bin/env python3
import inspect
import re
from BaseTest import BaseTest
from PerformanceTest import PerformanceTest
import subprocess
import os
from zlib import adler32

class ReadWriteTest(BaseTest, PerformanceTest):
    def __init__(self):
        super().__init__()
        self.stdout = None
        self.stderr = None
        self.groupedOutput = []
    
    def subprocess(self):
        #Read-write tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. Otherwise the protocol we use is gfal-copy
        #Go through each item in the self.matrix & create a combination of each protocol, server and root
        for srvr in self.matrix[0]: #Iterate over protocols
            for items in self.matrix[1:]:
                for prot in items:
            
                    tool = self.cmds[prot] #e.g. tool=xrd
                    endpoint = prot + srvr + ':' + str(self.port)
                    ext = '_' + prot.strip(':/') + '_' + tool
                    #destinPath = self.destinPath + ext
                    print("NEW EXT:", self.destinPath+ext)

                    print("Input Args:", self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                    fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)

                    print("Full Command:", fullCmd)
                    Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)

                    outputs = (Testprocess.returncode, Testprocess.stdout, Testprocess.stderr)
                    self.groupedOutput.append(outputs)
                    print('Output:', self.stdout, "Error:", self.stderr, Testprocess.returncode)

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
        from zlib import adler32
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