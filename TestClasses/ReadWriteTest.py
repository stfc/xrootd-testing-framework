#!/usr/bin/env python3
from BaseTest import BaseTest
from PerformanceTest import PerformanceTest
import subprocess
import os
from zlib import adler32

class ReadWriteTest(BaseTest, PerformanceTest):
    def __init__(self):
        super().__init__()
        self.stdout = None
        self.stderr = None
    
    def subprocess(self):
        

        #Needs to be given arguments to run test
        #Read-write tests will use xrdcp and gfal-copy
        #If the protocol is root, use xrootd. Otherwise the protocol we use is gfal-copy

        #Go through each item in the self.matrix & create a combination of each protocol, server and root
        for srvr in self.matrix[0]: #Iterate over protocols
            for items in self.matrix[1:]:
                for prot in items:
            
                    tool = self.cmds[prot]
                    endpoint = prot + srvr + ':' + str(self.port)


                    print("Input Args:", self.sourcePath, endpoint, self.destinPath, self.args)
                    fullCmd = self.parse(self.basecmd[tool], self.sourcePath, endpoint, self.destinPath, self.args)

                    print("Full Command:", fullCmd)
                    Testprocess = subprocess.run(fullCmd, capture_output=True, text=True)
        
                    self.stdout = Testprocess.stdout
                    self.stderr = Testprocess.stderr
                    print('Output:', self.stdout, "Error:", self.stderr, Testprocess.returncode)



                    #To be altered?
                    from junit_xml import TestSuite, TestCase

                    test_cases = [TestCase('CopyTest', 'ReadWriteTest', 123.345, self.stdout, self.stderr)]
                    [i.add_error_info(self.stderr) for i in test_cases]
                    [i.add_failure_info("FAIL") for i in test_cases]
                    ts = TestSuite("my test suite", test_cases)
                

                    # pretty printing is on by default but can be disabled using prettyprint=False
                    with open('../Results/output.xml', 'w') as f:
                        TestSuite.to_file(f, [ts], prettyprint=True)

                    #subprocess.run(['ls', os.path.expanduser('../..')])
                    #Call subprocess on each combination, for whatever the specified command was

        return Testprocess.returncode
        
    def parse(self, struc, src, endpoint, dest, args=None):
        finalCmd = [struc[0]]
        strucTmp = iter(struc[1:])

        for idx, item in enumerate(strucTmp):
            if locals()[item] is not None:
                if item == 'endpoint' and struc[idx+2] == 'dest':
                    fullPath = endpoint + '//' + dest
                    finalCmd.append(fullPath)
                    next(strucTmp)
                elif item == 'args':
                    [finalCmd.append(arg) for arg in args]
                else:
                    finalCmd.append(locals()[item])
            else:
                continue

        return finalCmd

    def adler32sum(self, filepath):
        from zlib import adler32
        BLOCKSIZE = 256*1024*1024
        asum = 1
        with open(filepath, 'rb') as f:
            while (data := f.read(BLOCKSIZE)):
                # print('read len:', len(data))
                asum = adler32(data, asum)
        return asum
    
    def xrdadler32(self, filePath):
        cmd = ['/usr/bin/xrdadler32', os.path.expanduser(filePath)]
        Testprocess = subprocess.run(cmd, capture_output=True, text=True)
        
        self.stdout = Testprocess.stdout
        self.stderr = Testprocess.returncode
        checksum = Testprocess.stdout.split(" ")[0]
        print('Output:', self.stdout, "Error:", self.stderr)
        
        return checksum



# CopyTest = ReadWriteTest()

# copyTest = subprocess.run(['xrdcp', '~/tst.txt', 'root://ceph-svc16.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt', '--force'], text=True)

# ls = subprocess.run(['xrdfs', 'root://ceph-svc16.gridpp.rl.ac.uk:1094', 'ls', '/dteam:/test/tst.txt'], text=True)
# checksum = subprocess.run(['xrdfs', 'root://ceph-svc16.gridpp.rl.ac.uk:1094', 'query', 'checksum', '/dteam:/test/tst.txt'], text=True)

# chksm = subprocess.run(['xrdcp', '-d1', '-C', 'adler32:print', '~/tst.txt root://ceph-svc16.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt', '--force'])

# print(copyTest.returncode)
# print(ls.returncode)
# print(checksum.returncode)

# #Write/Copy file across https: (uses gfal-copy):
# #gfal-copy ~/tst.txt https://cern.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt --force
# #internal manager:
# #gfal-copy ~/tst.txt https://echo-internal-manager01.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt --force

# #davs:
# #gfal-copy ~/tst.txt davs://echo-internal-manager01.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt --force

# #chktest = CopyTest.adler32sum('~/tst.txt')



# #Use usr/bin/xrdadler32 to get checksum on both source file + server file:
# srcChksm = subprocess.run(['/usr/bin/xrdadler32', '~/tst.txt'], capture_output=True)
# serverChksm = subprocess.run(['/usr/bin/xrdadler32', 'root://ceph-svc16.gridpp.rl.ac.uk:1094//dteam:/test/tst.txt'])
# #Compare the two and ensure they are the same, if so test passes


# print(srcChksm.stdout.decode())

# #print(chktest)
# #convert chktest to hexidecimal