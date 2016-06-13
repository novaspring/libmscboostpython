#! /usr/bin/python3

import os
import sys

## < Code to run examples without the need to specify the path to Msc.Boost
try:
    from Msc.Boost import *
except:
    sys.path.append("{0}/../".format(os.path.dirname(__file__)))
    from Msc.Boost import *
## >

class MyApplication(Application):
    def _Main(self):
        print ('Hello')

envPath = EnvironmentVariable("PATH", "Path to application")
envDummy = EnvironmentVariable("DUMMY", "Dummy application")

x = MyApplication()        
x.Run()
