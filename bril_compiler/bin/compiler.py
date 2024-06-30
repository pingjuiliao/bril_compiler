#!/usr/bin/env python3

import argparse
import json
import os
import sys

from bril_compiler import parser
from bril_compiler import program
from bril_compiler.optimization import compiler_pass

def opt(module, passes):
    """the optimizer routine"""
    pass_manager = compiler_pass.PassManager()
    pass_manager.optimize(module)
    data = module.dump_json()
    json.dump(data, sys.stdout)

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-c", "--source", type=str, required=True)
    argparser.add_argument("-p", "--passes", nargs="+")
    args = argparser.parse_args()

    # check if the source script exists
    if not os.path.exists(args.source):
        print("[Error] cannot find source {args.source}")
        quit()

    # parse the file and represent it as a Module
    bril_parser = parser.JSonToBrilParser()
    module = bril_parser.parse(args.source)
    opt(module, args.passes)


if __name__ == "__main__":
    main()
