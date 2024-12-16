#!/usr/bin/env python3
import ast
from fnmatch import fnmatch
import glob
import os
import re
import shutil
import subprocess
import sys
import yaml
from functools import wraps
from XRootD import client



class BaseTest():
    def __init__(self, configFile=None, createFiles=False, root=True, https=True, davs=True):
        self.config = None
        self.timeout = None
        self.action = None
        self.count = 0
        self.sourcePath = None
        self.destinBaseNm = None
        self.isLoad = False # Handles xrd's lack of path sanitisation when doing batch transfers
        self.cmds = {}
        self.results = {}
        self.fileBytes = {}
        self.tools = {'root://':'xrd', 'https://':'gfal', 'davs://':'gfal'}
        self.sitesList = {'CEPH-SVC16':['ceph-svc16.gridpp.rl.ac.uk', 'dteam:/test/']} #'LHCONE':['eoslhcb.cern.ch', 'dteam:/test/'], 'LHCOPN':['ce01-lhcb-t2.cr.cnaf.infn.it']}
        self.redirect = {'INT_MANAGER': {'INT_MANAGER':['echo-internal-manager01.gridpp.rl.ac.uk', 'dteam:/test/']},
                         'XROOTD_ECHO': {'XROOTD_ECHO':['xrootd.echo.stfc.ac.uk', 'dteam:/test/']}} 
        
        self.protocols = ['root://', 'davs://', 'https://']
        if root == False:
            self.protocols.remove('root://')
        if davs == False:
            self.protocols.remove('davs://')
        if https == False:
            self.protocols.remove('https://')

        self.port = 1094
        self.basecmd = {'copy'      : {'xrd' : ['xrdcp', 'src', 'endpoint', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', 'args']}, 
                        'checksum'  : {'xrd' : ['xrdfs', 'endpoint', 'query', 'checksum', 'dest'], 
                                       'gfal': ['gfal-sum', 'endpoint', 'dest', 'ADLER32']},   
                        'delete'    : {'xrd' : ['xrdfs', 'endpoint', 'rm', 'dest', 'args'], 
                                       'gfal': ['gfal-rm', 'endpoint', 'dest', 'args']},
                        'load'      : {'xrd' : ['xrdcp', 'src', 'endpoint', 'dest', '-d2', 'args'], 
                                       'gfal': ['gfal-copy', '--from-file', 'file', 'endpoint', 'dest', '-vv', 'args']},
                        'readv'     : {'xrd' : ['xrdClient', 'endpoint', 'dest', 'args']},
                        'bulk-copy' : {'xrd' : ['xrdcp', 'src', 'endpoint', 'dest', 'args'], 
                                       'gfal': ['gfal-copy', 'src', 'endpoint', 'dest', 'args']},
                        'bulk-delete':{'xrd' : ['xrdfs', 'endpoint', 'rm', 'dest'], 
                                       'gfal': ['gfal-rm', 'endpoint', 'dest']}                                  
                                       # List additional args that can be used for testing for each action (in docs)
                                       # Base cmd should be bare min cmd needed to execute that action successfully       
                        }
        self.parseConfig(configFile, createFiles)     
       
    ''' Define a decorator that runs specific methods only if self.action==readv (vector read), meaning XrdClient is used'''
    def run_if_readv(func):
        @wraps(func)
        def wrap(self, *args, **kwargs):
            if self.action == 'readv':
                return(func(self, *args, **kwargs))
            else:
                pass
        return wrap
    
    ''' Resets class variables used for command generation'''
    def _clear_vars(self, timeout):
        if timeout is not None:
            self.timeout = str(timeout)
        elif 'TIMEOUT' in self.config.keys():
            self.timeout = str(self.config['TIMEOUT'])
        else:
            self.timeout = str(5)
        self.action = None
        self.count = 0
        self.sourcePath = None
        self.destinBaseNm = None
        self.cmds = {}
        self.results = {}
        self.fileBytes = {}
        self.config['SITES'] = self.sitesList
        return
        
    ''' Checks that the correct required inputs are passed '''
    def _handle_inputs(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, gfalArgs=None, reps=None):
        if action not in self.basecmd.keys():
            raise ValueError(f'"{action}" is not a valid action')
        elif action=='copy':
            if sourcePath is None:
                raise ValueError('Please provide a sourcePath')
        elif action=='delete':
                if sourcePath is not None:    
                    raise ValueError('Action "delete" does not take sourcePath as argument')
                if destinBaseNm is None:
                    raise ValueError('Please provide a destinBaseNm')
        elif action=='checksum':
            if sourcePath is not None:
                raise ValueError('Action "checksum" does not take sourcePath as argument')
            if destinBaseNm is None:
                raise ValueError('Please provide one or more destinBaseNms')
        elif action=='load':
            if destinBaseNm is not None:
                raise ValueError('Action "load" does not take destinBaseNm as argument')
            if sourcePath is None:
                raise ValueError('Please provide one or more sourcePaths')
        elif action=='bulk-copy':
            if sourcePath is None:
                raise ValueError('Please provide one or more sourcePaths')
        elif action=='bulk-delete':
            if reps is not None:
                if sourcePath is None:
                    raise ValueError('Please provide one or more sourcePaths for timed deletions')
            else:
                if sourcePath is not None:
                    raise ValueError('Action "bulk-delete" does not take sourcePath as argument')
                if destinBaseNm is None:
                    raise ValueError('Please provide one or more destinBaseNms')
        elif action=='readv':
            if gfalArgs is not None:
                raise ValueError('Action "readv" does not take gfalArgs as argument')
            if sourcePath is None:
                raise ValueError('Please provide one or more sourcePaths')
    
        return

    ''' Initialises class variables based on user input'''
    def setup(self, action:str, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs):
        self._clear_vars(timeout)
        self._handle_inputs(action, sourcePath, sourceBaseNm, destinBaseNm, gfalArgs, reps)
        self._arg_contains_vector(**readvArgs)

        # Write file of size x during config
        self.action = action
        self.sourcePath = self._expand_paths(sourcePath)
        self.destinBaseNm = self._expand_paths(destinBaseNm, baseNm=True)  
        self.results[self.action] = {'cmdOuts':[], 'IDs':[]}
        
        if xrdArgs is not None:
            self._argReplace('xrd', xrdArgs)
        if gfalArgs is not None:
            self._argReplace('gfal', gfalArgs)
            
        if INT_MANAGER == True: 
            self.config['SITES'] = self.redirect['INT_MANAGER']
        if XROOTD_ECHO == True:
            self.config['SITES'] = self.redirect['XROOTD_ECHO']

        if action == 'checksum':
            self.results[self.action]['destsums'] = []
        elif action == 'load':
            self.isLoad = True
            self.results[self.action]['srcsums'] = [] 
            self.results[self.action]['redirects'] = []
        elif sourceBaseNm is None:
            if action == 'copy' or action == 'bulk-copy':
                self.isLoad = False
                self.results[self.action]['srcsums'] = [] 
    
        # print(f"\n INITIAL ARGS: {action} {sourcePath} {destinBaseNm} {self.args}")

        return
    
    ''' Takes string or list of paths and expands them. Returns list of paths'''
    def _expand_paths(self, paths, baseNm=False):
        if paths == None:
            return None
                
        if isinstance(paths, str):
            paths = [paths]  # Convert single string to a list for processing

        expandedFiles = []
        for path in paths:
            # Expand the `~` to the full home directory path
            expandedPath = os.path.expanduser(path)

            # Use glob to handle wildcards and expand them into file paths
            if '*' in expandedPath:
                files = glob.glob(expandedPath)
            else:
                files = [path]

            # Convert to absolute paths and add to the final list
            if baseNm is True: 
                # Generate a list of file base names only
                expandedFiles.extend([os.path.basename(file) for file in files])
            else: 
                # Generate a list of full file paths
                expandedFiles.extend([os.path.abspath(file) for file in files])
        
        # copy and delete can only take a single path for sourcePath/destinBaseNm
        if self.action=='copy' or self.action=='delete':
            if len(expandedFiles) > 1:
                raise ValueError("Only a single string is allowed as sourcePath or destinBaseNm for copy and delete")
        
        return expandedFiles
    
    ''' Replaces 'args' in self.basecmd dictionary with user-specified arguments '''
    def _argReplace(self, tool, toolArgs):
        if isinstance(toolArgs, str):
            toolArgs = tuple(toolArgs.split(","))
        if 'args' in self.basecmd[self.action][tool]:
            argdex = self.basecmd[self.action][tool].index('args')
            for arg in reversed(toolArgs):
                self.basecmd[self.action][tool].insert(argdex, arg)
            self.basecmd[self.action][tool].remove('args')

    ''' Parses user-specified configFile for endpoints and updates the class variable'''
    def parseConfig(self, configFile, createFiles):
        if configFile is not None:
            with open(configFile) as config:
                try:
                    self.config = yaml.safe_load(config)
                    self.sitesList = self.config['SITES']
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

        return
    
    '''Obtains port for site'''
    def _check_port(self, siteInfo):
        if len(siteInfo) == 3:
            if isinstance(siteInfo[2], int):
                return siteInfo[2]
            else:
                raise ValueError("Port number must be int")
        else:
            return self.port

    ''' Uses xrdadler32 script to obtain checksum'''
    def xrdadler32(self, filePath):
        cmd = ['/usr/bin/xrdadler32', os.path.expanduser(filePath)]
        Testprocess = subprocess.run(cmd, capture_output=True, text=True)
        checksum = Testprocess.stdout.split(" ")[0]
            
        return checksum
    
    ''' Unsets vomsProxy and token environmental variables'''
    def unsetCreds(self, vomsProxy=None, bearerToken=None, x509User=None):
        if vomsProxy is not None:
            vomsProxy = os.path.expanduser(vomsProxy)
            
            if isinstance(vomsProxy, str) and '*' in vomsProxy:   
                vomsProxy = glob.glob(vomsProxy)
            else:
                vomsProxy = [vomsProxy]
            for file in vomsProxy: 
                shutil.copy(file, '../TestData/') # copy to ../TestData                
                os.remove(file) # delete from tmp

        if bearerToken is not None:
            os.unsetenv("BEARER_TOKEN")
        if x509User is not None:
            os.unsetenv("X509_USER_PROXY")
        return

    ''' Resets vomsProxy and token environmental variables'''
    def resetCreds(self, vomsProxy=None, bearerToken=None, x509User=None):
        
        if vomsProxy is not None:
            vomsProxy = f"../TestData/{os.path.basename(vomsProxy)}"
            if isinstance(vomsProxy, str) and '*' in vomsProxy:   
                vomsProxy = glob.glob(vomsProxy)
            else:
                vomsProxy = [vomsProxy]
            for path in vomsProxy: 
                shutil.copy(path, '/tmp/') #copy from current dir back to tmp
                os.remove(path) # delete from current dir:

        if bearerToken is not None:
            os.environ["BEARER_TOKEN"] = bearerToken
        if x509User is not None:
            os.environ["X509_USER_PROXY"] = x509User
        return

    ''' Gets the protocol, endpoint and port combination for each command and initialises the results dictionary '''
    def _genCmds(self, action:str, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs):
        self.setup(action=action, sourcePath=sourcePath, destinBaseNm=destinBaseNm, xrdArgs=xrdArgs, gfalArgs=gfalArgs, reps=reps, timeout=timeout, XROOTD_ECHO=XROOTD_ECHO, INT_MANAGER=INT_MANAGER, **readvArgs)

        # print("ARGUMENTS:", self.action, self.sourcePath, self.destinBaseNm, self.timeout, self.count)
        
        # Iterate over destination sites
        for site, siteVal in self.config['SITES'].items(): 
            port = self._check_port(self.config['SITES'][site])

            # Iterate over protocols
            for protocol in self.protocols: 

                # If action == 'readv', skip generation of davs & https /gfal commands
                if action == 'readv' and protocol != 'root://':
                    continue

                self._cmd_helper_function(protocol, site, siteVal, port, reps)

        # Initialise results dictionary 
        if isinstance(self.results[self.action], dict):
             for key in self.results[self.action].keys():
                 self.results[self.action][key] = [None]*len(self.cmds)                 
        else:
            self.results[self.action] = [None]*len(self.cmds)

        # sys.exit()
    
        return

    ''' Generates the needed variables and passes them to the parser to generate the full commands '''
    def _cmd_helper_function(self, protocol=None, site=None, siteVal=None, port=None, reps=None):
        
        ''' Generate the variables and names needed by all actions '''
        tool = self.tools[protocol]
        endpoint = f"{protocol}{siteVal[0]}:{port}"
        ext = f"_{protocol.strip(':/')}_{tool}_{site}"
        testID = f"{protocol.strip('/')}{site}" 
        siteDir = siteVal[1] # e.g. dteam:/test/
        localSrcCopies = [f"{file}{ext}" for file in self.sourcePath] if self.sourcePath is not None else None
        if self.isLoad is True and tool == 'xrd' and self.action != 'load':
            siteDir += '/' # e.g. dteam:/test//

        ''' Obtain a list of destination paths '''
        if self.action == 'load':
        # Don't append the file name to the destinPath
            destinPaths = [siteDir]
        elif self.destinBaseNm is not None:
        # Use the provided destinBaseNms 
            destinPaths = [f"{siteDir}{baseNm}{ext}" for baseNm in self.destinBaseNm]
        else:
        # Get the baseNms from the source files
            destinPaths = [f"{siteDir}{os.path.basename(baseNm)}{ext}" for baseNm in self.sourcePath]


        ''' Pass the variables to the parser '''
        if self.action == 'checksum': 
        # Generate 1 command per destination file
            for n in range(len(destinPaths)):
                testID = f"{protocol.strip('/')}{site}-{self.destinBaseNm[n]}"
                self._baseCmd_parse(self.basecmd[self.action][tool], localSrcCopies, endpoint, [destinPaths[n]], testID, reps, ext)

        elif self.action == 'bulk-copy' or self.action == 'readv':  
         # Generate 1 command per source file
            for n in range(len(localSrcCopies)):
                testID = f"{protocol.strip('/')}{site}-{os.path.basename(self.sourcePath[n])}"
                self._baseCmd_parse(self.basecmd[self.action][tool], [localSrcCopies[n]], endpoint, [destinPaths[n]], testID, reps, ext)
        
        else: 
        # Generate 1 command (per protocol+endpoint)
            if self.destinBaseNm is not None:
            # Create IDs from the destination file(s) basenames
                for baseNm in self.destinBaseNm:
                    testID += f"-{baseNm}"
            else: 
            # Create IDs from the source file(s) basenames
                for sourcePath in self.sourcePath: 
                    testID += f"-{os.path.basename(sourcePath)}"

            self._baseCmd_parse(self.basecmd[self.action][tool], localSrcCopies, endpoint, destinPaths, testID, reps, ext)
      
        return

    ''' Uses the action's basecmd structure to build and store the full command'''
    def _baseCmd_parse(self, struc, src=None, endpoint=None, dest=None, testID=None, reps=None, ext=None):
        self.cmds[self.count] = {'cmd': None, 'localFileCopy': None, 'IDs': None}
        finalCmd = []
        if self.action != 'readv':
            finalCmd.extend(['timeout', str(self.timeout)])
            finalCmd.append(struc[0])
        strucTmp = struc[1:]
        n = 0

        while n < len(strucTmp):
            item = strucTmp[n]
            if n < len(strucTmp)-1:
                nextItem = struc[1:][n+1]
                
            if item in locals().keys() and locals()[item] is not None:
                if item == 'endpoint' and nextItem == 'dest': # Combine the endpoint and dest
                    for d in dest:
                        fullPath = f"{endpoint}//{d}"
                        finalCmd.append(fullPath) 
                    n+=1 # Skip to the item after 'dest'
                elif item == 'src':
                    finalCmd.extend(src)
                else:
                    if isinstance(locals()[item], list):
                        finalCmd.extend(locals()[item])
                    else:
                        finalCmd.append(locals()[item])
                n+=1

            elif item not in locals().keys() and isinstance(item, str):
            # If the basecmd contains items not passed in as arguments to this method 
                if item == 'file': 
                    transferFile = self._create_gfal_transfer_file(src, reps, None, self.count)
                    finalCmd.append(transferFile)
                    src.append(transferFile)
                    n+=1
                elif item == 'args' or item == 'mult':
                # Skip to the next item
                    n+=1
                else:
                # Add the item to the command (e.g. ADLER32)
                    finalCmd.append(item)
                    n+=1
            else:
                n+=1    

        if reps is not None:
            finalCmd, src = self._clone_commands(finalCmd, src, reps, ext)

        self.cmds[self.count]['cmd'] = finalCmd
        self.cmds[self.count]['localFileCopy'] = src
        self.cmds[self.count]['IDs'] = testID

        # print(f"\nfinalCmds: {finalCmd} \n\n Local File Copies: {src}")
        
        self.count += 1

        return
    
    ''' Creates a file that contains the file paths to transfer using gfal's bulk copy '''
    def _create_gfal_transfer_file(self, fileList, reps=None, r=None, *args):
        # Create a new file called transfer{args}.txt in the given dir
        if 'DIRECTORY' in self.config.keys() and self.config['DIRECTORY'] is not None:
            dir = self.config['DIRECTORY']
        else:
            dir = "../TestData/"

        filePath = f"{dir}transfer"

        if args is not None:    
            for arg in args:
                filePath += str(arg)
    
        filePath += ".txt"

        if reps is not None:
            return filePath

        f = open(filePath, "w")

        #iterate over the files to transfer
        for srcfile in fileList:
            fullPath = f"file://{os.path.abspath(srcfile)}"
            # Generate the full path and write it to transfer{args}.txt
            if r is not None:
                fullPath += f"_{r}"
            f.write(fullPath + "\n")
        f.close()

        return filePath

    ''' Generates replicates of the commands and appends number to end of file(s) based on number of reps'''
    def _clone_commands(self, cmd, origSrc, reps, ext):
        
        finalCmd = []
        src = []

        for i in range(1, reps+1):
            finalCmd.append([])
        
            for n in range(len(cmd)):
                argmnt = cmd[n]

                if fnmatch(argmnt, "*/transfer*.txt"):
                    filePath = self._create_gfal_transfer_file(origSrc[:-1], None, i, f"{self.count}_{i}")
                    argmnt = filePath
                    currFiles = [f"{file}_{i}" for file in origSrc[:-1]] 
                    src.extend((currFiles + [argmnt]))
                
                elif ext in cmd[n]: # e.g. tst.txt_root_xrd
                    argmnt = f"{cmd[n]}_{i}" # e.g. tst.txt_xrd_1

                    if self.sourcePath is not None and cmd[n].split(ext)[0] in self.sourcePath:
                        src.append(argmnt)
                
                finalCmd[-1].append(argmnt)
        
        if len(src) == 0:
            src = None
      
        return finalCmd, src
                
    ''' Opens user-specified local files and saves data as bytes'''
    def _store_local_file_bytes(self):
        if self.sourcePath is None:
            return
        for path in self.sourcePath:
            with open(path, 'rb') as f:
                bytes = f.read()
            self.fileBytes[path] = bytes
        return
    
    ''' Creates local copies of the user-specified local files '''
    async def _gen_file_copy(self, idx:int=None, fileCopyNms:list=None):
        
        if fileCopyNms is None or self.sourcePath is None:
            return
        
        for n in range(len(fileCopyNms)):
            ext = r"_[a-zA-Z]+_[a-zA-Z]+_[a-zA-Z]+.*"
            fileCopyBase = re.sub(ext, '', fileCopyNms[n])

            if fileCopyBase not in self.sourcePath:
                continue
            
            byteData = self.fileBytes[fileCopyBase]

            with open(fileCopyNms[n], "wb") as tmpFile:
                tmpFile.write(byteData)
        return 
    
    ''' Deletes the local copies of the user-specified local files'''
    async def _del_file_copy(self, idx:int=None, tempFiles:list=None, fileCopyNms:list=None):
        if fileCopyNms is None or self.sourcePath is None:
            return None
        
        for n in range(len(fileCopyNms)):
            try:
                os.remove(fileCopyNms[n])
            except:
                pass
        return

    '''Checks that the keyword arguments contain a vector with a valid format'''
    @run_if_readv
    def _arg_contains_vector(self, **readvArgs):
        is_valid = True
        if 'vector' in readvArgs.keys():
            if not isinstance(readvArgs['vector'], list):
                is_valid=False
            for item in readvArgs['vector']:
                if not isinstance(item, tuple) or len(item) != 2:
                    is_valid=False
                if not all(isinstance(i, int) for i in item):
                    is_valid=False
        else:
            is_valid=False
        
        if is_valid is False:
            raise ValueError('Please provide a valid vector structure, for example: [(0, 100)]')
        return
    
    ''' Uses XRootD client to obtain chunks from destination file'''
    @run_if_readv
    def _vector_read_dest(self, cmd, **readvArgs):
        xrd_client = client.File()
        chunks = []
        
        for destinPath in cmd:
            
            # Open destination file on server
            status, response = xrd_client.open(destinPath, timeout=int(self.timeout))
            if status.ok == True:
                status, response = xrd_client.vector_read(readvArgs['vector'], timeout=int(self.timeout))
                for n, data in enumerate(response):
                    chunks.append(data.buffer)
            else: 
                chunks = None

        returncode, stdout, stderr = status.code, chunks, status.message 

        return returncode, stdout, stderr
    
    ''' Obtains chunks from user-specified local file '''
    @run_if_readv
    def _vector_read_src(self, **readvArgs):
        self.results[self.action]['srcchunks'] = []
        for file in self.sourcePath: 
            chunks = [] 
            for offset, length in readvArgs['vector']:
                bytes = self.fileBytes[file]
                chunk = bytes[offset:offset + length]
                chunks.append(chunk)
            self.results[self.action]['srcchunks'].append(chunks)
        return

    ''' Runs self._run_cmd synchronously instead of asynchronously'''
    async def _run_cmd_sync(self, idx):
        return await self._run_cmd(idx)
    
    ''' Runs self._run_timed_cmd synchronously instead of asynchronously'''
    async def _run_time_sync(self, reps, idx):
        return await self._run_timed_cmd(reps, idx)
    
    ''' Deletes stored byte data  '''
    def _teardown(self):
        if self.sourcePath is not None:
            for file in self.sourcePath:
                del self.fileBytes[file]
        return

    '''Removes the files generated from Config file'''
    def cleanup(self):
        # delete the files generated from ConfigFile
        if 'DIRECTORY' in self.config.keys() and 'FILES' in self.config.keys():
            directory = self.config['DIRECTORY']
            for file in self.config['FILES']:
                filePath = f"{directory}{file['name']}"
                if os.path.exists(filePath):
                    os.remove(filePath)
        else:
            pass
        return