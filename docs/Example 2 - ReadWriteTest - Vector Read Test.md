> **NOTE:** Currently this test can only use the root protocol, as the XRootD python client is used for vector reading.

Protocols can be toggled when creating the test object, however it is not required to do this for ```action='readv'```:
~~~
RWTestxrd = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml", davs=False, https=False)
~~~

## Vector Read Test Setup:
This test’s setup involves first transferring the files to the endpoints. 
Then, call genScenarios and pass `action=’readv’`, and `vector=[(0, 100)]` to obtain these chunks from the destination and source files.
~~~
    ...
    elif class_name == "Test_Vector_Read":
        if test_name == "test_chunks_0_100":
            FILENAME = 'tst.txt'

            loop.run_until_complete(RWTestxrd.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, 
                        xrdArgs='--force', gfalArgs='--force'))

            outputs = loop.run_until_complete(RWTestxrd.genScenarios('readv', 
                        sourcePath=f'../TestData/{FILENAME}', vector=[(0,10)]))

            testCases = zip(outputs['cmdOuts'], outputs['srcchunks'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, srcChunk", testCases, ids=ids)
~~~

## Vector Read Test Function:
For the test to pass, the returncode from the destination vector read should equal 0, and the source file and destination file’s chunks should match.
~~~
class Test_Vector_Read:
    def test_chunks_0_100(self, cmdOut, srcChunk):
        returncode, destChunk, stderr = cmdOut
        assert returncode == 0; f"Vector read of destination file failed. Error: {stderr}"
        assert srcChunk == destChunk; f"Vectors of local file and destination file do not match"
~~~

## Result:
~~~
$ pytest test_readwrite.py::Test_Token -v
~~~

![alt text](image-4.png)
