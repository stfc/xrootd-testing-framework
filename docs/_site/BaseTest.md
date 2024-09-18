# BaseTest

## BaseTest Class:
The BaseTest class stores the protocols, endpoints and ports to generate scenarios with. Methods and attributes of this class are inherited by the subclasses: ReadWriteTest, MetadataTest and TPCTest

_class_ **BaseTest( _configFile_**=None, **_createFiles_**=False, **_root_**=True, **_https_**=True, **_davs_**=True **)**

A configuration file can be passed upon instantiation of the subclasses containing the endpoint, file path and optional port. 

Optionally, specifying a directory, file name(s) and file size(s) in the config file and instantiating with ```createFiles=True``` will generate these files in the provided directory.

To exclude up to two of the protocols from being used, they can be toggled to False when instantiating the subclass

### BaseTest Methods:
___
This class has the following accessory methods that can be used for test setup/teardown by the user:

_method_ **xrdadler32( _filePath_ )**

Uses the xrdadler32 shell script to obtain an adler32 checksum of any single file. The checksum is hexadecimal and of type big-Endian.
 
&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**  
* **filePath** (*string*) – A path to the file, local or on the endpoint
  
&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Returns the checksum as a string

&nbsp;&nbsp;&nbsp;&nbsp; **Return type:**  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; String 

___

_method_ **unsetCreds( _vomsProxy_**=None, **_bearerToken_**=None, **_x509User_**=None **)**

Temporarily removes the VOMS proxy token file from the given directory and copies it to a temporary location, and un-sets the ```BEARER_TOKEN``` and ```X509_USER_PROXY``` environmental variables.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:**  
* **vomsProxy** (*string, optional*) – A path to the VOMS proxy file
* **bearerToken** (*string, optional*) – Value of the ```BEARER_TOKEN``` environmental variable
* **X509_USER_PROXY** (*string, optional*) – Value of the ```X509_USER_PROXY``` environmental variable
  
&nbsp;&nbsp;&nbsp;&nbsp; **Returns:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

___

*method* **resetCreds( _vomsProxy_**=None, **_bearerToken_**=None, **_x509User_**=None **)**

Restores the VOMS proxy token file to the given directory, and resets the ```BEARER_TOKEN``` and ```X509_USER_PROXY``` environmental variables with the given values.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:** 
* **vomsProxy** (*string, optional*) – A path to the VOMS proxy file
* **bearerToken** (*string, optional*) – Value of the ```BEARER_TOKEN``` environmental variable
* **X509_USER_PROXY** (*string, optional*) – Value of the ```X509_USER_PROXY``` environmental variable

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

___

_method_ **cleanup()**

Removes the files generated from the configuration file when the class was instantiated.

&nbsp;&nbsp;&nbsp;&nbsp; **Parameters:** \
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

&nbsp;&nbsp;&nbsp;&nbsp; **Returns:**\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; None

