#!/usr/bin/env python3
import sys
import time
import numpy as np
from BaseTest import BaseTest
import yaml
import random
import subprocess
import os

class TPCTest(BaseTest):
    def __init__(self, configFile):
        super().__init__(configFile)
        self.srcServer = None
        self.destinServer = None
        self.siteB = {**self.config['UK_SITE'], **self.config['NON_UK_SITE']}
        self.timeout = str(self.config['TIMEOUT'])
        self.checksums = []
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp', 'args', '--tpc', 'delegate', 'only', 'siteA', 'src', 'siteB', 'dest'], 
                                       'gfal': ['gfal-copy', 'siteA', 'src', 'siteB', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'siteB', 'query', 'checksum', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'siteB', 'dest', 'ADLER32']},  
                        'delete'    : {'xrd' : ['xrdfs', 'siteB', 'args', 'dest'], 
                                       'gfal': ['gfal-rm', 'siteB', 'dest']},          
                        'load'      : {'xrd' : ['xrdcp','siteA', 'src', 'siteB', 'dest', '-d1', '--force', '--tpc', 'delegate', 'only'], 
                                       'gfal': ['gfal-copy', 'siteA', 'src', 'siteB', 'dest', '-v', 'args']}                  
                        }
        

    def genScenarios(self, action:str, sourceBaseNm=None, destinBaseNm=None, *args, TestAll=False):

        self.setup(action, None, None, self.timeout, *args)

        if TestAll == False:
            key, value = random.choice(list(self.config['TEST_ENDPOINT'].items()))
            self.config['TEST_ENDPOINT'] = {key : value}

        for uksite, uksiteVal in self.config['TEST_ENDPOINT'].items():

            # If self.action = copy, Transfer an initial file named tst.txt to siteA(s):
            if self.action == 'copy' or self.action == 'load':
                self.transferInitFile(sourceBaseNm, uksiteVal)

            for extsite, extsiteVal in self.siteB.items():
                for prot in self.protocols:

                    tool = self.cmds[prot]
                    # if tool == 'gfal': # remove line later
                    #     continue

                    siteA = prot + uksiteVal[0] + ':' + str(self.port)
                    siteB = prot + extsiteVal[0] + ':' + str(self.port)

                    sourcePath = uksiteVal[1] + sourceBaseNm
                    destinPath = extsiteVal[1] + destinBaseNm

                    cmdAB = ['timeout', self.timeout] + self.parse(self.basecmd[self.action][tool], siteA, sourcePath, siteB, destinPath+'_ab', self.args)
                    siteA, siteB, sourcePath, destinPath = siteB, siteA, destinPath, sourcePath
                    cmdBA = ['timeout', self.timeout] + self.parse(self.basecmd[self.action][tool], siteA, sourcePath+'_ab', siteB, destinPath+'_ba', self.args)
                
                    # print("TIMEOUT:", self.timeout, "CmdAB:", cmdAB, "\n CmdBA:", cmdBA)
                    # continue

                    outputAB = subprocess.run(cmdAB, capture_output=True, text=True) # Runs the commands and obtains output
                    outputBA = subprocess.run(cmdBA, capture_output=True, text=True)
                    
                    self.outputHandle(outputAB, outputBA)                    
        
        return self.results[self.action]
        

    def outputHandle(self, outputAB, outputBA):
       
        if self.action == "checksum": # Handles stdout to obtain the checksum values
            checksumPair = []
            for output in [outputAB, outputBA]:
                if output.returncode == 0:
                    checksum = output.stdout.split(" ")[1].strip('\n')
                else:
                    checksum = None
                checksumPair.append(checksum)
            self.results[self.action].append(checksumPair)
        else:
            returnAB = (outputAB.returncode, outputAB.stdout, outputAB.stderr)
            returnBA = (outputBA.returncode, outputBA.stdout, outputBA.stderr)
            self.results[self.action].extend([(returnAB, returnBA)])
        
        return
    

    def genTimedScenarios(self, action:str, sourceBaseNm=None, destinBaseNm=None, *args, reps=5, TestAll=False):

        self.setup(action, None, None, self.timeout, *args)

        if TestAll == False:
            key, value = random.choice(list(self.config['TEST_ENDPOINT'].items()))
            self.config['TEST_ENDPOINT'] = {key : value}

        for uksite, uksiteVal in self.config['TEST_ENDPOINT'].items():

            # If copy, Transfer an initial file named tst.txt to siteA:
            if self.action == 'copy' or self.action == 'load':
                self.transferInitFile(sourceBaseNm, uksiteVal)

            for extsite, extsiteVal in self.siteB.items():
                for prot in self.protocols:

                    tool = self.cmds[prot]
                   
                    siteA = prot + uksiteVal[0] + ':' + str(self.port)
                    siteB = prot + extsiteVal[0] + ':' + str(self.port)

                    sourcePath = uksiteVal[1] + sourceBaseNm
                    destinPath = extsiteVal[1] + destinBaseNm

                    cmdAB = ['timeout', self.timeout] + self.parse(self.basecmd[self.action][tool], siteA, sourcePath, siteB, destinPath+'_ab', self.args)

                    siteA, siteB, sourcePath, destinPath = siteB, siteA, destinPath, sourcePath
                    cmdBA = ['timeout', self.timeout] + self.parse(self.basecmd[self.action][tool], siteA, sourcePath+'_ab', siteB, destinPath+'_ba', self.args)

                    # print("cmds:", cmdAB, "\n", cmdBA)
                    # continue

                    self.timeOutputHandle(reps, cmdAB, cmdBA, sourceBaseNm)

        print(self.results[self.action])
        return self.results[self.action]
    
    
    def timeOutputHandle(self, reps, cmdAB, cmdBA, sourceBaseNm):
        timesAB = []
        timesBA = []
        for i in range(reps):
            # print("\n RUNNING SET", i)
            initialTimeAB = time.time()
            outputAB = subprocess.run(cmdAB, capture_output=True, text=True)
            endTimeAB = time.time()

            initialTimeBA = time.time()
            outputBA = subprocess.run(cmdBA, capture_output=True, text=True)
            endTimeBA = time.time()

            timeTotAB = endTimeAB - initialTimeAB
            timeTotBA = endTimeBA - initialTimeBA

            timesAB.append(timeTotAB)
            timesBA.append(timeTotBA)

        avgTimeAB = float(np.mean(np.array(timesAB)))
        avgTimeBA = float(np.mean(np.array(timesBA)))

        fileSize = os.stat('../TestData/'+sourceBaseNm).st_size

        returnAB = (outputAB.returncode, outputAB.stdout, outputAB.stderr, avgTimeAB, fileSize)
        returnBA = (outputBA.returncode, outputBA.stdout, outputBA.stderr, avgTimeBA, fileSize)

        self.results[self.action].extend([returnAB, returnBA])

        return


    def parse(self, struc, siteA, src, siteB, dest, args=None):
        finalCmd = [struc[0]]
        strucTmp = struc[1:]
        idx = 0

        while idx < len(strucTmp):
            item = strucTmp[idx]
            if idx < len(strucTmp)-1:
                nextItem = struc[1:][idx+1]
            
            if item in locals().keys() and locals()[item] is not None:
                if item == 'siteA' and nextItem == 'src':
                    fullPath = siteA + '//' + src
                    finalCmd.append(fullPath)
                    idx += 1
                    
                elif item == 'siteB' and nextItem == 'dest':
                    fullPath = siteB + '//' + dest
                    finalCmd.append(fullPath)
                    idx += 1
                    
                elif item == 'args':
                    [finalCmd.append(arg) for arg in args]
                
                else:
                    finalCmd.append(locals()[item])
                
                idx += 1

            elif item not in locals().keys() and isinstance(item, str):
                finalCmd.append(item)
                idx += 1
            else:
                idx += 1

        return finalCmd


    def transferInitFile(self, sourceBaseNm, ukSite):
        setupSrc = '../TestData/'+sourceBaseNm
        setupDst = 'root://'+ukSite[0]+':'+str(self.port)+'//'+ukSite[1]+sourceBaseNm
        setupCmd = ['xrdcp', setupSrc, setupDst, '--force']
        # subprocess.run(setupCmd, capture_output=True, text=True)
        print("Initial file transferred:", setupCmd)
        
        return