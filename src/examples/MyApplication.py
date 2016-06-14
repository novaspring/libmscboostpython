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
    def __init__(self):
        super(self.__class__,self).__init__("MyApplication", "Example application.")
        self.ArgParser.add_argument("--dummy", help="Dummy.")

    def _Main(self):
        print ("Hello World")

envPath = EnvironmentVariable("PATH", "Path to application.")
envDummy = EnvironmentVariable("DUMMY", "Dummy application.")

x = MyApplication()        
x.Run()
