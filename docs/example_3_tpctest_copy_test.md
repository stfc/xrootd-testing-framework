# Example 3 – TPCTest: Copy Test

## TPCopy Test Setup:
This test setup transfers a file from site A to site B, and then back. Then, the checksums of both files are obtained. 
> **NOTE:** The TPCTest object will automatically transfer a local file to site A when using ```action='copy'``` 

 
First, setup the ```pytest_generate_tests``` function:
~~~
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    TPC = TPCopyTest(configFile='../TestClasses/ConfigTPC.yaml')
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__

    if class_name == "Test_TPCopy":
        if test_name == "test_copy":
            FILENAME = 'tst.txt'

            outputs = loop.run_until_complete(TPC.genScenarios('copy', sourcePath=f"../TestData/{FILENAME}", 
                    sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force'))

            destsums = loop.run_until_complete(TPC.genScenarios('checksum', sourceBaseNm=FILENAME,  
                    destinBaseNm=FILENAME))

            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)
~~~


## TPCopy Test Function:
The scenarios and their outputs for Third-Party Copy are treated as **pairs**. In the test, the copy from site A to site B and site B to site A should **both succeed**, and the checksums of the transferred files should match.
~~~
class Test_TPCopy:
    def test_copy(self, cmdOuts, destsums, destderrs):
        returncodeAB, stdoutAB, stderrAB = cmdOuts[0]
        returncodeBA, stdoutBA, stderrBA = cmdOuts[1]
        destsumAB, destsumBA = destsums
        destderrAB, destderrBA = destderrs
        
        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"
        assert destsumAB == destsumBA, f"Stat failed: Source: {destsumAB}, Error: {destderrAB}, Dest: {destsumBA}, Error: {destderrBA}"
~~~

## Result:
Example of test cases where tests fail:
~~~
$ pytest test_tpc.py::Test_TPCopy -v
~~~
![alt text]({{ site.baseurl }}/assets/css/images/image-5.png)
