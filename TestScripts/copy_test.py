#!/usr/bin/env python3
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest
import pytest


copyTest = ReadWriteTest()
copyTest.setup('xrdcp', '../TestData/tst.txt', 'dteam:/test/tst.txt', '--force')
copyTest.subprocess()

