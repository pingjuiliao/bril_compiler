#!/usr/bin/env python3

import argparse
import json
import os
import sys

from bril_compiler import parser
from bril_compiler import program
from bril_compiler.optimization import compiler_pass

pass_map = {
    "tdce": "bril_compiler.optimization.redundancy.tdce.TrivilDeadCodeEliminationPass",
    "lvn": "bril_compiler.optimization.redundancy.lvn.LocalValueNumberingCompositePass",
    "lvn-only": "bril_compiler.optimization.redundancy.lvn.LocalValueNumberingPass"
}

def dynamic_import(pass_name):
    pass_module = pass_map[pass_name]
    module_name, class_name = pass_module.rsplit(".", 1)
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)

def opt(module, bril_passes_name):
    """the optimizer routine"""
    pass_manager = compiler_pass.BrilPassManager()
    for pass_name in bril_passes_name:
        if pass_name not in pass_map:
            print(f"[ERROR] Do not have pass named {bril_pass}")
            quit()
        BrilPassClass = dynamic_import(pass_name)
        bril_pass = BrilPassClass()
        pass_manager.add_pass(bril_pass)

    pass_manager.optimize(module)
    data = module.dump_json()
    json.dump(data, sys.stdout)

def list_all_passes():
    print("Pass lists:")
    for pass_name in pass_map.keys():
        print(f"\t{pass_name}")
    print("===end of list====")
    quit()

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-l", "--list", action="store_true")
    argparser.add_argument("-c", "--source", type=str)
    argparser.add_argument("-p", "--passes", nargs="+")
    args = argparser.parse_args()

    # -l has the first priority: just print out list of passes
    if args.list:
        list_all_passes()

    # check if the source script exists
    if not os.path.exists(args.source):
        print("[Error] cannot find source {args.source}")
        quit()

    # parse the file and represent it as a Module
    bril_parser = parser.JSonToBrilParser()
    module = bril_parser.parse(args.source)
    passes = [] if args.passes is None else args.passes
    opt(module, passes)


if __name__ == "__main__":
    main()
