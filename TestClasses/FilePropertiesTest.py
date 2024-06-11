#!/usr/bin/env python3
from BaseTest import BaseTest
from MetadataTest import MetadataTest

fileProperties = MetadataTest()
fileProperties.setup('~/tst.txt', 'dteam:/test/')

#Call function that uses subprocess to run xrdfs stat on server side file
#Check against the file's own properties
