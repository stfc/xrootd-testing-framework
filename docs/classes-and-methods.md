# Classes and Methods

This section documents the setup classes and methods.

## BaseTest Class:
The BaseTest class stores the protocols, endpoints and ports to generate scenarios with. Methods and attributes of this class are inherited by the subclasses: ReadWriteTest, MetadataTest and TPCTest

_class_ **BaseTest( _configFile_**=None, **_createFiles_**=False, **_root_**=True, **_https_**=True, **_davs_**=True **)**

A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 

Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with *createFiles*=True will generate these files in the provided directory.

To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

### BaseTest Methods:
This class has the following accessory methods that can be used for test setup/teardown by the user:

_method_ **xrdadler32( _filePath_ )**

Uses the xrdadler32 shell script to obtain an adler32 checksum of any single file. The checksum is hexadecimal and of type big-Endian.
 
&nbsp;&nbsp;&nbsp;&nbsp; **Parameters**:  
* **filePath** (*string*) – A path to the file, local or on the endpoint
  
&nbsp;&nbsp;&nbsp;&nbsp; **Returns**:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns the checksum as a string

&nbsp;&nbsp;&nbsp;&nbsp; **Return** type:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; String 

&nbsp;

_method_ **unsetCreds( _vomsProxy_**=None, **_bearerToken_**=None, **_x509User_**=None **)**

Temporarily removes the VOMS proxy token file from the given directory and copies it to a temporary location, and un-sets the BEARER_TOKEN and X509_USER_PROXY environmental variables.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters**:  
* **vomsProxy** (*string, optional*) – A path to the VOMS proxy file
* **bearerToken** (*string, optional*) – Value of the BEARER_TOKEN environmental variable
* **X509_USER_PROXY** (*string, optional*) – Value of the X509_USER_PROXY environmental variable
  
&nbsp;&nbsp;&nbsp;&nbsp; **Returns**: \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

&nbsp;

*method* **resetCreds( _vomsProxy_**=None, **_bearerToken_**=None, **_x509User_**=None **)**

Restores the VOMS proxy token file to the given directory, and resets the BEARER_TOKEN and X509_USER_PROXY environmental variables with the given values.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters**: 
* **vomsProxy** (*string, optional*) – A path to the VOMS proxy file
* **bearerToken** (*string, optional*) – Value of the BEARER_TOKEN environmental variable
* **X509_USER_PROXY** (*string, optional*) – Value of the X509_USER_PROXY environmental variable

&nbsp;&nbsp;&nbsp;&nbsp; **Returns**:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

&nbsp;

_method_ **cleanup()**

Removes the files generated from the configuration file when the class was instantiated.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters**: \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

&nbsp;&nbsp;&nbsp;&nbsp; **Returns**:\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

&nbsp;
## ReadWriteTest Class:
The ReadWriteTest class inherits from BaseTest class, and contains the main methods to create and run the test commands.
class ReadWriteTest(configFile=None, createFiles=False, root=True, https=True, davs=True)
A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 
Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with createFiles=True will generate these files in the provided directory.
To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass


method genScenarios(action, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs)
This method generates and runs commands for a given functionality, for each protocol and endpoint combination
Parameters:
•	action (string) – Functionality of the command. Expects a string of one of the following:
o	copy – copy a single file
o	checksum – get checksum of one or more destination files
o	delete – delete a single destination file
o	readv – vector read on source and destination file
o	load – batch transfer multiple files to destination
o	bulk-copy – transfer multiple files to destination one-by-one
o	bulk-delete – delete multiple destination files
•	sourcePath (string, list) – Path to local file. Can be list when action = ‘readv’, ‘load’ or ‘bulk-copy’
•	destinBaseNm (string, list) – Base name of file on endpoint. Can be list when action = ‘checksum’, ‘readv’ or ‘bulk-delete’
•	xrdArgs (string, optional) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
•	gfalArgs (string, optional) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
•	timeout (int, optional) – Optional timeout for all commands, overrides default (5 seconds)
•	XROOTD_ECHO (bool, optional) – Sets endpoint to redirector: xrootd.echo.stfc.ac.uk 
•	INT_MANAGER (bool, optional) – Sets endpoint to redirector: echo-internal-manager01.gridpp.rl.ac.uk
•	**readvArgs (list, optional) – A vector list in format [(0, 100), .. (0, 100)]

	Returns:
