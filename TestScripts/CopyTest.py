#!/usr/bin/env python3
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest

copyTest = ReadWriteTest()
copyTest.setup('xrdcp', '~/tst.txt', 'dteam:/test/tst.txt', '--force')

copyTest.subprocess()

