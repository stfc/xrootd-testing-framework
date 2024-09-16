## XRootD Testing Framework

### What This Framework Is For:
This framework is made to test XRootD functionalities and performance on pre-deployed endpoints. The purpose of these tests is to:
* Check that basic XRootD functionality works with the endpoint’s setup and configuration
  
* Benchmark the performance of file transfer and deletion

Link to Documentation: https://stfc.github.io/xrootd-testing-framework/ 

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