Returns a dictionary containing the command outputs required by the given action. All actions will return a dictionary containing the following key:value pairs:
•	‘cmdOuts’: [(returncode, stdout, stderr), … (returncode, stdout, stderr)] – Returncode, stdout and stderr in a tuple for each command that was run
•	‘IDs’: [‘example_ID1’, … ‘example_IDx’] – ID for each command/scenario in the format ‘protocol:endpoint-file’
Additionally, the following actions will also contain extra key:value outputs:
		Copy and bulk-copy:
•	‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
Checksum: 
•	‘cmdOuts’: [(stderr1, stderr2), … (stderr1, stderr2)] – Standard error (without returncode and stdout) for each command that was run. Grouped into tuples if multiple files are passed to destinBaseNm.
•	‘destsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each destination file. Grouped into tuples if multiple files are passed to destinBaseNm.
Load:
•	‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
•	‘redirects’ = [(‘site1’, ‘site2’), … (‘site1’, ‘site2’)] – Sites that were redirected to, populated if redirectors XROOTD_ECHO=True or INT_MANAGER=True
	Return type:
		dictionary

method genTimedScenarios(action, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=3, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs)
This method generates and runs commands for a given functionality, for each protocol and endpoint combination. Each command is run for several repetitions (reps) and timed. An average of this time is returned with the output.
Parameters:
•	action (string) – Functionality of the command. Expects a string of one of the following:
o	copy – copy a single file
o	checksum – get checksum of one or more destination files
o	delete – delete a single destination file
o	readv – vector read on source and destination file
o	load – batch transfer multiple files to destination
o	bulk-copy – transfer multiple files to destination one-by-one
o	bulk-delete – delete multiple destination files
•	sourcePath (string, list) – Path to local file. Can be list when action = ‘readv’, ‘load’ or ‘bulk-copy’
•	destinBaseNm (string, list) – Base name of file on endpoint. Can be list when action = ‘checksum’, ‘readv’ or ‘bulk-delete’
•	xrdArgs (string, optional) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
•	gfalArgs (string, optional) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
•	reps (int, optional) – Set number of repetitions for each command to run, overrides default (3)
•	timeout (int, optional) – Optional timeout for all commands, overrides default (5 seconds)
•	XROOTD_ECHO (bool, optional) – Sets endpoint to redirector: xrootd.echo.stfc.ac.uk 
•	INT_MANAGER (bool, optional) – Sets endpoint to redirector: echo-internal-manager01.gridpp.rl.ac.uk
•	**readvArgs (list, optional) – A vector list in format [(0, 100), .. (0, 100)]

	Returns:
Returns a dictionary containing the command outputs required by the given action. All actions will return a dictionary containing the following key:value pairs:
•	‘cmdOuts’: [(returncode, stdout, stderr, avgTime), … (returncode, stdout, stderr, avgTime)] – Returncode, stdout, stderr and avgTime in a tuple for each command that was run
•	‘IDs’: [‘example_ID1’, … ‘example_IDx’] – ID for each command/scenario in the format ‘protocol:endpoint-file’
Additionally, the following actions will also contain extra key:value outputs:
		Copy and bulk-copy:
•	‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
Checksum: 
•	‘cmdOuts’: [(stderr1, stderr2), … (stderr1, stderr2)] – Standard error (without returncode and stdout) for each command that was run. Grouped into tuples if multiple files are passed to destinBaseNm.
•	‘destsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each destination file. Grouped into tuples if multiple files are passed to destinBaseNm.
Load:
•	‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
•	‘redirects’ = [(‘site1’, ‘site2’), … (‘site1’, ‘site2’)] – Sites that were redirected to, populated if redirectors XROOTD_ECHO=True or INT_MANAGER=True
	Return type:
		dictionary


