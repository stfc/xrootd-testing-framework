#!/usr/bin/env python3
import timeit
import time
import memory_profiler #import memory_usage
from datetime import datetime

class PerformanceTest():
    def __init__(self):
        self.startTime = None
        self.endTime = None
    
    def setStartTime(self):
        self.startTime = datetime.now().time()
    def setEndTime(self):
        self.endTime = datetime.now().time()

    def timeTaken(self):
        #tdelta = self.endTime.strptime()
        print(self.startTime, self.endTime)
        #print(self.endTime - self.startTime)

# obj = PerformanceTest()
# obj.setStartTime()
# time.sleep(3)
# obj.setEndTime()
# obj.timeTaken()

