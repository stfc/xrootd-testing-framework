import asyncio
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from TPCTest import TPCTest as TPCopyTest
import pytest

class Test_TPCopy:
    ''' Transfer files from site A->B and site B->A, then compare checksums on both files '''
    def test_copy(self, cmdOuts, destsums, destderrs):
        returncodeAB, stdoutAB, stderrAB = cmdOuts[0]
        returncodeBA, stdoutBA, stderrBA = cmdOuts[1]
        destsumAB, destsumBA = destsums
        destderrAB, destderrBA = destderrs
        
        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"
        assert destsumAB == destsumBA, f"Stat failed: Source: {destsumAB}, Error: {destderrAB}, Dest: {destsumBA}, Error: {destderrBA}"

class Test_Empty_Transfer:
    ''' Transfer empty from site A->B and site B->A, then try to obtain checksums on both files '''
    def test_empty(self, destsums, destderrs):
        destsumAB, destsumBA = destsums
        destderrAB, destderrBA = destderrs
        assert destsumAB == None, f"Checksum of 0 bytes file should be None. Destsum: {destsumAB} Error: {destderrAB}"
        assert destsumBA == None, f"Checksum of 0 bytes file should be None. Destsum: {destsumBA} Error: {destderrBA}"

class Test_TPDelete:
    ''' Delete files from siteB and siteA, then try to obtain checksums on both files '''
    def test_deletion(self, cmdOuts, destsums, destderrs):
        returncodeAB, stdoutAB, stderrAB = cmdOuts[0]
        returncodeBA, stdoutBA, stderrBA = cmdOuts[1]
        destsumAB, destsumBA = destsums
        destderrAB, destderrBA = destderrs

        assert returncodeAB == 0, f"Deletion failed: {stderrAB}, {stdoutAB}"
        assert destsumAB == None and "file not found" or "no such file or directory" in destderrAB.casefold(), f"Deletion failed: Destsum: {destsumAB} Error: {destderrAB}"
       
        assert returncodeBA == 0, f"Deletion failed: {stderrBA}, {stdoutBA}"
        assert destsumBA == None and "file not found" or "no such file or directory" in destderrBA.casefold(), f"Deletion failed: Destsum: {destsumBA} Error: {destderrAB}"


''' Setup functions for each test'''
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    TPC = TPCopyTest(configFile='../TestClasses/ConfigTPC.yaml')
    test_name = metafunc.function.__name__
    class_name = metafunc.cls.__name__

    if class_name == "Test_TPCopy":
        if test_name == "test_copy":
            FILENAME = 'tst.txt'
            outputs = loop.run_until_complete(TPC.genScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force'))            
            destsums = loop.run_until_complete(TPC.genScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)

    elif class_name == "Test_Empty_Transfer":
        if test_name == "test_empty":
            FILENAME = '0bytes.txt'
            loop.run_until_complete(TPC.genScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force'))            
            destsums = loop.run_until_complete(TPC.genScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(destsums['destsums'], destsums['cmdOuts'])
            ids = destsums['IDs']
            metafunc.parametrize("destsums, destderrs", testCases, ids=ids)

    elif class_name == "Test_TPDelete":
        if test_name == "test_deletion":
            FILENAME = 'tst.txt'
            loop.run_until_complete(TPC.genScenarios('copy', sourcePath=f"../TestData/{FILENAME}", sourceBaseNm=FILENAME, destinBaseNm=FILENAME, xrdArgs=f'--force', gfalArgs='--force'))            
            outputs = loop.run_until_complete(TPC.genScenarios('delete', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))            
            destsums = loop.run_until_complete(TPC.genScenarios('checksum', sourceBaseNm=FILENAME, destinBaseNm=FILENAME))
            testCases = zip(outputs['cmdOuts'], destsums['destsums'], destsums['cmdOuts'])
            ids = outputs['IDs']
            metafunc.parametrize("cmdOuts, destsums, destderrs", testCases, ids=ids)
    TPC.cleanup()