MetadataTest Class:
The MetadataTest class inherits from BaseTest class, and contains the main methods to create and run the test commands.
class MetadataTest(configFile=None, createFiles=False, root=True, https=True, davs=True)
A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 
Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with createFiles=True will generate these files in the provided directory.
To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

method genScenarios(action, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False)
This method generates and runs commands for a given functionality, for each protocol and endpoint combination
Parameters:
•	action (string) – Functionality of the command. Expects a string of one of the following:
o	copy – copy a single file
o	checksum – get checksum of one or more destination files
o	delete – delete a single destination file
o	bulk-copy – transfer multiple files to destination one-by-one
o	bulk-delete – delete multiple destination files
o	stat – compare metadata categories on destination file to expected categories 
•	sourcePath (string, list) – Path to local file. Can be list when action = ‘readv’, ‘load’ or ‘bulk-copy’
•	destinBaseNm (string, list) – Base name of file on endpoint. Can be list when action = ‘checksum’, ‘readv’ or ‘bulk-delete’
•	xrdArgs (string, optional) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
•	gfalArgs (string, optional) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
•	timeout (int, optional) – Optional timeout for all commands, overrides default (5 seconds)
•	XROOTD_ECHO (bool, optional) – Sets endpoint to redirector: xrootd.echo.stfc.ac.uk 
•	INT_MANAGER (bool, optional) – Sets endpoint to redirector: echo-internal-manager01.gridpp.rl.ac.uk
	Returns:
Returns a dictionary containing the command outputs required by the given action. All actions will return a dictionary containing the following key:value pairs:
•	‘cmdOuts’: [(returncode, stdout, stderr), … (returncode, stdout, stderr)] – Returncode, stdout and stderr in a tuple for each command that was run
•	‘IDs’: [‘example_ID1’, … ‘example_IDx’] – ID for each command/scenario in the format ‘protocol:endpoint-file’
Additionally, the following actions will also contain extra key:value outputs:
		Copy and bulk-copy:
•	‘srcsums’ = [(file1-checksum, file2-checksum), … (file1-checksum, file2-checksum)] – Checksum for each local file. Grouped into tuples if multiple files are passed to sourcePath.
Checksum: 
•	‘cmdOuts’: [(stderr1, stderr2), … (stderr1, stderr2)] – Standard error (without returncode and stdout) for each command that was run. Grouped into tuples if multiple files are passed to destinBaseNm.
•	‘destsums’ = [((file1-checksum, endian-ness), (file2-checksum, endian-ness)), … ((file1-checksum, endian-ness), (file2-checksum, endian-ness))] – Checksum and Endian-ness for each destination file. Grouped into tuples if multiple files are passed to destinBaseNm.
Stat:
•	‘cmdOuts’: [(returncode, stdout, stderr, categories, expectedCategories), … (returncode, stdout, stderr, categories, expectedCategories)] – Returncode, stdout, stderr, list of metadata categories of file on destination, list of expected categories
	Return type:
		dictionary

TPCTest Class:
The TPCTest class inherits from BaseTest class, and contains the main methods to create and run the test commands.
class TPCTest(configFile=None, createFiles=False, root=True, https=True, davs=True)
A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 
Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with createFiles=True will generate these files in the provided directory.
To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

method genScenarios(action, sourcePath=None, sourceBaseNm=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs)
This method generates and runs commands for a given functionality, for each protocol and endpoint combination. These functionalities are performed on endpoint A and endpoint B, therefore the commands and their outputs are treated as pairs.
Parameters:
•	action (string) – Functionality of the command. Expects a string of one of the following:
o	copy – copy a single file
o	checksum – get checksum of one or more destination files
o	delete – delete a single destination file
•	sourcePath (string) – Path to local file. Used to transfer local file to source endpoint
•	sourceBaseNm (string) – Base name of file on source endpoint.
•	destinBaseNm (string) – Base name of file on destination endpoint.
•	xrdArgs (string, optional) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
•	gfalArgs (string, optional) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
•	TestAll (bool, optional) – If set to True, will test all sites specified as TEST_ENDPOINTS in config file (i.e. all ‘Site A’s)
•	timeout (int, optional) – Optional timeout for all commands, overrides default (5 seconds)
	Returns:
