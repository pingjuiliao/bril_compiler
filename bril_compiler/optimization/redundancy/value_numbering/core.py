#!/usr/bin/env python

from bril_compiler import ir
from bril_compiler import ir_builder

class ValueNumberingTableEntry:
    def __init__(self, number, value, variable):
        self.number = number
        self.value = value
        # the conanical home of the variable
        self.variable = variable

class ValueNumberingTable:
    def __init__(self):
        self._entries = []
        self._value_to_entry = {}
        self._variable_to_entry = {}
        self.irbuilder = ir_builder.IRBuilder()

    def add_entry(self, instruction):
        variable = instruction.get_destination()
        if variable is None:
            return
        encoded_value = self._encode_to_value(instruction)
        if encoded_value in self._value_to_entry:
            self._variable_to_entry[variable] = (
                self._value_to_entry[encoded_value]
            )
        else:
            entry = ValueNumberingTableEntry(
                len(self._entries), encoded_value, variable
            )
            self._entries.append(entry)
            self._value_to_entry[entry.value] = entry
            self._variable_to_entry[variable] = entry

    def get_entry_by_number(self, number):
        if number >= len(self._entries):
            print(f"number {number} not in table")
            quit()
        return self._entries[number]

    def get_entry_by_value(self, value):
        if value not in _value_to_entry:
            print(f"value encoded as {value} not in table")
            quit()
        return self._value_to_entry[value]

    def get_entry_by_variable(self, variable):
        if variable not in self._variable_to_entry:
            print(f"variable named {variable} not in table")
            quit()
        return self._variable_to_entry[variable]

    def _encode_to_value(self, instruction):
        operator = instruction.get_operator_string()
        operands = instruction.get_arguments()
        encoded_operands = []
        for operand in operands:
            if operator == "const":
                encoded_operands.append(operand)
                continue
            reference_entry = self.get_entry_by_variable(operand)
            encoded_operands.append(reference_entry.number)

        if len(encoded_operands) == 1:
            return (operator, encoded_operands[0])
        elif len(encoded_operands) == 2:
            return (operator, encoded_operands[0], encoded_operands[1])

        print(f"Cannot decode this new type of instruction {instruction}")
        quit()

    def reform_instruction(self, variable_name, variable_type):
        """Query the table and """
        entry = self.get_entry_by_variable(variable_name)
        if entry.variable != variable_name:
            return self.irbuilder.build_by_name(
                "id",
                uses=[entry.variable],
                destination=variable_name,
            )

        operator = entry.value[0]
        if operator == "const":
            uses = [entry.value[1]]
        else:
            uses = []
            for i in range(1, len(entry.value)):
                use_number = entry.value[i]
                use_entry = self._entries[use_number]
                uses.append(use_entry.variable)

        return self.irbuilder.build_by_name(
            operator,
            uses=uses,
            destination=variable_name,
            dest_type=variable_type
        )
