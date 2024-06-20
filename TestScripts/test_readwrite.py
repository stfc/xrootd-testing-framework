import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import subprocess
import pytest

def test_xrdcp_upload():
    copyTest = ReadWriteTest() #Initialise object
    copyTest.setup('xrdcp', '../TestData/tst.txt', 'dteam:/test/tst.txt', '--force') #Use setup method to organise parameters
    returncode, stdout, stderr = copyTest.subprocess() #Call subprocess to create the commands for each protocol + site, and run them
    #It will return the returncode, stdout, and stderr
    
    assert returncode == 0, f"Upload failed: {stderr}"

def test_xrd_checksums():
    checksumTest = ReadWriteTest()
    #checksumTest.setup('xrdfs', None, 'dteam:/test/tst.txt', 'query', 'checksum')
    source = checksumTest.xrdadler32('../TestData/tst2.txt')
    dest = checksumTest.xrdadler32('root://ceph-svc16.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt')

    assert dest == source, f"Source file checksum {source} does not match destination file checksum {dest}"


#def test_some_other():