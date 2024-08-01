#!/usr/bin/env python3
import os
import subprocess
import yaml

class BaseTest():
    def __init__(self, configFile=None):
        self.config = None
        self.timeout = None
        self.action = None
        self.sourcePath = None
        self.destinPath = None
        self.args = None
        self.results = {}
        self.cmds = {'root://':'xrd', 'https://':'gfal', 'davs://':'gfal'}       
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