#! /usr/bin/python3

import os
import sys

## < Code to run examples without the need to specify the path to MscBoost
try:
    from MscBoost import *
except:
    sys.path.append("{0}/../".format(os.path.dirname(__file__)))
    from MscBoost import *
## >

class MyApplication(Application):
    def __init__(self):
        super(self.__class__,self).__init__("MyApplication", "Example application.")
        self.arg_parser.add_argument("--dummy", help="Dummy.")

        sub_parsers = self.arg_parser.add_subparsers(title="commands", help="Commands.")
        cmd_parser = sub_parsers.add_parser("clone", help="Clones.")
        cmd_parser = sub_parsers.add_parser("update", help="Updates.")
        cmd_parser.add_argument("--from",
                                help="From.",
                                action="store_true")

    def _main(self):
        print ("Hello World")

env_path = EnvironmentVariable("PATH", "Path to application.")
env_dummy = EnvironmentVariable("DUMMY", "Dummy application.")

x = MyApplication()        
x.run()
