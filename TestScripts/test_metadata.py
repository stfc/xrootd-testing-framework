import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from MetadataTest import MetadataTest
import pytest
import asyncio 

loop = asyncio.get_event_loop()

class Test_Metadata_Format:
    ''' Transfer files to endpoints, then stat files and compare metadata format to expected '''
    def test_format(self, cmdOut):
        returncode, stdout, stderr, categs, toolCategs = cmdOut
        assert returncode == 0, f"Stat failed: {stderr}, {stdout}"
        assert categs == toolCategs, f"Metadata formats do not match. Expected: {toolCategs}, Actual: {categs}"

class Test_Metadata_Checksum:
    ''' Transfer files to endpoints, determine endian-ness of destination checksum'''
    def test_endian(self, destsum, destderr):
        checksum, endian = destsum
        assert endian == 'BigEndian', f"Checksum: {checksum} Error: {destderr}"


''' Setup functions for each test'''
def pytest_generate_tests(metafunc):
    loop = asyncio.get_event_loop()
    MDTest = MetadataTest(configFile="../TestClasses/ConfigReadWrite.yaml")
    test_name = metafunc.function.__name__

    if test_name == "test_format":
        FILENAME = 'tst.txt'
        loop.run_until_complete(MDTest.genScenarios('copy', f'../TestData/{FILENAME}', FILENAME, xrdArgs='--force', gfalArgs='--force')) #Transfer file to destination
        outputs = loop.run_until_complete(MDTest.genScenarios('stat', None, FILENAME))
        testCases = outputs['cmdOuts']
        ids = outputs['IDs']
        metafunc.parametrize("cmdOut", testCases, ids=ids)

    elif test_name == "test_endian":
        FILENAME = 'tst.txt'
        outputs = loop.run_until_complete(MDTest.genScenarios('checksum', f'../TestData/{FILENAME}', FILENAME))
        testCases = zip(outputs['destsums'], outputs['cmdOuts'])
        ids = outputs['IDs']
        metafunc.parametrize("destsum, destderr", testCases, ids=ids)
    MDTest.cleanup()