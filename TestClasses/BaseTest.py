#!/usr/bin/env python3
import subprocess
import os

class BaseTest():
    def __init__(self):
        self.sourcePath = None
        self.testProcess = None #This is the name of the test processes
        self.cmd = None #This variable will contain the test's command
        self.args = None
        self.matrix = None
        self.inpPath = None
        self.destinPath = None
        self.sitesList = {'LHCONE':'hostname1', 'LHCOPN':'hostname2', 'DCACHE':'hostname3', 'XROOTD':'hostname4', 'TSTP':'ceph-svc16.gridpp.rl.ac.uk'}
        self.servers = ['ceph-svc16.gridpp.rl.ac.uk']
        self.protocols = ['root://', 'davs://', 'https://']
        self.basecmd = {'xrdcp':['xrdcp','src', 'endpoint', 'dest', 'args'], 'gfal-copy': ['gfal-copy', 'src', 'endpoint', 'dest', 'args'], 
                   'xrdfs': ['xrdfs', 'endpoint', 'args', 'dest'], 'gfal-sum': ['gfal-sum', 'endpoint', 'args', 'dest'],
                   'copy' : {'xrd': ['xrdfs', 'endpoint', 'args', 'dest'], 'gfal': ['gfal-sum', 'endpoint', 'args', 'dest']}}
        self.authentSys = []
        self.port = 1094
        self.expectOut = None
        self.stdout = None
        self.stderr = None
        #import os
    
    def setup(self, tool, sourcePath=None, destinPath=None, *args):
        
        if isinstance(sourcePath, str) and '~' in sourcePath:
            self.sourcePath = os.path.expanduser(sourcePath)
        else:
            self.sourcePath = sourcePath

        self.destinPath = destinPath
        self.args = args
        print("INITIAL ARGS:", sourcePath, destinPath, self.args)

        if tool in ['xrdcp', 'gfal-copy']:
            self.cmds = {'root://':'xrdcp', 'https://':'gfal-copy', 'davs://':'gfal-copy'}
        elif tool in ['xrdfs']:
            self.cmds = {'root://':'xrdfs', 'https://':'gfal-sum', 'davs://':'gfal-sum'}

        self.setupMatrix()
        print(self.sourcePath, self.destinPath)

        return
    
    def setupMatrix(self):
        self.matrix = [self.servers, self.protocols]
        #print(self.matrix)
        return

    def setupToken(self):
        tempProcess = subprocess.Popen(['eval', '`oidc-agent`'])
        usrNm = ['oidc-add', 'efv97572']
        exportToken = ['( export', 'BEARER_TOKEN=$(oidc-token --scope=offline_access --scope=storage.read:/ --time=3600 cms_katy) ; unset X509_USER_PROXY ; gfal-stat davs://ceph-dev-gw4.gridpp.rl.ac.uk:1094/atlas:scratchdisk/rucio/user/jwalder/test/test1M ; )']
        print("setupToken")
        return

    # def tearDown(self):
    #     self.testProcess.kill()
    #     print(str(self.testProcess.pid))
    #     print("tearDown")
    #     return