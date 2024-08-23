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
        encodings = []
        for instruction in basic_block.get_instructions():
            identifier = self._lvn_table.add_entry(instruction)
            if identifier is None:
                encodings.append(instruction)
                continue

            encodings.append(identifier)

        self._lvn_table.show_table("tmp_table.txt")
        # we use another iteration to reconstruct the local block
        # because variable names can be changed if they are reused.
        new_block = []
        for encoding in encodings:
            if isinstance(encoding, ir.Instruction):
                new_block.append(encoding)
                continue

            new_instruction = (self._lvn_table.
                reconstruct_instruction(encoding)
            )
            new_block.append(new_instruction)


        # Take action and change the basic block
        basic_block.transform_into(new_block)

    def retire(self):
        for extension in self._extensions:
            extension.reset()

