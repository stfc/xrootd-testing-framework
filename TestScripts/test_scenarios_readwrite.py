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
    scenarios = RWTest.subprocess('copy', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--force')
    destsum = RWTest.subprocess('checksum', None, f'dteam:/test/{FILENAME}', 'query', 'checksum')

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_copy(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        sourcesum = self.sourcesum
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert destsum == sourcesum, f"Stat failed: Mismatching checksums. Source: {sourcesum}, Dest: {destsum}"

    FILENAME = 'tst100K.txt'
    XRATE = '50k'
    fileSize = os.stat(f'../TestData/{FILENAME}').st_size
    scenarios = RWTest.timed('copy', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--force', '--xrate', XRATE)
    destsum = RWTest.subprocess('checksum', None, f'dteam:/test/{FILENAME}', 'query', 'checksum')
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_xrate_copy(self, scenario):
        expectTime = 2
        returncode, stdout, stderr, avgTime = scenario
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert  expectTime+1 >= avgTime >= expectTime-1


    scenarios = RWTest.subprocess('copy', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--posc', '--xrate', XRATE, '--force', timeout=1)
    destsum = RWTest.subprocess('checksum', None, f'dteam:/test/{FILENAME}', 'query', 'checksum')

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_posc_deletion(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        assert returncode != 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None, f"Deletion failed: Checksum still present {destsum}"


    scenarios = RWTest.subprocess('load', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--force')

    @pytest.mark.parametrize("scenario", scenarios)
    def load_redirection(self, scenario): #test needs adjusting
        returncode, stdout, stderr = scenario
        assert returncode != 0, f"Deletion failed: {stderr}, {stdout}"


class Test_Empty_Transfer:
    FILENAME = '0bytes.txt'
    RWTest = ReadWriteTest()
    RWTest.subprocess('copy', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--force')
    destsum = RWTest.subprocess('checksum', None, f'dteam:/test/{FILENAME}', 'query', 'checksum')
    
    @pytest.mark.parametrize(("destsum"), destsum)
    def test_empty(self, destsum):
        assert destsum == None, f"Checksum of 0 bytes file should be None. {destsum}"


# class Test_ATLAS_Token:
#     FILENAME = 'tst.txt'
#     #First test - attempt transfer without token
#     RWTest = ReadWriteTest('../TestData/ConfigReadWrite.yaml')
#     scenarios = RWTest.subprocess('copy', f'../TestData/{FILENAME}', f'dteam:/test/{FILENAME}', '--force')
    
    #Second test - generate token, then attempt transfer
    #Set env variable for token
    #clear variable for voms
    #reset voms at end of test


class Test_Delete:
    FILENAME = 'tst.txt'
    RWTest = ReadWriteTest()
    scenarios = RWTest.subprocess('delete', None, f'dteam:/test/{FILENAME}', 'rm')
    destsum = RWTest.subprocess('checksum', None, f'dteam:/test/{FILENAME}', 'query', 'checksum')

    @pytest.mark.parametrize(("scenario, destsum"), zip(scenarios, destsum))
    def test_deletion(self, scenario, destsum):
        returncode, stdout, stderr = scenario
        assert returncode == 0, f"Deletion failed: {stderr}, {stdout}"
        assert destsum == None, f"Deletion failed: Checksum still present {destsum}"
