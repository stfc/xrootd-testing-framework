# How To Setup and Write A Test
This section describes how to use the setup class *ReadWriteTest* to setup the data for the test, and how to write the test function itself.

## How To Setup A Test:
Setup, and naming of the test file and function follow the [pytest conventions](https://docs.pytest.org/en/stable/explanation/goodpractices.html): \
Pytest filenames, classes and test functions will start with ```test_*``` or ```Test_*```.

This example will look at how to write a test for a **copy** test using the *ReadWriteTest* class. \
For this copy test, we will need to:
* Copy the file to the destination(s) and get the returncode, stdout, and stderr 
* Obtain the checksum for the source and destination files
* Check the returncode status of the copy command is 0
* Check that the source file and destination file checksums match
  
In the test file, we define and use pytest’s ```pytest_generate_tests``` [function](https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_generate_tests) to write setup code for tests.  We can configure this function to run specific code before each of our test functions. 

First, define pytest_generate_tests:
~~~
def pytest_generate_tests(metafunc): 
~~~
Then, we store the name of the test class and test function, initialise the asyncio event loop, and the appropriate test object: 
~~~
def pytest_generate_tests(metafunc):
    class_name = metafunc.cls.__name__
    test_name = metafunc.function.__name__
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile=ConfigReadWrite.yaml)
~~~

Now, add an ‘if’ statement that ensures that the setup code runs before the test function is called. In this example, we will have a test class called ‘Test_Copy’, and the test function will be called ‘test_copy’:
~~~
    if class_name == "Test_Copy":
    if test_name == "test_copy":
~~~

Time to write the setup code – Under ```if test_name == "test_copy":```, let’s store the test file name as a variable, use the genScenarios method to copy that file to the endpoints, and store the outputs:
~~~
FILENAME = 'tst.txt'
outputs = loop.run_until_complete(RWTest.genScenarios('copy', sourcePath=f'../TestData/{FILENAME}', xrdArgs='--force', gfalArgs='--force'))
~~~
Here, we passed the optional arguments ```'--force'```, which will overwrite the server file if it already exists.

Next, we need to get the checksums of the files on the endpoints, and store those:
~~~
destsums = loop.run_until_complete(RWTest.genScenarios('checksum', destinBaseNm=FILENAME))
~~~
The outputs we have obtained are:
* ```outputs[‘IDs’] = [protocol:endpoint-file, … protocol:endpoint-file]```
* ```outputs[‘cmdOuts’] = [(returncode, stdout, stderr), … (returncode, stdout, stderr)]```
* ```outputs[‘srcsums’] = [checksum1, … checksumx]```
* ```destsums[‘destsums’] = [checksum1, … checksumx]```
* ```destsums[‘cmdOuts’] = [stderr1, … stderrx]```
  
For each list, the items at index 0 correspond to the first scenario, or test case. The items at index 1 correspond to the second, and so on. 

We can now [**parametrize**](https://docs.pytest.org/en/stable/example/parametrize.html) our test with these outputs using ```metafunc.parametrize```:
~~~
metafunc.parametrize("cmdOut, srcsums, destsums, destderrs", 
[outputs[‘cmdOuts’], outputs[‘srcsums’], destsums[‘destsums’], destsums[‘cmdOuts’]], ids=outputs[‘IDs’])
~~~

For a cleaner syntax, we can also use ‘zip’ to gather the outputs as ```testCases``` before passing them to ```metafunc.parametrize```:
~~~
testCases = zip(zip(outputs['cmdOuts'], outputs['srcsums']), destsums['destsums'], destsums['cmdOuts'])
metafunc.parametrize("cmdOut, destsums, destderrs", testCases, ids=outputs[‘IDs’])
~~~
Here, we grouped the ```srcsum``` into ```cmdOut``` with the returncode, stdout and stderr. NOTE: Any form of grouping is purely up to stylistic preference. \
Now that the data for the test is set up, we can write the test class and test function.

## Writing a test function:
In this framework, convention is to group the test functions into test classes, based on the functionality (i.e. action) type being tested.

In the same test file, add imports for the necessary modules at the top of the file:
~~~
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import pytest
import asyncio
~~~

Next, define the test class and within it, the test function. 
~~~
class Test_Copy:
    def test_copy(self):
~~~
When parametrizing the test, we passed the arguments:
```metafunc.parametrize("cmdOut, destsums, destderrs", testCases, ids=outputs[‘IDs’])```

Pass these same arguments to the test_copy function:
~~~
    def test_copy(self, cmdOut, destsum, destderr):
        (returncode, stdout, stderr), srcsum = cmdOut
~~~
We also unpacked the ```cmdOut``` argument to get the individual ```returncode, stdout, stderr``` and ```srcsum``` values for the scenario.

Now we can add the assert statements. For the copy test to pass, the copy command’s returncode should == 0, and the srcsum and destsum should match:
~~~
        assert returncode == 0, f"Upload Failed: {stdout}, {stderr}"
        assert srcsum == destsum, f"Stat failed: Source: {srcsum}, Dest: {destsum} Error: {destderr}"
~~~

&nbsp;

The full file should look like this:
~~~
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import pytest
import asyncio

class Test_Copy:
    def test_copy(self, cmdOut, destsum, destderr):
        (returncode, stdout, stderr), srcsum = cmdOut
        assert returncode == 0, f"Upload Failed: {stdout}, {stderr}"
        assert srcsum == destsum, f"Stat failed: Source: {srcsum}, Dest: {destsum} Error: {destderr}"

```Test setup:```
def pytest_generate_tests(metafunc):
    class_name = metafunc.cls.__name__
    test_name = metafunc.function.__name__
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile=ConfigReadWrite.yaml)
    if class_name == "Test_Copy":
    if test_name == "test_copy":
        FILENAME = 'tst.txt'
        outputs = loop.run_until_complete(RWTest.genScenarios('copy', sourcePath=f'../TestData/{FILENAME}', 
			xrdArgs='--force', gfalArgs='--force'))

	destsums = loop.run_until_complete(RWTest.genScenarios('checksum', destinBaseNm=FILENAME))

	testCases = zip(zip(outputs['cmdOuts'], outputs['srcsums']), 
			destsums['destsums'], destsums['cmdOuts'])

	metafunc.parametrize("cmdOut, destsums, destderrs", testCases, ids=outputs[‘IDs’])
~~~

The test can now be run in the command line:
~~~
$ pytest test_readwrite.py
~~~

The output will look like this: \
![alt text]({{ site.baseurl }}/assets/css/images/image-1.png)

We can also use the allure module to generate a more detailed report that can be shared. [See more about allure reports in pytest here](https://allurereport.org/docs/pytest/). \
When running the test file in the command line, use the flag ```--alluredir``` and specify a directory to store the results, then pass that directory to ```allure serve```:
~~~
$ pytest --alluredir=../Results test_readwrite.py
$ allure serve ../Results
~~~
