#!/usr/bin/env python3
import asyncio
from fnmatch import fnmatch
import sys
import time
import numpy as np
from BaseTest import BaseTest
import yaml
import random
import subprocess
import os

# Make sure to update this so that you create a list of Nones for the results, and use the counter, and put the output in the correct spot
# Also make sure to add the testIDs thing here!!

class TPCTest(BaseTest):
    def __init__(self, configFile, createFiles=False, root=True, https=True, davs=True):
        super().__init__(configFile, createFiles, root=root, https=https, davs=davs)
        if "NON_UK_SITE" in self.config.keys():
            self.siteB = {**self.config['UK_SITE'], **self.config['NON_UK_SITE']}
        else:
            self.siteB = {**self.config['UK_SITE']}
        self.timeout = str(self.config['TIMEOUT'])
        self.checksums = []
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp',  '--tpc', 'delegate', 'only', 'siteA', 'src', 'siteB', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'siteA', 'src', 'siteB', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'siteB', 'query', 'checksum', 'dest'], 
                                       'gfal': ['gfal-sum', 'siteB', 'dest', 'ADLER32']},  
                        'delete'    : {'xrd' : ['xrdfs', 'siteB', 'rm', 'dest', 'args'], 
                                       'gfal': ['gfal-rm', 'siteB', 'dest', 'args']},                   
                        }
        
    ''' Checks that the correct required inputs are passed to TPCTest.genScenarios within BaseTest.setup method (Override) '''
    def _handle_inputs(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, gfalArgs=None, reps=None):
        if action not in self.basecmd.keys():
            raise ValueError(f'"{action}" is not a valid action')
        elif action=='copy':
            if sourcePath is None:
                raise ValueError('Please provide a sourcePath') # To transfer initial file
        elif action=='delete':
            if reps is not None:
                if sourcePath is not None:
                    raise ValueError('Action "delete" does not take sourcePath as argument')
            else:
                if sourceBaseNm is None:    
                    raise ValueError('Please provide a sourceBaseNm')
                if destinBaseNm is None:
                    raise ValueError('Please provide a destinBaseNm')
        elif action=='checksum':
            if sourcePath is not None:
                raise ValueError('Action "checksum" does not take sourcePath as argument')
            if destinBaseNm is None or sourceBaseNm is None:
                raise ValueError('Please provide a sourceBaseNm and destinBaseNm')   
        return
    
    ''' Generates and stores pairs of commands for siteA and siteB functionalities'''
    def _genCmds(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=None, TestAll=False, timeout=None):
        
        self.setup(action=action, sourcePath=sourcePath, sourceBaseNm=sourceBaseNm, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, reps=reps, timeout=timeout)
        
        if TestAll == False:
            key, value = random.choice(list(self.config['TEST_ENDPOINT'].items()))
            self.config['TEST_ENDPOINT'] = {key : value}

        if self.sourcePath is not None:
            self.cmds['initFileCmds'] = []

        for uksite, uksiteVal in self.config['TEST_ENDPOINT'].items():
            portA = self._check_port(self.config['TEST_ENDPOINT'][uksite])
            
            for extsite, extsiteVal in self.siteB.items():
                portB = self._check_port(self.siteB[extsite])

                for protocol in self.protocols:
                    self.cmds[self.count] = {'cmd': None, 'IDs': None}

                    tool = self.tools[protocol]
                    ext = f"_{protocol.strip('://')}_{tool}_{extsite}"

                    testID = f"{protocol.strip('/')}{uksite}-{extsite}-{destinBaseNm}"

                    siteA = f"{protocol}{uksiteVal[0]}:{portA}"
                    siteB = f"{protocol}{extsiteVal[0]}:{portB}"

                    sourcePath = f"{uksiteVal[1]}{sourceBaseNm}{ext}" 
                    destinPath = f"{extsiteVal[1]}{destinBaseNm}{ext}"

                    cmdAB = self._baseCmd_parse(self.basecmd[self.action][tool], siteA, sourcePath, siteB, destinPath+'_ab', reps, ext, isUKSite=True)
                    siteA, siteB, sourcePath, destinPath = siteB, siteA, destinPath, sourcePath
                    cmdBA = self._baseCmd_parse(self.basecmd[self.action][tool], siteA, sourcePath+'_ab', siteB, destinPath+'_ba', reps, ext)
                    
                    if reps is not None:
                        cmdPairs = tuple(zip(cmdAB, cmdBA))
                    else:
                        cmdPairs = (cmdAB, cmdBA)

                    self.cmds[self.count]['cmd'] = cmdPairs
                    self.cmds[self.count]['IDs'] = testID
                    
                    self.count+=1

        
        # Initialise results dictionary 
        if isinstance(self.results[self.action], dict):
            if 'initFileCmds' in self.cmds.keys():
                cmdsLength = len(self.cmds)-1
            else:
                cmdsLength = len(self.cmds)
            for key in self.results[self.action].keys():
                if key == 'IDs':
                    self.results[self.action]['IDs'] = [None]*cmdsLength
                else:
                    self.results[self.action][key] = [[] for x in range(cmdsLength)]        
        else:
            self.results[self.action] = [[] for x in range(cmdsLength)] 
        
        return


    ''' Calls method to setup, generate and asynchronously run commands, and format the outputs. Returns dictionary of results'''    
    async def genScenarios(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, TestAll=False, timeout=None):
        
        self._genCmds(action=action, sourcePath=sourcePath, sourceBaseNm=sourceBaseNm, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, TestAll=TestAll, timeout=timeout)
        self._store_local_file_bytes()

        # print("InitCmds:", self.cmds['initFileCmds'])
        # sys.exit()

        if self.sourcePath is not None:
            # Create the LocalFileCopies to be transferred to siteA
            genLocalFiles = [asyncio.create_task(self._gen_file_copy(fileCopyNms=self.cmds[k]['localFileCopy'])) for k in self.cmds.keys() if isinstance(k, int)]
            await asyncio.gather(*genLocalFiles)

            #Transfer the initial files to siteA
            transferInitFiles = [asyncio.create_task(self._transferInitFile(cmd)) for cmd in self.cmds['initFileCmds']]
            await asyncio.gather(*transferInitFiles)

            del self.cmds['initFileCmds']

            #Delete the LocalFileCopies from local machine
            delLocalCopies = [asyncio.create_task(self._del_file_copy(fileCopyNms=self.cmds[k]['localFileCopy'])) for k in self.cmds.keys() if isinstance(k, int)]
            await asyncio.gather(*delLocalCopies)


        tasks = [asyncio.create_task(self._run_cmd(idx)) for idx in range(len(self.cmds))]
        await asyncio.gather(*tasks)      

        self._teardown() 
        return self.results[self.action]
        
    ''' Runs each command in pair, passes output to self.outputHandle'''
    async def _run_cmd(self, idx):
        cmdPair = self.cmds[idx]['cmd']

        for cmd in cmdPair:
            Testprocess = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

            stdout, stderr = await Testprocess.communicate()
            returncode = Testprocess.returncode

            returncode, stdout, stderr = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip()
            await self.outputHandle(idx=idx, returncode=returncode, stdout=stdout, stderr=stderr)
       
        return
        
    ''' Formats and processes output based on the action type'''
    async def outputHandle(self, idx=None, returncode=None, stdout=None, stderr=None):
        
        self.results[self.action]['IDs'][idx] = self.cmds[idx]['IDs']

        if self.action == "checksum":
            if returncode == 0:
                checksum = stdout.split(" ")[1]
            else:
                checksum = None
            self.results[self.action]['destsums'][idx].append(checksum)
            outputs = stderr

        else:
            outputs = (returncode, stdout, stderr)
        
        self.results[self.action]['cmdOuts'][idx].append(outputs)
        return
    
    ''' Calls method to setup, generate and asynchronously run timed repetitions of commands, and format the outputs. Returns dictionary of results'''
    async def genTimedScenarios(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=3, TestAll=False, timeout=None):
        
        self._genCmds(action=action, sourcePath=sourcePath, sourceBaseNm=sourceBaseNm, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, reps=reps, timeout=timeout, TestAll=TestAll)
        self._store_local_file_bytes()

        if self.sourcePath is not None:
            # Create the LocalFileCopies to be transferred to siteA
            genLocalFiles = [asyncio.create_task(self._gen_file_copy(fileCopyNms=self.cmds[k]['localFileCopy'])) for k in self.cmds.keys() if isinstance(k, int)]
            await asyncio.gather(*genLocalFiles)

            #Transfer the initial files to siteA
            transferInitFiles = [asyncio.create_task(self._transferInitFile(cmd)) for cmd in self.cmds['initFileCmds']]
            await asyncio.gather(*transferInitFiles)

            del self.cmds['initFileCmds']
            #Delete the LocalFileCopies from local machine
            delLocalCopies = [asyncio.create_task(self._del_file_copy(fileCopyNms=self.cmds[k]['localFileCopy'])) for k in self.cmds.keys() if isinstance(k, int)]
            await asyncio.gather(*delLocalCopies)

        # Run the timed commands
        tasks = [asyncio.create_task(self._run_timed_cmd(cmdPairs=self.cmds[idx]['cmd'], reps=reps, idx=idx)) 
                 for idx in range(len(self.cmds))]
        await asyncio.gather(*tasks)

        self._teardown() 
        return self.results[self.action]
    
    ''' Runs each repetition of command pairs, computes average time taken for each command and passes output to timeOutputHandle'''
    async def _run_timed_cmd(self, cmdPairs, reps, idx=None):
        timesAB = []
        timesBA = []
        
        tasks = [asyncio.create_task(self._run_cmd_pair(cmdPairs[r][0], cmdPairs[r][1])) for r in range(reps)]
        results = await asyncio.gather(*tasks)

        for (resultAB, resultBA) in results:
            returncodeAB, stdoutAB, stderrAB, timeAB = resultAB
            returncodeBA, stdoutBA, stderrBA, timeBA = resultBA
            
            timesAB.append(timeAB)
            timesBA.append(timeBA)

        avgTimeAB = np.mean(np.array(timesAB), dtype=np.float64)
        avgTimeBA = np.mean(np.array(timesBA), dtype=np.float64)
       
        await self.timeOutputHandle(idx, reps, returncodeAB, stdoutAB, stderrAB, avgTimeAB)
        await self.timeOutputHandle(idx, reps, returncodeBA, stdoutBA, stderrBA, avgTimeBA)

        return
                    

    ''' Used to run one pair of a command. Returns subprocess outputs and timeTaken'''
    async def _run_cmd_pair(self, cmdAB, cmdBA, reps=None, idx=None, times=None, r=None, **readvArgs):
   
        # Run and time cmdAB:
        initialTimeA = time.time()

        Testprocess = await asyncio.create_subprocess_exec(
        *cmdAB,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await Testprocess.communicate()
        
        endTimeA = time.time()
        timeTakenAB = endTimeA - initialTimeA
        
        returncodeAB, stdoutAB, stderrAB = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip()

        # Run and time cmdBA:
        initialTimeB = time.time()

        Testprocess = await asyncio.create_subprocess_exec(
        *cmdBA,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await Testprocess.communicate()
        
        endTimeB = time.time()
        timeTakenBA = endTimeB - initialTimeB
        
        returncodeBA, stdoutBA, stderrBA = Testprocess.returncode, stdout.decode().strip(), stderr.decode().strip()
        
        # print(returncodeAB, stdoutAB, stderrAB, returncodeBA, stdoutBA, stderrBA)
        return (returncodeAB, stdoutAB, stderrAB, timeTakenAB), (returncodeBA, stdoutBA, stderrBA, timeTakenBA)

    ''' Formats and processes output based on the action type for the timed outputs'''
    async def timeOutputHandle(self, idx=None, reps=None, returncode=None, stdout=None, stderr=None, avgTime=None):
        self.results[self.action]['IDs'][idx] = self.cmds[idx]['IDs']

        if self.action == "checksum": # Handles stdout to obtain the checksum values
            if returncode == 0:
                checksum = stdout.split(" ")[1]
            else:
                checksum = None
            self.results[self.action]['destsums'][idx].append(checksum)
            outputs = stderr

        else:
            outputs = (returncode, stdout, stderr, avgTime)

        self.results[self.action]['cmdOuts'][idx].append(outputs)
        return

    ''' Uses the action's basecmd structure to build and store the full command'''
    def _baseCmd_parse(self, struc, siteA, src, siteB, dest, reps=None, ext=None, isUKSite=False, args=None):
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
                if item == 'args':
                    idx += 1
                else:
                    finalCmd.append(item)
                    idx += 1
            else:
                idx += 1

        finalCmd = ['timeout', self.timeout] + finalCmd

        if reps is not None:
            if self.sourcePath is not None:
                # Create repetition commands to transfer local file -> SiteA
                if isUKSite is True:
                    localCopies = []
                    for r in range(1, reps+1):
                        localFileCopy = f"{self.sourcePath[0]}{ext}_{r}"
                        siteAPath = f"root://{siteA.split('://')[1]}//{src}_{r}"

                        initTransferCmd = ['timeout', self.timeout, 'xrdcp', localFileCopy, siteAPath, '--force']
                        self.cmds['initFileCmds'].append(initTransferCmd)
                        localCopies.append(localFileCopy)
            
                    self.cmds[self.count]['localFileCopy'] = localCopies
            
            # Create the repetition commands for AB and BA
            finalCmd, src = self._clone_commands(finalCmd, None, reps, ext)

        elif self.sourcePath is not None and isUKSite is True:
        # Create single command to transfer local file -> siteA
            localFileCopy = f"{self.sourcePath[0]}{ext}"
            siteAPath = f"root://{siteA.split('://')[1]}//{src}"
            initTransferCmd = ['timeout', self.timeout, 'xrdcp', localFileCopy, siteAPath, '--force']
            self.cmds['initFileCmds'].append(initTransferCmd)
            self.cmds[self.count]['localFileCopy'] = [localFileCopy]
                 
        return finalCmd

    ''' Transfers the local file to siteA prior to running the TPC commands'''
    async def _transferInitFile(self, cmd=None):
    
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print("Initial file transferred:", process.returncode, cmd)
        else:
            print("\n", cmd)
            print("Initial Transfer To SiteA Error:", process.returncode, process.stdout, process.stderr)
    
        return
    
    ''' Parses user-specified configFile for endpoints and updates the class variable'''
    def parseConfig(self, configFile, createFiles):
        if configFile is not None:
            with open(configFile) as config:
                try:
                    self.config = yaml.safe_load(config)
    
                    if createFiles is True:
                        directory = self.config['DIRECTORY']
                        os.makedirs(directory, exist_ok=True)

                        for fileData in self.config['FILES']:
                            if isinstance(fileData['size'], str) and '*' in fileData['size']:
                                nums = fileData['size'].split('*')
                                size=int(nums[0])
                                for num in nums[1:]:
                                    size *= int(num)
                               
                            elif isinstance(fileData['size'], int):
                                size = fileData['size']

                            else:
                                raise ValueError('Please provide size as int or a multiplication of ints')

                            filePath = os.path.join(directory, fileData['name'])

                            with open(filePath, 'wb') as f:
                                f.write(os.urandom(size))

                except yaml.YAMLError as exc:
                    print(exc)
        else:
            self.config = {'SITES': self.sitesList} # Default sites
