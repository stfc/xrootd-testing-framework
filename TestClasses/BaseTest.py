#!/usr/bin/env python3
import os
import subprocess
import yaml
import memory_profiler

class BaseTest():
    def __init__(self, configFile=None):
        self.config = None
        self.timeout = None
        self.action = None
        self.sourcePath = None
        self.destinPath = None
        self.args = None
        self.cmds = []
        self.results = {}
        self.tools = {'root://':'xrd', 'https://':'gfal', 'davs://':'gfal'}       
        self.sitesList = {'CEPH-SVC16':['ceph-svc16.gridpp.rl.ac.uk', 'dteam:/test/']} #'LHCONE':['eoslhcb.cern.ch', 'dteam:/test/'], 'LHCOPN':['ce01-lhcb-t2.cr.cnaf.infn.it'], 'DCACHE':'hostname3'}
        self.redirect = {'INT_MANAGER':['echo-internal-manager01.gridpp.rl.ac.uk', 'dteam:/test/']} 
        self.protocols = ['root://', 'davs://', 'https://']
        self.port = 1094
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp','src', 'endpoint', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'endpoint', 'query', 'checksum', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'endpoint', 'dest', 'ADLER32']}, #Figure out how to add a custom arg ADLER32  
                        'delete'    : {'xrd' : ['xrdfs', 'endpoint', '-rm', 'args', 'dest'], 
                                       'gfal': ['gfal-rm', 'endpoint', 'dest']},
                        'load'      : {'xrd' : ['xrdcp','src', 'endpoint', 'dest', '-d1', '--force', '--tpc', 'delegate', 'only'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', '-v', 'args']
                                       }                     
                                       # List additional args that can be used for testing for each action (in docs)
                                       # Base cmd should be bare min cmd needed to execute that action successfully       
                        }
        self.parseConfig(configFile)     
       

    def setup(self, action:str, sourcePath=None, destinPath=None, timeout=None, *args):
        self.results = {}

        if isinstance(sourcePath, str) and '~' in sourcePath:
            self.sourcePath = os.path.expanduser(sourcePath)
        else:
            self.sourcePath = sourcePath
        
        if action == 'load': 
            self.sitesList = self.redirect
            self.siteB = self.redirect
        
        if timeout is not None:
            self.timeout = timeout

        self.action = action
        self.destinPath = destinPath
        self.args = args    
        self.cmds = [] # Clear the cmds list each time setup is called (in genScenarios)
        self.results[self.action] = []
        
        # print("\n INITIAL ARGS:", action, sourcePath, destinPath, self.args)
        
        return
    
    def parseConfig(self, configFile):
        if configFile is not None:
            with open(configFile) as config:
                try:
                    self.config = yaml.safe_load(config)
                except yaml.YAMLError as exc:
                    print(exc)
        else:
            self.config = {'SITES': self.sitesList} # Default sites

    def xrdadler32(self, filePath):
        cmd = ['/usr/bin/xrdadler32', os.path.expanduser(filePath)]
        Testprocess = subprocess.run(cmd, capture_output=True, text=True)
        checksum = Testprocess.stdout.split(" ")[0]
        print('Output:', Testprocess.stdout, "Error:", Testprocess.stderr)
        
        return checksum
    

    def genCmds(self, action:str, sourcePath=None, destinBaseNm=None, *args, timeout=None):
        self.setup(action, sourcePath, destinBaseNm, timeout, *args)

        #Tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. If https or davs, use gfal
        #create a combination of each protocol, server and root (i.e. a 'scenario')
        
        cmds = []
        for site, siteVal in self.config['SITES'].items(): #Iterate over destination sites
            for prot in self.protocols: #Iterate over protocols
                
                tool = self.tools[prot] #e.g. tool=xrd
                endpoint = prot + siteVal[0] + ':' + str(self.port)
                ext = '_' + prot.strip(':/') + '_' + tool
                self.destinPath = siteVal[1] + destinBaseNm
                
                # Command changes depending on self.action
                fullCmd = self.parse(self.basecmd[self.action][tool], self.sourcePath, endpoint, self.destinPath+ext, self.args)
                if self.timeout is not None:
                    fullCmd = ['timeout', str(self.timeout)] + fullCmd

                cmds.append(fullCmd)

        return cmds