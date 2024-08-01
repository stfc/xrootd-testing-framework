import os
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
from TPCTest import TPCTest
import pytest

class Test_Copy_Performance:
    RWTest = ReadWriteTest()
    FILENAME = 'tst2G.txt'
    scenarios = RWTest.genTimedScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force', reps=1)
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_2GB(self, scenario):
        returncode, stdout, stderr, avgTime, fileSize = scenario
        throughput = fileSize/avgTime
        expected = 2
        assert returncode == 0, f"Upload failed: {stderr}, {stdout}"
        assert expected-5 <= throughput <= expected+5


    FILENAME = 'tst40M.txt'
    scenarios = RWTest.genTimedScenarios('copy', f'../TestData/{FILENAME}', FILENAME, '--force', reps=5)
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_40MB(self, scenario):
        returncode, stdout, stderr, avgTime, fileSize = scenario
        throughput = fileSize/avgTime
        expected = 2
        assert returncode == 0; f"Upload failed: {stderr}, {stdout}"
        assert expected-5 <= throughput <= expected+5

class Test_TPCopy_Performance:
    TPCTest = TPCTest()
    FILENAME = 'tst2G.txt'
    scenarios = TPCTest.genTimedScenarios('copy', FILENAME, FILENAME, '--force', reps=1)
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_2GB(self, scenario):
        returncodeAB, stdoutAB, stderrAB, avgTimeAB, fileSizeAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA, avgTimeBA, fileSizeBA = scenario[1]
        throughputAB = fileSizeAB/avgTimeAB
        throughputBA = fileSizeBA/avgTimeBA
        expected = 2

        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"
        
        assert expected-5 <= throughputAB <= expected+5
        assert expected-5 <= throughputBA <= expected+5

    FILENAME = 'tst40M.txt'
    scenarios = TPCTest.genTimedScenarios('copy', FILENAME, FILENAME, '--force', reps=5)
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_40MB(self, scenario):
        returncodeAB, stdoutAB, stderrAB, avgTimeAB, fileSizeAB = scenario[0]
        returncodeBA, stdoutBA, stderrBA, avgTimeBA, fileSizeBA = scenario[1]
        throughputAB = fileSizeAB/avgTimeAB
        throughputBA = fileSizeBA/avgTimeBA
        expected = 2

        assert returncodeAB == 0, f"Upload failed: {stderrAB}, {stdoutAB}"
        assert returncodeBA == 0, f"Upload failed: {stderrBA}, {stdoutBA}"
        
        assert expected-5 <= throughputAB <= expected+5
        assert expected-5 <= throughputBA <= expected+5
