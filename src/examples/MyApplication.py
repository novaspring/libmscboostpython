#! /usr/bin/python3

import os
import sys

# Use MscBoost from this libMscBoostPython checkout
sys.path.insert(0, "{0}/../".format(os.path.dirname(__file__)))
from MscBoost.Application import Application
from MscBoost.EnvironmentVariable import EnvironmentVariable

class MyApplication(Application):
    def __init__(self):
        super().__init__("MyApplication", "Example application.")
        self.arg_parser.add_argument("--dummy", help="Dummy.")

        sub_parsers = self.arg_parser.add_subparsers(title="commands", help="Commands.")
        clone_cmd_parser = sub_parsers.add_parser("clone", help="Clones.")
        update_cmd_parser = sub_parsers.add_parser("update", help="Updates.")
        update_cmd_parser.add_argument("--from", help="From.", action="store_true")

    def _main(self):
        print ("Hello World")

env_path = EnvironmentVariable("PATH", "Path to application.")
env_dummy = EnvironmentVariable("DUMMY", "Dummy application.")

app = MyApplication()
app.run()
