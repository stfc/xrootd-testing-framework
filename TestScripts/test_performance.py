import asyncio
import os
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from TPCTest import TPCTest as TPCopyTest
import pytest

BUFFER = 2 # Seconds
#UK Sites: 60 MB/s target, Non-UK 120 MB/s

class Test_Copy_Performance:
    ''' Transfer files to server, get avgTime taken for 3 transfers and compare to target rate '''
    def test_2GB(self, cmdOuts, destsums, destderrs):
        returncode, stdout, stderr, avgTime = cmdOuts
        UKtarget = (1024*2 / 60) + BUFFER
        NonUKtarget = (1024*2 / 120) + BUFFER
        throughput = 1024*2/avgTime
        assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
        assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
        assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"

    def test_40MB(self, cmdOuts, destsums, destderrs):
        returncode, stdout, stderr, avgTime = cmdOuts
        UKtarget = (40 / 60) + BUFFER
        NonUKtarget = (40 / 120) + BUFFER
        throughput = 40/avgTime
        assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
        assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
        assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"

class Test_Load_Copy:
    ''' Perform batch transfer of 2 files to server, get avgTime taken for 3 batch transfers and compare to target rate '''
    def test_40MB_100MB(self, cmdOuts, destsums, destderrs):
        returncode, stdout, stderr, avgTime = cmdOuts
        UKtarget = (40 / 60) + BUFFER
        NonUKtarget = (40 / 120) + BUFFER
        throughput = 40/avgTime
        assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
        assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
        assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"

class Test_TPCopy_Performance:
    ''' Transfer files from site A->B and site B->A, get avgTime taken for 3 transfers and compare to target rate '''
    def test_2GB(self, cmdOuts, destsums, destderrs):
        UKtarget = (1024*2 / 60) + BUFFER
        NonUKtarget = (1024*2 / 120) + BUFFER

        for i in range(len(cmdOuts)):
            returncode, stdout, stderr, avgTime = cmdOuts[i]
            throughput = 1024*2 /avgTime
            assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
            assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
            assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"

    def test_40MB(self, cmdOuts, destsums, destderrs):
        UKtarget = (40 / 60) + BUFFER # seconds
        NonUKtarget = (40 / 120) + BUFFER

        for i in range(len(cmdOuts)):
            returncode, stdout, stderr, avgTime = cmdOuts[i]
            throughput = 40 / avgTime 
            assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
            assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
            assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"

class Test_Deletion_Performance:
    ''' Delete files from endpoint, get avgTime taken for 3 deletions and compare to target rate '''
    def test_40MB(self, cmdOuts, destsums, destderrs):
        returncode, stdout, stderr, avgTime = cmdOuts
        UKtarget = (40 / 60) + BUFFER
        NonUKtarget = (40 / 120) + BUFFER
        throughput = 40/avgTime
        assert returncode == 0; f"Deletion failed: {stderr}, {stdout}"
        assert destsums == None and "file not found" or "no such file" in destderrs.casefold(), f"Deletion failed: Destsum: {destsums} Error: {destderrs}"
      
        assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
        assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"


class Test_TPDeletion_Performance:
    ''' Delete files from siteB and siteA, get avgTime taken for 3 deletions and compare to target rate '''
    def test_40MB(self, cmdOuts, destsums, destderrs):
        UKtarget = (40 / 60) + BUFFER # seconds
        NonUKtarget = (40 / 120) + BUFFER

        for i in range(len(cmdOuts)):
            returncode, stdout, stderr, avgTime = cmdOuts[i]
            destsum, destderr = destsums[i], destderrs[i]
            throughput = 40 / avgTime 
            assert returncode == 0; f"Deletion failed: {stderr}, {stdout}"
            assert destsum == None and "file not found" or "no such file" in destderr.casefold(), f"Deletion failed: Destsum: {destsum} Error: {destderr}"

            assert avgTime <= NonUKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {NonUKtarget}/ 120 MB/s"
            assert avgTime <= UKtarget; f"Throughput rate {throughput} MB/s did not reach target rate: {UKtarget}/ 60 MB/s"



''' Setup functions for each test'''
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    RWTest = ReadWriteTest(configFile="../TestClasses/ConfigReadWrite.yaml", createFiles=True)
    TPC = TPCopyTest(configFile='../TestClasses/ConfigTPC.yaml')
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__
    if class_name == 'Test_TPCopy_Performance': # Third-Party Copy setup
        if test_name == 'test_2GB': 
            FILENAME = 'tst2G.txt'
            outputs = loop.run_until_complete(TPC.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=50))            
            destsums = loop.run_until_complete(TPC.genTimedScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids) 

        elif test_name == 'test_40MB':
            FILENAME = 'tst40M.txt'
            outputs = loop.run_until_complete(TPC.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=8))            
            destsums = loop.run_until_complete(TPC.genTimedScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids) 

    elif class_name == 'Test_Load_Copy':
        if test_name == 'test_40MB_100MB':
            FILENAMES = ["../TestData/tst40M.txt", "../TestData/tst100M.txt"]
            outputs = loop.run_until_complete(RWTest.genTimedScenarios('load', sourcePath=FILENAMES, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=8))            
            destsums = loop.run_until_complete(RWTest.genTimedScenarios('checksum', destinBaseNm=FILENAMES))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)
    
    elif class_name == 'Test_Deletion_Performance':
        if test_name == 'test_40MB':
            FILENAME = 'tst40M.txt'
            loop.run_until_complete(RWTest.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=8))            
            outputs = loop.run_until_complete(RWTest.genTimedScenarios('delete', destinBaseNm=FILENAME, reps=3, timeout=8))            
            destsums = loop.run_until_complete(RWTest.genTimedScenarios('checksum', destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)

    elif class_name == 'Test_TPDeletion_Performance':
        if test_name == 'test_40MB':
            FILENAME = 'tst40M.txt'
            loop.run_until_complete(TPC.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', timeout=10)) 
            outputs = loop.run_until_complete(TPC.genTimedScenarios('delete', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))           
            destsums = loop.run_until_complete(TPC.genTimedScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids) 

    elif class_name == 'Test_Copy_Performance':
        if test_name == 'test_2GB':
            FILENAME = 'tst2G.txt'
            outputs = loop.run_until_complete(RWTest.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=50))            
            destsums = loop.run_until_complete(RWTest.genTimedScenarios('checksum', destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)

        if test_name == 'test_40MB':
            FILENAME = 'tst40M.txt'
            outputs = loop.run_until_complete(RWTest.genTimedScenarios('copy', sourcePath=f"../TestData/{FILENAME}", destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force', reps=3, timeout=8)) 
            destsums = loop.run_until_complete(RWTest.genTimedScenarios('checksum', destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)
    RWTest.cleanup()
    TPC.cleanup()
    