#!/usr/bin/env python3
import sys   
sys.path.insert(0, "../TestClasses")
from BaseTest import BaseTest
from ReadWriteTest import ReadWriteTest

checksumTest = ReadWriteTest()
#checksumTest.setup('xrdfs', None, 'dteam:/test/tst.txt', 'query', 'checksum')
dest = checksumTest.xrdadler32('root://ceph-svc16.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt')
source = checksumTest.xrdadler32('~/test.tmp')

assert dest == source