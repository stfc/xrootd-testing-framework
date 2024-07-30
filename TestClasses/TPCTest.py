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
        super().__init__()
        self.srcServer = None
        self.destinServer = None
        self.siteA = None #{'CEPH-SVC16':['ceph-svc16.gridpp.rl.ac.uk', 'dteam:/test/tst.txt']} # Defaults if no config file? 
        self.siteB = None #{'GOLIAS100': ['golias100.farm.particle.cz', 'dpm/farm.particle.cz/home/dteam/test/tst.txt']}
        self.checksums = []
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp', 'args', '--tpc', 'delegate', 'only', 'siteA', 'src', 'siteB', 'dest'], 
                                       'gfal': ['gfal-copy', 'siteA', 'src', 'siteB', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'siteB', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'siteB', 'dest', 'ADLER32']},  
                        'delete'    : {'xrd' : ['xrdfs', 'siteB', 'args', 'dest'], 
                                       'gfal': ['gfal-rm', 'siteB', 'dest']},          
                        'load'      : {'xrd' : ['xrdcp','siteA', 'src', 'siteB', 'dest', '-d1', '--force'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', '-v', 'args']}                  
                        }
        
        #Reading config file for sites
        if configFile is not None:
            with open(configFile) as config:
                try:
                    sites = yaml.safe_load(config)
                    self.timeout = str(sites['TIMEOUT'])
                    self.siteA = sites['TEST_ENDPOINT']
                    self.siteB = {**sites['UK_SITE'], **sites['NON_UK_SITE']}

                except yaml.YAMLError as exc:
                    print(exc)


    def subprocess(self, action:str, sourceBaseNm=None, destinBaseNm=None, *args, TestAll=False):
        #Get the file path from the dict and concat with BaseNms to get source and destin paths
        # But setup here shouldn't assign sourcePath and destinPath 
    
        self.setup(action, None, None, *args)
        self.groupedOutput = []
        self.checksums = []

        if TestAll == False:
            key, value = random.choice(list(self.siteA.items()))
            self.siteA = {key : value}

        if action == 'load': self.siteB = self.redirect

        for uksite, uksiteVal in self.siteA.items():

            # If copy, Transfer an initial file named tst.txt to siteA:
            if self.action == 'copy' or self.action == 'load':
                setupSrc = '../TestData/'+sourceBaseNm
                setupDst = 'root://'+uksiteVal[0]+':'+str(self.port)+'//'+uksiteVal[1]+sourceBaseNm
                setupCmd = ['xrdcp', setupSrc, setupDst, '--force']
                subprocess.run(setupCmd, capture_output=True, text=True)
                print("Initial file transferred")

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

                    # print("\n FULL CMD:", self.action, cmdAB)
                    # print("\n FULL CMD:", self.action, cmdBA)

                    outputAB = subprocess.run(cmdAB, capture_output=True, text=True) # Runs the commands and obtains output
                    outputBA = subprocess.run(cmdBA, capture_output=True, text=True)
                    returnAB = (outputAB.returncode, outputAB.stdout, outputAB.stderr)
                    returnBA = (outputBA.returncode, outputBA.stdout, outputBA.stderr)

                    # print("\n", returnAB, "\n", returnBA)

                    self.groupedOutput.extend([(returnAB, returnBA)])

                    if action == "checksum": # Handles stdout to obtain the checksum values
                        checksumPair = []
                        for output in [outputAB, outputBA]:
                            if output.returncode == 0:
                                checksum = output.stdout.split(" ")[1].strip('\n')
                            else:
                                checksum = None
                            checksumPair.append(checksum)
                        self.checksums.append(tuple(checksumPair))
                      

                    # outputs = (0, 'success', '') #Temporary Dummy Values
                    # self.groupedOutput.append(outputs)

                    # if action == "checksum": #Temporary Dummy checksums
                    #     srcsum = '32c10641'
                    #     destsum = '32c10641'
                    #     self.checksums.append((srcsum, destsum))
        
        if action == "checksum":
            return self.checksums
        else:
            return self.groupedOutput
        

    def timed(self, action:str, sourceBaseNm=None, destinBaseNm=None, *args, reps=5, TestAll=False):

        self.setup(action, None, None, *args)
        self.groupedOutput = []
        self.checksums = []

        if TestAll == False:
            key, value = random.choice(list(self.siteA.items()))
            self.siteA = {key : value}

        for uksite, uksiteVal in self.siteA.items():

            # If copy, Transfer an initial file named tst.txt to siteA:
            if self.action == 'copy' or self.action == 'load':
                setupSrc = '../TestData/'+sourceBaseNm
                setupDst = 'root://'+uksiteVal[0]+':'+str(self.port)+'//'+uksiteVal[1]+destinBaseNm
                setupCmd = ['xrdcp', setupSrc, setupDst, '--force']
                subprocess.run(setupCmd, capture_output=True, text=True)
                print("Initial file transferred")

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


                    timesAB = []
                    timesBA = []
                    for i in range(reps): # This could be a separate method?
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

                    self.groupedOutput.extend([returnAB, returnBA])

        return self.groupedOutput


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




        #Matrix has been setup
        #tpc will use more or less the same cmds, just with -T/--tpc
        #and the src is also the same format as dest

        #A combination of root+endpoint will need to be made,
        #Then compared?
    
    
    #TPC tests need to do a test for storage types
    #i.e. dcache, xrootd, other server
    #And needs to be tested against atleast one non-UK site
    #and one for each network type (end-points) LHCOne + LHCOPN
    #A -> B, A aka sourcePath should always be RAL site (Ceph?)
    # Lancaster, Glasgow or LCP(?)
    # Set up in config file - param that has UK site which can be changed as different end-points are introduced

    #A should be a UK site
    #B should be a non-UK site

    #TPC_UK site
        #transfer test_endpoint UK_SITE <- defined in config file
        #UK_SITE=ceph-c04.glasgow.ac.uk
        #code loads config file, gets the endpoint and performs tests by loading from there
        #LHCONE_SITE
        #LHCOPN

    #We will also be using all sites' supported protocols here too
    #Pick which sites to transfer against - should be able to run DAVS/HTTPS and ROOT
    #DAVS is a variant of HTTPS
    #Test will always be against the endpoint being tested against one UK site 
    #Config file - can put in the option to be able to test against every UK site (put as a list/dict) or just pick a random site
    # dictionary 
    #For arbitrary site, i.e. TPC-specific site variable can be defined





    # Parallelisation options in Jenkins - or Python multi-threading
    # Can look at multiprocessing in python 
    # Local instance of Jenkins - if it is accessible to web interface
        # i.e. host IP, it is using my system resource
    
    # In meeting, people can give input too to things they'd like to see
    #Can update on which test cases I'm testing, and if there's any specific tests to be included

    #Iterate over a list of protocols + endpoints
    #These endpoints will be the LHCOne + LHCOPN + external sites
    #Unlike the other, these will be done for all sites except ceph
    #The ceph/RAL site will be the source
    #Will still test all protocols???