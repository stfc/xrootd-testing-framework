import os
import re
import sys   
import shutil
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import pytest
import asyncio

class Test_Copy:
    ''' Transfer files to endpoints via root, https and davs, then compare checksum on server files to local file '''
    def test_copy(self, cmdOut, destsum, destderr):
        (returncode, stdout, stderr), srcsum = cmdOut
        assert returncode == 0, f"Upload Failed: {stdout}, {stderr}"
        assert srcsum == destsum, f"Stat failed: Source: {srcsum}, Dest: {destsum} Error: {destderr}"

    ''' Transfer files to XROOTD_ECHO, obtain checksum to see if transfer was redirected to other sites '''
    def test_load_redirection(self, cmdOut, destsums, destderrs): 
        (returncode, stdout, stderr), srcsums = cmdOut
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert srcsums == destsums, f"Stat failed: Source: {srcsums}, Dest: {destsums} Error: {destderrs}"

    ''' root-only: Transfer files and specify xrate, measure average time for transfer, check that it is within expected time range '''
    def test_xrate_copy(self, cmdOut):
        returncode, stdout, stderr, avgTime = cmdOut
        expectTime = 40/10
        lowerBound = expectTime - (expectTime*0.15)
        upperBound = expectTime + (expectTime*0.15)

        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert upperBound >= avgTime >= lowerBound, f"Rate {avgTime} not capped to expected range: {lowerBound} - {upperBound}"

    ''' root-only: Force transfer to terminate early by setting xrate and timeout, stat checksum to verify that file was deleted from server '''
    def test_posc_deletion(self, cmdOut, destsum, destderr):
        returncode, stdout, stderr = cmdOut
        assert returncode != 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None, f"Deletion failed: Destsum: {destsum} Error: {destderr}"

class Test_Empty_Transfer:
    ''' Transfer file of 0 bytes, stat checksum of file on server to verify transfer failed '''
    def test_empty(self, destsum, destderr):
        assert destsum == None, f"Checksum of 0 bytes file should be None. Destsum: {destsum} Error: {destderr}"

class Test_Token:
    ''' Attempt to transfer file. Check returncode != 0 to verify transfer without token failed '''
    def test_copy_without_token(self, cmdOut):
        returncode, stdout, stderr = cmdOut
        assert returncode != 0; f"Upload Succeeded Without Token: {stdout}, {stderr}"

class Test_Vector_Read:
   
    def test_chunks_0_100(self, cmdOut, srcChunk):
        returncode, destChunk, stderr = cmdOut
        assert returncode == 0; f"Vector read of destination file failed. Error: {stderr}"
        assert srcChunk == destChunk; f"Vectors of local file and destination file do not match"

    def test_bug_chunks(self, cmdOut, srcChunk):
        returncode, destChunk, stderr = cmdOut
        assert returncode == 0; f"Vector read of destination file failed. Error: {stderr}"
        assert srcChunk == destChunk; f"Vectors of local file and destination file do not match"

        
class Test_Delete:
    ''' Transfer files to servers, then delete. Stat checksums to verify deletion '''
    def test_deletion(self, cmdOut, destsum, destderr):
        returncode, stdout, stderr = cmdOut
        assert returncode == 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None and "file not found" or "no such file or directory" in destderr.casefold(), f"Deletion failed: Destsum: {destsum} Error: {destderr}"



