import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from TPCTest import TPCTest
import pytest

class Test_TPCopy:
    FILENAME = 'tst.txt'
    TPCTest = TPCTest('../TestClasses/ConfigTPC.yaml')
    scenarios = TPCTest.genScenarios('copy', FILENAME, FILENAME, '--force', TestAll=False)
    checksums = TPCTest.genScenarios('checksum', FILENAME, FILENAME, TestAll=False)

    @pytest.mark.parametrize(("scenario, checksums"), zip(scenarios, checksums))
    def test_copy(self, scenario, checksums):
        returncodeAB, stdoutAB, stderrAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA = scenario[1]
        srcsum, destsum = checksums
        
        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"
        assert destsum == srcsum, f"Stat failed: Mismatching checksums. Source: {srcsum}, Dest: {destsum}"

    
    scenarios = TPCTest.genScenarios('load', FILENAME, FILENAME)

    @pytest.mark.parametrize("scenario", scenarios)
    def test_load_redirection(self, scenario): #test needs adjusting - Only want siteB and A->B to be self.redirect
        returncodeAB, stdoutAB, stderrAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA = scenario[1]
        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"


class Test_Empty_Transfer:
    FILENAME = '0bytes.txt'
    TPCTest = TPCTest('../TestClasses/ConfigTPC.yaml')
    scenarios = TPCTest.genScenarios('copy', FILENAME, FILENAME, '--force')
    checksums = TPCTest.genScenarios('checksum', FILENAME, FILENAME)
    
    @pytest.mark.parametrize(("scenario, checksums"), zip(scenarios, checksums))
    def test_empty(self, scenario, checksums):
        returncodeAB, stdoutAB, stderrAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA = scenario[1]
        srcsum, destsum = checksums
        assert destsum == None, f"Checksum of 0 bytes file should be None. {destsum}"


class Test_TPDelete:
    FILENAME = 'tst.txt'
    TPCTest = TPCTest('../TestClasses/ConfigTPC.yaml')
    scenarios = TPCTest.genScenarios('copy', FILENAME, FILENAME, '--force')
    checksums = TPCTest.genScenarios('checksum', FILENAME, FILENAME)

    @pytest.mark.parametrize(("scenario, checksums"), zip(scenarios, checksums))
    def test_deletion(self, scenario, checksums):
        returncodeAB, stdoutAB, stderrAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA = scenario[1]
        srcsum, destsum = checksums
        assert returncodeAB == 0, f"Deletion failed: {stderrAB}, {stdoutAB}"
        assert destsum == None, f"Deletion failed: Checksum still present {destsum}"
        assert returncodeBA == 0, f"Deletion failed: {stderrBA}, {stdoutBA}"
        assert srcsum == None, f"Deletion failed: Checksum still present {srcsum}"
