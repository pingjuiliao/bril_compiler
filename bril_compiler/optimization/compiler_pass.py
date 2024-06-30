#!/usr/bin/env python3

class CompilerPass:
    """Compiler Pass follows Composite design pattern, where """

    def __init__(self):
        self._passes = []

    def add_pass(self, bril_pass):
        raise NotImplementedError

    def optimize(self, module):
        raise NotImplementedError

class PassManager(CompilerPass):
    """The composite design pattern of CompilerPass"""

    def add_passes(self, bril_pass):
        self._passes.append(bril_pass)

    def optimize(self, module):
        for bril_pass in self._passes:
            bril_pass.optimize(module)
