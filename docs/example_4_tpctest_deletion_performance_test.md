# Example 4 – TPCTest: Deletion (Performance) Test

## TPDeletion Test Setup:
This test setup uses the method ```genTimedScenarios``` to transfer a file from site A to site B, and then back. 
This method generates the commands, then runs each command (default: 3) times.
> **NOTE:** The TPCTest object will automatically transfer a local file to site A when using ```action='copy'``` 

Next, ```genTimedScenarios``` is used to delete the files from the destination, which is once again performed in triplicate, and timed. The outputs and average times are obtained.\
Finally, ```genTimedScenarios``` is used to checksum each deleted file on the two sites. The average time for the deletions is stored in the ```outputs[‘cmdOuts’]``` key.


~~~
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml")
    TPC = TPCopyTest(configFile='../TestClasses/ConfigTPC.yaml')
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__
~~~
[sic]
~~~
    elif class_name == 'Test_TPDeletion_Performance':
        if test_name == 'test_40MB':
            FILENAME = 'tst40M.txt'

            loop.run_until_complete(TPC.genScenarios('copy', sourcePath=f"../TestData/{FILENAME}", 
                                    sourceBaseNm=FILENAME, destinBaseNm=FILENAME, 
                                    xrdArgs=f'--force', gfalArgs='--force', timeout=10))

            outputs = loop.run_until_complete(TPC.genTimedScenarios('delete', 
                                    sourcePath=f"../TestData/{FILENAME}", 
                                    sourceBaseNm=FILENAME, destinBaseNm=FILENAME))           

            destsums = loop.run_until_complete(TPC.genScenarios('checksum', sourceBaseNm=FILENAME, 
                                    destinBaseNm=FILENAME))
            
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)

~~~

## TPDeletion Test Function:
This example test checks that the average deletion time is under a target time. The target time is calculated by dividing the file size in MB by the target rate(s) in MB/s. \
A buffer of 2 seconds is used to account for the time taken to establish and close the network connection. 

For each output in the pair: \
If the deletion’s returncode is 0, the destsums cannot be found due to a missing file, and the average time is below the target maximum time, then the test will pass.
~~~
class Test_Deletion_Performance:
    BUFFER = 2 #seconds
    # UK Sites: 60 MB/s target, Non-UK 120 MB/s
    def test_40MB(self, cmdOuts, destsums, destderrs):
        UKtarget = (40 / 60) + BUFFER #seconds
        NonUKtarget = (40 / 120) + BUFFER

        for i in range(len(cmdOuts)):
            returncode, stdout, stderr, avgTime = cmdOuts[i]
            destsum, destderr = destsums[i], destderrs[i]
            throughput = 40 / avgTime 
            assert returncode == 0; f"Deletion failed: {stderr}, {stdout}"
            assert destsum == None and "file not found" in destderr.casefold(), f"Deletion failed: Destsum: {destsum} Error: {destderr}"

            assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
            assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"
~~~

## Result:
~~~
$ pytest test_performance.py::Test_TPDeletion_Performance -v
~~~
![alt text]({{ site.baseurl }}/assets/css/images/image-6.png)
