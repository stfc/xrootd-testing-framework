#!/usr/bin/env python3
import subprocess
import os

class BaseTest():
    def __init__(self):
        self.action = None
        self.sourcePath = None
        self.destinPath = None
        self.args = None
        self.testProcess = None #This is the name of the test processes
        self.cmds = {'root://':'xrd', 'https://':'gfal', 'davs://':'gfal'}       
        self.sitesList = {'LHCONE':'hostname1', 'LHCOPN':'hostname2', 'DCACHE':'hostname3', 'XROOTD':'hostname4', 'TSTP':'ceph-svc16.gridpp.rl.ac.uk'}
        self.servers = ['ceph-svc16.gridpp.rl.ac.uk']
        self.protocols = ['root://', 'davs://', 'https://']
        self.matrix = None 
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp','src', 'endpoint', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'endpoint', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'endpoint', 'dest', 'ADLER32']}, #Figure out how to add a custom arg ADLER32  
                        'delete'    : {'xrd' : ['xrdfs', 'endpoint', 'args', 'dest'], 
                                       'gfal': ['gfal-rm', 'endpoint', 'dest']},
                                                               
                                       }
        self.authentSys = []
        self.port = 1094
        #import os
    
    def setup(self, action:str, sourcePath=None, destinPath=None, *args):
        
        if isinstance(sourcePath, str) and '~' in sourcePath:
            self.sourcePath = os.path.expanduser(sourcePath)
        else:
            self.sourcePath = sourcePath

        self.action = action
        self.destinPath = destinPath
        self.args = args
        print("INITIAL ARGS:", action, sourcePath, destinPath, self.args)

        self.setupMatrix()
        print(self.sourcePath, self.destinPath)
        return
    
    def setupMatrix(self):
        self.matrix = [self.servers, self.protocols]
        return

    # def tearDown(self):
    #     self.testProcess.kill()
    #     print(str(self.testProcess.pid))
    #     print("tearDown")
    #     return