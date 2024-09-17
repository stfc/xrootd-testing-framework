---
layout: default
---
## XRootD Testing Framework

### What This Framework Is For:
This framework is made to test XRootD functionalities and performance on pre-deployed endpoints. The purpose of these tests is to:
* Check that basic XRootD functionality works with the endpoint’s setup and configuration
  
* Benchmark the performance of file transfer and deletion


### Overview of How It Works:
The testing framework uses [Pytest](https://docs.pytest.org/en/7.1.x/contents.html) to parametrize and run the tests. Accessory classes are used to setup the data for the tests. The classes are organised into 3 types: **_ReadWriteTests_**, **_ThirdPartyCopyTests_** and **_MetadataTests_**, with attributes and methods specific to their type. 

To set up a test, a test object is created from the relevant class. This object stores the endpoints that will be tested against, the port(s), and the protocol. The method **_genScenarios_** is used to setup _functional_ tests, by generating XRootD (or gfal2) commands for each combination of protocol and endpoint. 

The commands will then be run asynchronously using the [asyncio-subprocess](https://docs.python.org/3/library/asyncio-subprocess.html) module, which return a returncode, stdout and stderr to be stored as results. Other outputs relevant to the type of command are also stored, such as checksums. Once the commands have been run, the outputs will be returned by genScenarios in a dictionary, under keys describing the type of output. 

For _performance_ tests, **_genTimedScenarios_** is used to:
* Get the start and end time of the command
* Re-run the command (default: 3) times
* Get the average time taken to run the commands

This average time is returned with the returncode, stdout and stderr.  
After setting up the test by running the relevant commands, the output data is used to [parametrise](https://docs.pytest.org/en/7.1.x/how-to/parametrize.html#basic-pytest-generate-tests-example) the Pytest test function. Each command is a scenario, and its output is used as a test case. 

## Installation
### Conda
The latest versions of [XRootD](https://github.com/xrootd/xrootd?tab=readme-ov-file), [XRootD Python client](https://pypi.org/project/xrootd/) and [gfal2](https://github.com/cern-fts/gfal2) packages are required to generate and run the tests.
  
Once the packages are installed, it is recommended that a conda environment is created to install relevant python modules and clone the repository. We recommend using either [miniconda](https://docs.anaconda.com/miniconda/miniconda-install/), which is a minimal installer for conda. 

Create a new conda environment with python version 3.9 or higher:
~~~ 
conda create -n xrd_tests python=3.9 
~~~

Activate the environment:
~~~ 
conda activate xrd_tests
~~~

Clone the repository and navigate into its root directory:
~~~	
git clone https://github.com/stfc/xrootd-testing-framework.git

cd xrootd-testing-framework
~~~

Install pip:
~~~
conda install pip
~~~
Install the required python modules:
~~~	
pip install -r requirements.txt
~~~
Finally, navigate to the TestScripts directory to modify or run test scripts:
~~~
cd TestScripts
pytest test_readwrite.py
~~~

### Docker
Alternatively, the framework environment can be run as a Docker container, and tests can be run within this container. The Docker image uses Rocky Linux 8 and can be downloaded on Harbour:

**_COMING SOON_**
