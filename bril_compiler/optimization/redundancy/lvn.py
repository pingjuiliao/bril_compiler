#!/usr/bin/env python3

from bril_compiler.optimization import compiler_pass
from bril_compiler.optimization.redundancy import tdce
from bril_compiler.optimization.redundancy.value_numbering import core
from bril_compiler.optimization.redundancy.value_numbering import local_agent

class LocalValueNumberingPass(compiler_pass.BrilPass):
    def __init__(self):
        self.num_block_processed = 0

    def optimize(self, module):
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                agent = local_agent.ValueNumberingLocalAgent()
                agent.reform(basic_block)
                # self.lvn_reform(basic_block, lvn_table)
                # lvn_table.show_table()

class LocalValueNumberingCompositePass(compiler_pass.BrilCompositePass):
    def __init__(self):
        super().__init__()
        self.add_pass(LocalValueNumberingPass())
        self.add_pass(tdce.TrivilDeadCodeEliminationPass())