Returns a dictionary containing the command outputs required by the given action. The commands in TPCTest are generated and run as pairs, so the outputs are also in pairs. All actions will return a dictionary containing the following key:value pairs:
•	‘cmdOuts’: [((returncode, stdout, stderr), (returncode, stdout, stderr)), … ((returncode, stdout, stderr), (returncode, stdout, stderr))] – Returncode, stdout and stderr in pairs of tuples for each command pair that was run
•	‘IDs’: [‘example_ID1’, … ‘example_IDx’] – ID for each command/scenario in the format ‘protocol:sourceEndpoint-destinationEndpoint-file’
Additionally, the following actions will also contain extra key:value outputs:
Checksum: 
•	‘cmdOuts’: [(stderrAB, stderrBA), … (stderrAB, stderrBA)] – Standard errors (without returncode and stdout) for each command pair that was run.
•	‘destsums’ = [(checksumAB, checksumBA), … (checksumAB, checksumBA)] – Checksums for files on both sites in pairs.
	Return type:
		dictionary

method genTimedScenarios(action, sourcePath=None, destinBaseNm=None, xrdArgs=None, gfalArgs=None, reps=3, timeout=None, XROOTD_ECHO=False, INT_MANAGER=False, **readvArgs)
This method generates and runs commands for a given functionality, for each protocol and endpoint combination. These functionalities are performed on endpoint A and endpoint B, therefore the commands and their outputs are treated as pairs. Each command pair is run for several repetitions (reps) and timed. An average of the time is returned with the output.
Parameters:
•	action (string) – Functionality of the command. Expects a string of one of the following:
o	copy – copy a single file
o	checksum – get checksum of one or more destination files
o	delete – delete a single destination file
•	sourcePath (string) – Path to local file. Used to transfer local file to source endpoint
•	sourceBaseNm (string) – Base name of file on source endpoint.
•	destinBaseNm (string) – Base name of file on destination endpoint.
•	xrdArgs (string, optional) – Extra flag(s) to be added to the generated base command of the action, for XRootD commands
•	gfalArgs (string, optional) - Extra flag(s) to be added to the generated base command of the action, for gfal2 commands
•	reps (int, optional) – Set number of repetitions for each command to run, overrides default (3)
•	timeout (int, optional) – Optional timeout for all commands, overrides default (5 seconds)
•	XROOTD_ECHO (bool, optional) – Sets endpoint to redirector: xrootd.echo.stfc.ac.uk 
•	INT_MANAGER (bool, optional) – Sets endpoint to redirector: echo-internal-manager01.gridpp.rl.ac.uk

	Returns:
Returns a dictionary containing the command outputs required by the given action. The commands in TPCTest are generated and run as pairs, so the outputs are also in pairs. All actions will return a dictionary containing the following key:value pairs:
•	‘cmdOuts’: [((returncode, stdout, stderr, avgTime), (returncode, stdout, stderr, avgTime)), … ((returncode, stdout, stderr, avgTime), (returncode, stdout, stderr, avgTime))] – Returncode, stdout, stderr and avgTime in pairs of tuples for each command pair that was run
•	‘IDs’: [‘example_ID1’, … ‘example_IDx’] – ID for each command/scenario in the format ‘protocol:sourceEndpoint-destinationEndpoint-file’
Additionally, the following actions will also contain extra key:value outputs:
Checksum: 
•	‘cmdOuts’: [(stderrAB, stderrBA), … (stderrAB, stderrBA)] – Standard errors (without returncode and stdout) for each command pair that was run.
•	‘destsums’ = [(checksumAB, checksumBA), … (checksumAB, checksumBA)] – Checksums for files on both sites in pairs.
	Return type:
		dictionary
