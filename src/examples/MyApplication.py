#! /usr/bin/python3

import os
import sys

## < Code to run examples without the need to specify the path to Msc.Boost
try:
    import Msc.Boost
except:
    sys.path.append("{0}/../".format(os.path.dirname(__file__)))
    import Msc.Boost
## >

class MyApplication(Msc.Boost.Application):
    def _Main(self):
        print ('Hello')

x = MyApplication()        
x.Run()
