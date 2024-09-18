# ReadWriteTest

## ReadWriteTest Class:
The ReadWriteTest class inherits from BaseTest class, and contains the main methods to create and run the test commands.

_class_ **ReadWriteTest( _configFile_**=None, **_createFiles_**=False, **_root_**=True, **_https_**=True, **_davs_**=True **)**

A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 

Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with ```createFiles=True``` will generate these files in the provided directory.

To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

&nbsp;

### ReadWriteTest Methods:
___

_method_ **genScenarios( _action_**, **_sourcePath_**=None, **_destinBaseNm_**=None, **_xrdArgs_**=None, **_gfalArgs_**=None, **_timeout_**=None, **_XROOTD_ECHO_**=False, **_INT_MANAGER_**=False, ****_readvArgs_ )**

This method generates and runs commands for a given functionality, for each protocol and endpoint combination

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**
* **action** (*string*) – Functionality of the command. Expects a string of one of the following:
    * *copy* – copy a single file
    * *checksum* – get checksum of one or more destination files
    * *delete* – delete a single destination file
    * *readv* – vector read on source and destination file
    * *load* – batch transfer multiple files to destination (Commands are run synchronously)
    * *bulk-copy* – transfer multiple files to destination (Commands are run asynchronously)
    * *bulk-delete* – delete multiple destination files
* **sourcePath** (*string, list*) – Path to local file. Can be list when action = *readv*, *load* or *bulk-copy*
* **destinBaseNm** (*string, list*) – Base name of file on endpoint. Can be list when action = *checksum*, *readv* or *bulk-delete*
* **xrdArgs** (*string, optional*) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
* **gfalArgs** (*string, optional*) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
* **timeout** (*int, optional*) – Optional timeout for all commands, overrides default (5 seconds)
* **XROOTD_ECHO** (*bool, optional*) – Sets endpoint to redirector: ```xrootd.echo.stfc.ac.uk```
* **INT_MANAGER** (*bool, optional*) – Sets endpoint to redirector: ```echo-internal-manager01.gridpp.rl.ac.uk```
* ****readvArgs** (*list, optional*) – A vector list in format ```[(0, 100), .. (0, 100)]```

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns a dictionary containing the command outputs required by the given action. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; All actions will return a dictionary containing the following key:value pairs:
* ```'cmdOuts': [(returncode, stdout, stderr), … (returncode, stdout, stderr)]``` – Returncode, stdout and stderr in a tuple for each command that was run
* ```‘IDs’: [‘example_ID1’, … ‘example_IDx’]``` – ID for each command/scenario in the format ‘protocol:endpoint-file’ 
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Additionally, the following actions will also contain extra key:value outputs:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Copy* and *bulk-copy*:
* ```‘srcsums’: [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each local file.
  When multiple files are passed, the ```‘srcsums’``` and ```‘cmdOuts’``` for each file is grouped into a tuple. 
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Checksum*: 
* ```‘cmdOuts’: [(stderr1, stderr2), … (stderr1, stderr2)]``` – Standard error (without returncode and stdout) for each command that was run. Grouped into tuples if multiple files are passed to destinBaseNm.
* ```‘destsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each destination file. Grouped into tuples if multiple files are passed to destinBaseNm.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Readv*: 
* ```‘cmdOuts’: [(returncode, [destChunk], stderr), … (returncode, destChunk, stderr)]``` – Returncode, destChunk (a.k.a stdout) and stderr in a tuple for each command that was run. 
* ```‘srcChunks’ = [[srcChunk], … [srcChunk]]``` – Chunks for local file for each command that was run
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Load*:
* ```‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
* ```‘redirects’ = [(‘site1’, ‘site2’), … (‘site1’, ‘site2’)]``` – Sites that were redirected to, populated if redirectors ```XROOTD_ECHO=True``` or ```INT_MANAGER=True```

&nbsp;&nbsp;&nbsp;&nbsp; **Return type:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dictionary

___

_method_ **genTimedScenarios( _action_**, **_sourcePath_**=None, **_destinBaseNm_**=None, **_xrdArgs_**=None, **_gfalArgs_**=None, **_reps_**=3, **_timeout_**=None, **_XROOTD_ECHO_**=False, **_INT_MANAGER_**=False, ****_readvArgs_ )**

This method generates and runs commands for a given functionality, for each protocol and endpoint combination. \
Each command is run for several repetitions (reps) and timed. An average of this time is returned with the output.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**
* **action** (*string*) – Functionality of the command. Expects a string of one of the following:
    * *copy* – copy a single file
    * *checksum* – get checksum of one or more destination files
    * *delete* – delete a single destination file
    * *readv* – vector read on source and destination file
    * *load* – batch transfer multiple files to destination (Commands are run synchronously)
    * *bulk-copy* – transfer multiple files to destination (Commands are run asynchronously)    
    * *bulk-delete* – delete multiple destination files
* **sourcePath** (*string, list*) – Path to local file. Can be list when action = *readv*, *load* or *bulk-copy*
* **destinBaseNm** (*string, list*) – Base name of file on endpoint. Can be list when action = *checksum*, *readv* or *bulk-delete*
* **xrdArgs** (*string, optional*) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
* **gfalArgs** (*string, optional*) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
* **reps** (*int, optional*) – Set number of repetitions for each command to run, overrides default (3)
* **timeout** (*int, optional*) – Optional timeout for all commands, overrides default (5 seconds)
* **XROOTD_ECHO** (*bool, optional*) – Sets endpoint to redirector: ```xrootd.echo.stfc.ac.uk``` 
* **INT_MANAGER** (*bool, optional*) – Sets endpoint to redirector: ```echo-internal-manager01.gridpp.rl.ac.uk```
* ****readvArgs** (*list, optional*) – A vector list in format ```[(0, 100), .. (0, 100)]```

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns a dictionary containing the command outputs required by the given action. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; All actions will return a dictionary containing the following key:value pairs:
* ```‘cmdOuts’: [(returncode, stdout, stderr, avgTime), … (returncode, stdout, stderr, avgTime)]``` – Returncode, stdout, stderr and avgTime in a tuple for each command that was run
* ```‘IDs’: [‘example_ID1’, … ‘example_IDx’]``` – ID for each command/scenario in the format ‘protocol:endpoint-file’

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Additionally, the following actions will also contain extra key:value outputs: 

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Copy* and *bulk-copy*:
* ```‘srcsums’: [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each local file.
  When multiple files are passed, the ```‘srcsums’``` and ```‘cmdOuts’``` for each file is grouped into a tuple.
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Checksum*: 
* ```‘cmdOuts’: [(file1-stderr, file2-stderr), … (file1-stderr, file2-stderr)]``` – Standard error (without returncode and stdout) for each command that was run. Grouped into tuples if multiple files are passed to destinBaseNm.
* ```‘destsums’: [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each destination file. Grouped into tuples if multiple files are passed to destinBaseNm.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Readv*: 
* ```‘cmdOuts’: [(returncode, [destChunk], stderr, avgTime), … (returncode, destChunk, stderr), avgTime]``` – Returncode, destChunk (a.k.a stdout), stderr and avgTime in a tuple for each command that was run. 
* ```‘srcChunks’ = [[srcChunk], … [srcChunk]]``` – Chunks for local file for each command that was run
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Load*:
* ```‘srcsums’: [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)]``` – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
* ```‘redirects’: [(‘site1’, ‘site2’), … (‘site1’, ‘site2’)]``` – Sites that were redirected to, populated if redirectors ```XROOTD_ECHO=True``` or ```INT_MANAGER=True```
  
&nbsp;&nbsp;&nbsp;&nbsp; **Return type:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dictionary

