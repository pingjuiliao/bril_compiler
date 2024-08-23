#!/usr/bin/env python3

from bril_compiler.optimization import compiler_pass
from bril_compiler.optimization.redundancy import tdce
from bril_compiler.optimization.redundancy.value_numbering import core
from bril_compiler.optimization.redundancy.value_numbering import local_agent
from bril_compiler.optimization.redundancy.numbering import agent
from bril_compiler.optimization.redundancy.numbering import extensions

class LocalValueNumberingOldPass(compiler_pass.BrilPass):
    def __init__(self):
        self.num_block_processed = 0

    def optimize(self, module):
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                lvn_agent = local_agent.ValueNumberingLocalAgent()
                lvn_agent.reform(basic_block)
                # self.lvn_reform(basic_block, lvn_table)
                # lvn_table.show_table()

class LocalValueNumberingPass(compiler_pass.BrilPass):
    def __init__(self):
        self.num_block_processed = 0
        self._extensions = [
            extensions.CommutativityExtension(),
            extensions.IdentityPropagationExtension(),
        ]

    def optimize(self, module):
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                lvn_agent = agent.NumberingLocalAgent(self._extensions)
                lvn_agent.reform(basic_block)
                lvn_agent.retire()
                self.num_block_processed += 1


class LocalValueNumberingCompositePass(compiler_pass.BrilCompositePass):
    def __init__(self):
        super().__init__()
        self.add_pass(LocalValueNumberingPass())
        self.add_pass(tdce.TrivilDeadCodeEliminationPass())


class NumberingConstantPropagationPass(compiler_pass.BrilPass):
    def __init__(self):
        self._extensions = [
            extensions.CommutativityExtension(),
            extensions.ConstantPropagationExtension(),
            extensions.IdentityPropagationExtension(),
            extensions.IdentityToConstantInstructionExtension(),
        ]

    def optimize(self, module):
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                lvn_agent = agent.NumberingLocalAgent(self._extensions)
                lvn_agent.reform(basic_block)
                lvn_agent.retire()

class NumberingConstantPropagationCompositePass(compiler_pass.BrilCompositePass):
    def __init__(self):
        super().__init__()
        self.add_pass(NumberingConstantPropagationPass())
        self.add_pass(tdce.TrivilDeadCodeEliminationPass())
