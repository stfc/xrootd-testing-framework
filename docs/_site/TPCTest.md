# TPCTest

## TPCTest Class:
The TPCTest class inherits from BaseTest class, and contains the main methods to create and run the test commands.

_class_ **TPCTest( _configFile_**=None, **_createFiles_**=False, **_root_**=True, **_https_**=True, **_davs_**=True **)**

A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port.

Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with createFiles=True will generate these files in the provided directory.

To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

&nbsp;

### TPCTest Methods:
___

_method_ **genScenarios( _action_**, **_sourcePath_**=None, **_sourceBaseNm_**=None, **_destinBaseNm_**=None, **_xrdArgs_**=None, **_gfalArgs_**=None, **_timeout_**=None, **_XROOTD_ECHO_**=False, **_INT_MANAGER_**=False **)**

This method generates and runs commands for a given functionality, for each protocol and endpoint combination. \
These functionalities are performed on endpoint A and endpoint B, therefore the commands and their outputs are treated as pairs.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**
* **action** (*string*) – Functionality of the command. Expects a string of one of the following:
    * *copy* – copy a single file
    * *checksum* – get checksum of one or more destination files
    * *delete* – delete a single destination file
* **sourcePath** (*string*) – Path to local file. Used to transfer local file to source endpoint
* **sourceBaseNm** (*string*) – Base name of file on source endpoint.
* **destinBaseNm** (*string*) – Base name of file on destination endpoint.
* **xrdArgs** (*string, optional*) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
* **gfalArgs** (*string, optional*) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
* **TestAll** (*bool, optional*) – If set to True, will run commands using all sites under ```TEST_ENDPOINTS``` in config file (i.e. all ‘Site A’s)
* **timeout** (*int, optional*) – Optional timeout for all commands, overrides default (5 seconds)
* **XROOTD_ECHO** (*bool, optional*) – Sets endpoint to redirector: ```xrootd.echo.stfc.ac.uk``` 
* **INT_MANAGER** (*bool, optional*) – Sets endpoint to redirector: ```echo-internal-manager01.gridpp.rl.ac.uk```

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns a dictionary containing the command outputs required by the given action. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The commands in TPCTest are generated and run as pairs, so the outputs are also in pairs. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; All actions will return a dictionary containing the following key:value pairs:
* ```‘cmdOuts’: [((returncodeAB, stdoutAB, stderrAB), (returncodeBA, stdoutBA, stderrBA)), … ((returncodeAB, stdoutAB, stderrAB), (returncodeBA, stdoutBA, stderrBA))]``` – Returncode, stdout and stderr in pairs of tuples for each command pair that was run
* ```‘IDs’: [‘example_ID1’, … ‘example_IDx’]``` – ID for each command/scenario in the format ‘protocol:sourceEndpoint-destinationEndpoint-file’
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Additionally, the following actions will also contain extra key:value outputs:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Checksum*: 
* ```‘cmdOuts’: [(stderrAB, stderrBA), … (stderrAB, stderrBA)]``` – Standard errors (without returncode and stdout) for each command pair that was run.
* ```‘destsums’: [(checksumAB, checksumBA), … (checksumAB, checksumBA)]``` – Checksums for files on both sites in pairs.
  
&nbsp;&nbsp;&nbsp;&nbsp; **Return type:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; dictionary

___

_method_ **genTimedScenarios( _action_**, **_sourcePath_**=None, **_destinBaseNm_**=None, **_xrdArgs_**=None, **_gfalArgs_**=None, **_reps_**=3, **_timeout_**=None, **_XROOTD_ECHO_**=False, **_INT_MANAGER_**=False **)**

This method generates and runs commands for a given functionality, for each protocol and endpoint combination.  
These functionalities are performed on endpoint A and endpoint B, therefore the commands and their outputs are treated as pairs. \
Each command pair is run for several repetitions (reps) and timed. An average of the time is returned with the output.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**
* **action** (*string*) – Functionality of the command. Expects a string of one of the following:
    * *copy* – copy a single file
    * *checksum* – get checksum of one or more destination files
    * *delete* – delete a single destination file
* **sourcePath** (*string*) – Path to local file. Used to transfer local file to source endpoint
* **sourceBaseNm** (*string*) – Base name of file on source endpoint.
* **destinBaseNm** (*string*) – Base name of file on destination endpoint.
* **xrdArgs** (*string, optional*) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
* **gfalArgs** (*string, optional*) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
* **reps** (*int, optional*) – Set number of repetitions for each command to run, overrides default (3)
* **timeout** (*int, optional*) – Optional timeout for all commands, overrides default (5 seconds)
* **XROOTD_ECHO** (*bool, optional*) – Sets endpoint to redirector: ```xrootd.echo.stfc.ac.uk```
* **INT_MANAGER** (*bool, optional*) – Sets endpoint to redirector: ```echo-internal-manager01.gridpp.rl.ac.uk```

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns a dictionary containing the command outputs required by the given action. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The commands in TPCTest are generated and run as pairs, so the outputs are also in pairs. \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; All actions will return a dictionary containing the following key:value pairs:
* ```‘cmdOuts’: [((returncodeAB, stdoutAB, stderrAB, avgTimeAB), (returncodeBA, stdoutBA, stderrBA, avgTimeBA)), … ((returncodeAB, stdoutAB, stderrAB, avgTimeAB), (returncodeBA, stdoutBA, stderrBA, avgTimeBA))]``` – Returncode, stdout, stderr and avgTime in pairs of tuples for each command pair that was run
* ```‘IDs’: [‘example_ID1’, … ‘example_IDx’]``` – ID for each command/scenario in the format ‘protocol:sourceEndpoint-destinationEndpoint-file’
  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Additionally, the following actions will also contain extra key:value outputs:

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; *Checksum*: 
* ```‘cmdOuts’: [(stderrAB, stderrBA), … (stderrAB, stderrBA)]``` – Standard errors (without returncode and stdout) for each command pair that was run.
* ```‘destsums’ = [(checksumAB, checksumBA), … (checksumAB, checksumBA)]``` – Checksums for files on both sites in pairs.

&nbsp;&nbsp;&nbsp;&nbsp; **Return type:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; dictionary

