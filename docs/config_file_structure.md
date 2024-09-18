# Config File Structure
The configuration file is a .yaml file that can be used to specify endpoints, site paths and ports to the test object.

It is also possible to pass a directory, filename and file size, which can be generated during test setup.

A class-wide timeout can also be specified in the config file.

## Timeout
To specify a timeout (in seconds), add ```TIMEOUT:``` to the config file followed by the number of seconds:
~~~
TIMEOUT: 5
~~~
&nbsp;
## File Generation
To pass a directory and file generation information, the format is as follows:
~~~
DIRECTORY: ../TestData/bulkData/
FILES:
  - name: tst40M.txt 
    size: 41943040 
  - name: tst2K.txt
    size: 1024*20
~~~
File size is in bytes. It can be given in integers, or as an operation
> **NOTE:** The directory passed must end in a slash '/'

&nbsp;
## Adding Endpoints, Site Paths and Ports:

> **NOTE:** The site paths passed must end in a slash '/'

### ReadWriteTest and MetadataTest Config File:
For config files used for ReadWriteTest and MetadataTest classes, the format to specify sites is as follows:
~~~
SITES: # Destintation SitesList
  CEPH-SVC16:
      - ceph-svc16.gridpp.rl.ac.uk
      - dteam:/test/
      - 1095
  CEPH-SVC02:
       - ceph-svc02.gridpp.rl.ac.uk
       - dteam:/test/
~~~

Under ```SITES:```, specify the host/server name in capitals. 
Underneath it, pass the full endpoint, the site path (where the files will be transferred/deleted), and optionally, a port to use for this endpoint. If no port is specified, port ```1094``` will be used.

> These hostnames will be used to generate the test IDs  

---


### TPCTest Config File:
The sites in the TPCTest config file are divided into ```TEST_ENDPOINT```, which will be site A, and ```UK_SITE``` and (optional) ```NON_UK_SITE```, which are endpoints that will be tested against (i.e. site Bs). \
Under these categories, specify the host/server name, full endpoint path, site path and port as above: 
~~~
TEST_ENDPOINT: # SiteA 
    CEPH-SVC16:
        - ceph-svc16.gridpp.rl.ac.uk
        - dteam:/test/
         - 1094

UK_SITE: # SiteB
    CEPH-SVC30:
        - ceph-svc30.gridpp.rl.ac.uk
        - dteam:/test/

NON_UK_SITE: # SiteB
    GOLIAS100: 
        - golias100.farm.particle.cz
        - dpm/farm.particle.cz/home/dteam/test/
~~~