''' Setup functions for each test'''
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml", createFiles=False)
    RWTestxrd = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml", davs=False, https=False)
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__

    if class_name == "Test_Copy":
        if test_name == "test_copy":
            FILENAME = 'tst.txt'
            outputs = loop.run_until_complete(RWTest.genScenarios('copy', sourcePath=f'../TestData/{FILENAME}', 
                                                                  xrdArgs='--force', gfalArgs='--force'))
            destsums = loop.run_until_complete(RWTest.genScenarios('checksum', destinBaseNm=FILENAME))
            testCases = zip(zip(outputs['cmdOuts'], outputs['srcsums']), destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, destsum, destderr", testCases, ids=ids)

        elif test_name == "test_load_redirection":
            outputs = loop.run_until_complete(RWTest.genScenarios('load', sourcePath='../TestData/bulkData/*', 
                                                                  xrdArgs='--force', gfalArgs='--force', XROOTD_ECHO=True)) # Load
            destsums = loop.run_until_complete(RWTest.genScenarios('checksum', destinBaseNm='../TestData/bulkData/*', XROOTD_ECHO=True))
            testCases = zip(zip(outputs['cmdOuts'], outputs['srcsums']), destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, destsums, destderrs", testCases, ids=ids)

        elif test_name == "test_xrate_copy":
            FILENAME = 'tst40M.txt'
            XRATE = '10M'
            outputs = loop.run_until_complete(RWTestxrd.genTimedScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs=f'--force,--xrate,{XRATE}'))
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut", outputs['cmdOuts'], ids=ids)

        elif test_name == "test_posc_deletion":
            FILENAME = 'tst40M.txt'
            XRATE = '10M'
            outputs = loop.run_until_complete(RWTestxrd.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs=f'--posc,--xrate,{XRATE},--force', timeout=1))
            destsums = loop.run_until_complete(RWTestxrd.genScenarios('checksum', destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, destsum, destderr", testCases, ids=ids)

    elif class_name == "Test_Empty_Transfer":
        if test_name == "test_empty":
            FILENAME = '0bytes.txt'   
            loop.run_until_complete(RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs='--force', gfalArgs='--force'))
            destsums = loop.run_until_complete(RWTest.genScenarios('checksum', None, FILENAME))
            ids = destsums['IDs']
            metafunc.parametrize("destsum, destderr", zip(destsums['destsums'], destsums['cmdOuts']), ids=ids)

    elif class_name == "Test_Token":
        if test_name == "test_copy_without_token":
            FILENAME = 'tst.txt'

            ''' Unset environmental variable for token and voms_proxy '''
            bearerToken = os.getenv("BEARER_TOKEN")
            x509User = os.getenv("X509_USER_PROXY")
            RWTest.unsetCreds('/tmp/x509up_*', bearerToken, x509User)

            outputs = loop.run_until_complete(RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs='--force', gfalArgs='--force'))
            testCases = outputs['cmdOuts']
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut", testCases, ids=ids)

            ''' Reset environmental variables for token and voms_proxy '''
            RWTest.resetCreds('/tmp/x509up_*', bearerToken, x509User)

    elif class_name == "Test_Vector_Read":
        if test_name == "test_chunks_0_100":
            FILENAME = 'tst.txt'
            loop.run_until_complete(RWTestxrd.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs='--force', gfalArgs='--force'))
            outputs = loop.run_until_complete(RWTestxrd.genScenarios('readv', sourcePath=f'../TestData/{FILENAME}', vector=[(0,10)]))
            testCases = zip(outputs['cmdOuts'], outputs['srcchunks'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, srcChunk", testCases, ids=ids)

        elif test_name == "test_bug_chunks":
            # File size must be larger than (BUFFERSIZE + 100)
            FILENAME = 'tst40M.txt' # 40 MB 
            BUFFERSIZE = 1024*1024 # 1 MB
            loop.run_until_complete(RWTestxrd.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs='--force', gfalArgs='--force'))
            outputs = loop.run_until_complete(RWTestxrd.genScenarios('readv', sourcePath=f'../TestData/{FILENAME}', bufferSize=1024*1024, vector=[(100, 271), (20, BUFFERSIZE+100), (500, 370)]))
            testCases = zip(outputs['cmdOuts'], outputs['srcchunks'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, srcChunk", testCases, ids=ids)

    elif class_name == "Test_Delete":
        if test_name == "test_deletion":
            FILENAME = 'tst.txt'   
            loop.run_until_complete(RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME))
            outputs = loop.run_until_complete(RWTest.genScenarios('delete', None, FILENAME))
            destsums = loop.run_until_complete(RWTest.genScenarios('checksum', None, FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOut, destsum, destderr", testCases, ids=ids)

    RWTest.cleanup()