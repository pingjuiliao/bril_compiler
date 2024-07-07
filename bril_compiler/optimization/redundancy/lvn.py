#!/usr/bin/env python3

from bril_compiler.optimization import compiler_pass
from bril_compiler.optimization.redundancy import tdce
from bril_compiler.optimization.redundancy.value_numbering import core


class LocalValueNumberingPass(compiler_pass.BrilPass):
    def __init__(self):
        self._lvn_table = core.ValueNumberingTable()

    def optimize(self, module):
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                self.lvn_reform(basic_block)

    def lvn_reform(self, basic_block):
        """The algorithm that performs numbering
            so that dead code eliemiation will eliminate the redundant instrucitons"""
        instructions = basic_block.get_instructions()

        # construct the lvn table
        for instruction in instructions:
            # ignore instructions that has no destination
            destination = instruction.get_destination()
            if destination is None:
                continue
            self._lvn_table.add_entry(instruction)

        # reform instructions
        new_instructions = []
        for instruction in instructions:
            destination = instruction.get_destination()
            if destination is None:
                new_instructions.append(instruction)
                continue

            # reform
            dest_type = instruction.get_type()
            new_instruction = self._lvn_table.reform_instruction(
                destination, dest_type
            )
            new_instructions.append(new_instruction)

        # transform
        basic_block.transform_into(new_instructions)


class LocalValueNumberingCompositePass(compiler_pass.BrilCompositePass):
    def __init__(self):
        super().__init__()
        self.add_pass(LocalValueNumberingPass())
        self.add_pass(tdce.TrivilDeadCodeEliminationPass())
