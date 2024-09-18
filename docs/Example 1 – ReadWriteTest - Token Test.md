## Token Test Setup:
The setup for this test unsets the credentials, attempts to transfer a file to the endpoints, then resets the credentials.

Setup the ```pytest_generate_tests``` function:
~~~
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml", createFiles=False)
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__
~~~

Add the token test's setup code:
~~~
    if class_name == "Test_Token":
        if test_name == "test_copy_without_token":
            FILENAME = 'tst.txt'
Use unsetCreds method to unset environmental variable for token and voms_proxy:
            bearerToken = os.getenv("BEARER_TOKEN")
            x509User = os.getenv("X509_USER_PROXY")
            RWTest.unsetCreds('/tmp/x509up_*', bearerToken, x509User)
~~~

Transfer the file and obtain the outputs:
~~~
            outputs = loop.run_until_complete(RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, 
                        xrdArgs='--force', gfalArgs='--force'))

            testCases = outputs['cmdOuts']
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut", testCases, ids=ids)
~~~

Use resetCreds method to reset environmental variables for token and voms_proxy:
~~~
            RWTest.resetCreds('/tmp/x509up_*', bearerToken, x509User)
~~~


## Token Test Function:
Without the credentials, the returncode from the file transfer should fail, i.e. not equal 0:
~~~
class Test_Token:
    def test_copy_without_token(self, cmdOut):
        returncode, stdout, stderr = cmdOut
        assert returncode != 0; f"Upload Succeeded Without Token: {stdout}, {stderr}"
~~~

## Result:
~~~
$ pytest test_readwrite.py::Test_Token -v
~~~
![alt text](image-3.png)

