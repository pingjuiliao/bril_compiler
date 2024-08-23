#!/usr/bin/env python3

from bril_compiler import ir
from bril_compiler import ir_builder
from bril_compiler import program
from bril_compiler.optimization.redundancy.value_numbering import core
from bril_compiler.optimization.redundancy.value_numbering import base


class InstructionEncoding:
    def __init__(self, identifier=None, instruction=None,
                 var_type=None):
        self.identifier = identifier
        self.instruction = instruction
        self.var_type = var_type
        assert identifier is None or instruction is None


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
            identifier = None
            destination = instruction.get_destination()
            if destination is not None:
                identifier = base.LVNIdentifier(destination)

            new_entry = self._lvn_table.add_entry(instruction)
            if new_entry is not None:
                new_encoding = InstructionEncoding(
                    identifier=new_entry.number,
                    var_type=instruction.get_type()
                )
            elif self._lvn_table.identifier_is_in_table(identifier):
                new_encoding = InstructionEncoding(
                    identifier=identifier,
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
        entry = self._lvn_table.get_entry_by_identifier(encoding.identifier)
        if entry is None:
            print("Encoding error")
            quit()

        if encoding.identifier.is_number():
            return self._build_first_value_instruction(entry, encoding)

        # then, get entry by name
        if entry.value.is_id_instruction():
            return self._build_literal_id_instruction(entry, encoding)
        return self._build_reference_instruction(entry, encoding)

    def _build_first_value_instruction(self, entry, encoding):
        """This function is called when the encoding.identifier is
            a number in the local value numbering
        """
        uses = []
        for use in entry.value.get_operands():
            if isinstance(use, base.LVNPrimitive):
                uses.append(use.get_value())
            elif (isinstance(use, base.LVNIdentifier) and
                  use.is_named_identifier()):
                uses.append(use.get_named_identifier())
            else:
                use_entry = (self._lvn_table.
                             get_entry_by_identifier(use))
                uses.append(use_entry.variable.get_named_identifier())

        return self._ir_builder.build_by_name(
            entry.value.get_operator(),
            uses=uses,
            destination=entry.variable.get_named_identifier(),
            dest_type=entry.value.get_type()
        )

    def _build_literal_id_instruction(self, entry, encoding):
        use = entry.value.get_operands()[0]
        if use.is_named_identifier():
            uses = [use.get_named_identifier()]
        else:
            use_entry = self._lvn_table.get_entry_by_identifier(use)
            uses = [use_entry.variable.get_named_identifier()]
        return self._ir_builder.build_by_name(
            "id",
            uses=uses,
            destination=encoding.identifier.get_named_identifier(),
            dest_type=entry.value.get_type()
        )

    def _build_reference_instruction(self, entry, encoding):
        return self._ir_builder.build_by_name(
            "id",
            uses=[entry.variable.get_named_identifier()],
            destination=encoding.identifier.get_named_identifier(),
            dest_type=entry.value.get_type()
        )
