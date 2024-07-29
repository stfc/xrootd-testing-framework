#!/usr/bin/env python3
import os

class BaseTest():
    def __init__(self):
        self.action = None
        self.sourcePath = None
        self.destinPath = None
        self.args = None
        self.cmds = {'root://':'xrd', 'https://':'gfal', 'davs://':'gfal'}       
        self.sitesList = {'CEPH-SVC16':['ceph-svc16.gridpp.rl.ac.uk', 'dteam:/test/']} #'LHCONE':['eoslhcb.cern.ch', 'dteam:/test/'], 'LHCOPN':['ce01-lhcb-t2.cr.cnaf.infn.it'], 'DCACHE':'hostname3'}
        self.redirect = {'INT_MANAGER':['xrootd.echo.stfc.ac.uk', 'dteam:/test/']} 
        self.protocols = ['root://', 'davs://', 'https://']     
        
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp','src', 'endpoint', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'endpoint', 'args', 'dest'], 
                                       'gfal': ['gfal-sum', 'endpoint', 'dest', 'ADLER32']}, #Figure out how to add a custom arg ADLER32  
                        'delete'    : {'xrd' : ['xrdfs', 'endpoint', 'args', 'dest'], 
                                       'gfal': ['gfal-rm', 'endpoint', 'dest']},
                        'load'      : {'xrd' : ['xrdcp','src', 'endpoint', 'dest', '-d1', '--force'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', '-v', 'args']
                                       }                            
                        }

        self.authentSys = []
        self.port = 1094
       
    def setup(self, action:str, sourcePath=None, destinPath=None, *args):

        if isinstance(sourcePath, str) and '~' in sourcePath:
            self.sourcePath = os.path.expanduser(sourcePath)
        else:
            self.sourcePath = sourcePath

        self.action = action
        self.destinPath = destinPath
        self.args = args
        #print("\n INITIAL ARGS:", action, sourcePath, destinPath, self.args)
        
        return