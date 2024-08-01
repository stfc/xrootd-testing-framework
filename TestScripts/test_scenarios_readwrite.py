import os
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import time
import pytest

#Transfer file, check data/checksum on server is the same as local
class Test_Copy:
    FILENAME = 'tst.txt'
    RWTest = ReadWriteTest()
    sourcesum = RWTest.xrdadler32(f'../TestData/{FILENAME}')
    scenarios = RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force')
    destsum = RWTest.genScenarios('checksum', None, FILENAME) #xrd=['query', 'checksum'], gfal=['ADLER32'])

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_copy(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        sourcesum = self.sourcesum
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert destsum == sourcesum, f"Stat failed: Mismatching checksums. Source: {sourcesum}, Dest: {destsum}"


    FILENAME = 'tst100K.txt'
    XRATE = '50k'
    fileSize = os.stat(f'../TestData/{FILENAME}').st_size
    scenarios = RWTest.genTimedScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force', '--xrate', XRATE)
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_xrate_copy(self, scenario):
        expectTime = 2
        returncode, stdout, stderr, avgTime = scenario
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert  expectTime+1 >= avgTime >= expectTime-1


    scenarios = RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--posc', '--xrate', XRATE, '--force', timeout=1)
    destsum = RWTest.genScenarios('checksum', None, FILENAME)

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_posc_deletion(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        assert returncode != 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None, f"Deletion failed: Checksum still present {destsum}"


    scenarios = RWTest.genScenarios('load', f'../TestData/{FILENAME}', FILENAME)
    
    @pytest.mark.parametrize(("scenario"), (scenarios))
    def test_load_redirection(self, scenario): #test needs adjusting
        returncode, stdout, stderr = scenario
        assert returncode != 0, f"Upload failed: {stderr}, {stdout}"


class Test_Empty_Transfer:
    FILENAME = '0bytes.txt'
    RWTest = ReadWriteTest()
    RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force')
    destsum = RWTest.genScenarios('checksum', None, FILENAME)
    
    @pytest.mark.parametrize(("destsum"), destsum)
    def test_empty(self, destsum):
        assert destsum == None, f"Checksum of 0 bytes file should be None. {destsum}"


# class Test_ATLAS_Token:
#     FILENAME = 'tst.txt'
#     #First test - attempt transfer without token
#     RWTest = ReadWriteTest('../TestData/ConfigReadWrite.yaml')
#     scenarios = RWTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force')
    
    #Second test - generate token, then attempt transfer
    #Set env variable for token
    #clear variable for voms
    #reset voms at end of test


class Test_Delete:
    FILENAME = 'tst.txt'
    RWTest = ReadWriteTest()
    scenarios = RWTest.genScenarios('delete', None, FILENAME, 'rm')
    destsum = RWTest.genScenarios('checksum', None, FILENAME)

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_deletion(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        assert returncode == 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None, f"Deletion failed: Checksum still present {destsum}"
