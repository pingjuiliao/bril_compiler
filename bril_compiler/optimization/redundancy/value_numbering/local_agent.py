#!/usr/bin/env python3

from bril_compiler import ir
from bril_compiler import ir_builder
from bril_compiler import program
from bril_compiler.optimization.redundancy.value_numbering import core

class InstructionEncoding:
    def __init__(self, identity=None, instruction=None,
                 var_type=None):
        self.identity = identity
        self.instruction = instruction
        self.var_type = var_type
        assert identity is None or instruction is None


class ValueNumberingLocalAgent:
    def __init__(self):
        self._encoded_instructions = []
        self._lvn_table = core.ValueNumberingTable()
        self._block_imported = False
        self._ir_builder = ir_builder.IRBuilder()

    def reform(self, basic_block):
        """like a main function of the """
        if self._block_imported:
            print("The block should be called once")
            quit()
        self._block_imported = True
        instructions = basic_block.get_instructions()
        self._build_table_and_encoding(instructions)
        new_instructions = self._get_reformed_instructions()
        basic_block.transform_into(new_instructions)

    def _build_table_and_encoding(self, instructions):
        for instruction in instructions:
            destination = instruction.get_destination()

            new_entry = self._lvn_table.add_entry(instruction)
            if new_entry is not None:
                new_encoding = InstructionEncoding(
                    identity=new_entry.number,
                    var_type=instruction.get_type()
                )
            elif self._lvn_table.variable_is_in_table(destination):
                new_encoding = InstructionEncoding(
                    identity=destination,
                    var_type=instruction.get_type()
                )
            else:
                new_encoding = InstructionEncoding(
                    instruction=instruction
                )

            # add encoding
            self._encoded_instructions.append(new_encoding)

    def _get_reformed_instructions(self):
        """This function uses 2 data structure:
            A list of map that points to
            LocalValueNumbering table
        """
        new_instructions = []
        for encoding in self._encoded_instructions:
            new_instr = self._encoding_to_instruction(encoding)
            new_instructions.append(new_instr)
        return new_instructions

    def _encoding_to_instruction(self, encoding):
        # the type of instruction that does not use value numbering
        if encoding.instruction is not None:
            return encoding.instruction

        # first, get entry by number
        entry = self._lvn_table.get_entry_by_number(encoding.identity)
        if entry is not None:
            if entry.value[0] == "const":
                uses = [entry.value[1]]
            else:
                uses = []
                for use in entry.value[1:]:
                    if isinstance(use, str):
                        uses.append(use)
                    else:
                        use_entry = (self._lvn_table.
                            get_entry_by_number(use))
                        uses.append(use_entry.variable)

            return self._ir_builder.build_by_name(
                entry.value[0],
                uses=uses,
                destination=entry.variable,
                dest_type=encoding.var_type
            )

        # then, get entry by name
        entry = self._lvn_table.get_entry_by_variable(encoding.identity)
        if entry is None:
            print(f"weird encoding: {encoding.identity}")
            quit()
        return self._ir_builder.build_by_name(
            "id",
            uses=[entry.variable],
            destination=encoding.identity,
            dest_type=encoding.var_type
        )




