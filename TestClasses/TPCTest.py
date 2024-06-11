#!/usr/bin/env python3
import BaseTest
import subprocess


class TPCTest(BaseTest):
    def __init__(self):
        self.srcServer = None
        self.destinServer = None

    def setSrcDest(self, source, destination):
        self.srcServer = source
        self.destinServer = destination


    