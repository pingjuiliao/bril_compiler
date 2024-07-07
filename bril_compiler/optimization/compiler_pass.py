#!/usr/bin/env python3

class BrilPass:
    """Compiler Pass follows Composite design pattern, where """

    def __init__(self):
        raise NotImplementedError

    def add_pass(self, bril_pass):
        raise NotImplementedError

    def optimize(self, module):
        raise NotImplementedError

class BrilCompositePass(BrilPass):
    """The composite design pattern of CompilerPass"""
    def __init__(self):
        self._passes = []

    def add_pass(self, bril_pass):
        self._passes.append(bril_pass)

    def optimize(self, module):
        for bril_pass in self._passes:
            bril_pass.optimize(module)


class BrilPassManager(BrilCompositePass):
    """The universal pass manager, the root of compiler pass tree"""
    def __init__(self):
        super().__init__()
        self._is_manager = True

    def __new__(cls):
        """Singleton"""
        if not hasattr(cls, 'instance'):
            cls.instance = super(BrilPassManager, cls).__new__(cls)
        return cls.instance
