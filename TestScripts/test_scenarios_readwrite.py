import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import pytest

class Test_Copy:
    RWTest = ReadWriteTest()
    RWTest.setup('copy', '../TestData/tst.txt', 'dteam:/test/tst.txt', '--force') #Use setup method to organise parameters
    scenarios = RWTest.subprocess()
    @pytest.mark.parametrize(
        ("returncode", "stdout", "stderr"), scenarios)

    def test_copy(self, returncode, stdout, stderr):
        assert returncode == 0, f"Upload failed: {stderr}"

    
# class Test_Confirm():
#     RWTest = ReadWriteTest()
#     RWTest.setup('checksum', None, 'dteam:/test/tst.txt', 'query', 'checksum')
#     scenarios = RWTest.subprocess()
#     source = RWTest.xrdadler32('../TestData/tst.txt')
#     @pytest.mark.parametrize(
#         ("returncode", "stdout", "stderr"), scenarios)
    

#     def test_confirm(self, returncode, stdout, stderr, source):
#         dest = stdout.split(" ")[0]
#         assert dest == source, f"Checksum failed: {dest}, {source}"


class Test_Delete:
    delTest = ReadWriteTest()
    delTest.setup('copy', '../TestData/tst.txt', 'dteam:/test/tst.txt', '--force')
    delTest.subprocess()
    
    delTest.setup('delete', None, 'dteam:/test/tst.txt', 'rm')
    scenarios = delTest.subprocess()

    @pytest.mark.parametrize(
            ("returncode", "stdout", "stderr"), scenarios)

    def test_delete(self, returncode, stdout, stderr):
        assert returncode == 0, f"Deletion failed: {stderr}, {stdout}"


class Test_Empty_Transfer:
    RWTest = ReadWriteTest()
    RWTest.setup('copy', '../TestData/0bytes.txt', 'dteam:/test/0bytes.txt', '--force')
    scenarios = RWTest.subprocess()

    @pytest.mark.parametrize(
            ("returncode", "stdout", "stderr"), scenarios)

    def test_empty(self, returncode, stdout, stderr):
        assert returncode == 2, f"Error: File of 0 bytes was transferred: {returncode}, {stderr}, {stdout}"