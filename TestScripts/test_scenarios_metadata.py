import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from MetadataTest import MetadataTest
import pytest

class Test_Metadata_Format:
    FILENAME = 'tst.txt'
    RWTest = ReadWriteTest()
    RWTest.subprocess('copy', f'../TestData/{FILENAME}', FILENAME, '--force') #Transfer file to destination

    MDTest = MetadataTest()
    scenarios = MDTest.subprocess('stat', None, FILENAME)

    @pytest.mark.parametrize("scenario", scenarios)
    def test_format(self, scenario):
        returncode, stdout, stderr, categs, toolCategs = scenario
        assert returncode == 0, f"Stat failed: {stderr}, {stdout}"
        assert categs == toolCategs, f"Metadata formats do not match. Expected: {toolCategs}, Actual: {categs}"

class Test_Metadata_Checksum:
    FILENAME = 'tst.txt'
    RWTest = ReadWriteTest()
    RWTest.subprocess('copy', f'../TestData/{FILENAME}', FILENAME, '--force')

    MDTest = MetadataTest()
    checksums = MDTest.subprocess('checksum', f'../TestData/{FILENAME}', FILENAME)

    @pytest.mark.parametrize("checksums", checksums)
    def test_endian(self, checksums):
        checksum, endian = checksums
        assert endian == 'BigEndian', f"Could not obtain endian format."