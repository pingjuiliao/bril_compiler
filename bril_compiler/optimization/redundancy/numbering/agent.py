#!/usr/bin/env python3

from bril_compiler import ir
from bril_compiler import ir_builder
from bril_compiler import program
from bril_compiler.optimization.redundancy.numbering import base
from bril_compiler.optimization.redundancy.numbering import table


class NumberingLocalAgent:
    def __init__(self, extensions):

        self._lvn_table = table.NumberingTable(extensions)
        self._extensions = extensions
        self._ir_builder = ir_builder.IRBuilder()

    def reform(self, basic_block):
        """main function"""
        new_block = []
        for instruction in basic_block.get_instructions():
            identifier = self._lvn_table.add_entry(instruction)
            if identifier is None:
                new_block.append(instruction)
                continue

            new_instruction = (self._lvn_table.
                reconstruct_instruction(identifier)
            )
            new_block.append(new_instruction)

        self._lvn_table.show_table("./tmp_table.txt")
        # Take action and change the basic block
        basic_block.transform_into(new_block)

    def retire(self):
        for extension in self._extensions:
            extension.reset()

