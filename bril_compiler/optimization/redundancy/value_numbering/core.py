#!/usr/bin/env python

from bril_compiler import ir
from bril_compiler import ir_builder
from bril_compiler.optimization.redundancy.value_numbering import base

class ValueNumberingTableEntry:
    def __init__(self, number, value, variable):
        self.number = number
        self.value = value
        # the conanical home of the variable
        self.variable = variable
        if (self.number is None or self.value is None or
            self.variable is None):
            print(self.value, self.variable)
            quit()

class ValueNumberingTable:
    def __init__(self):
        """The data structure for the table defined as
        the three mapping to the entries
            - _entrires: mapping from number to entries
            - _value_to_entry: mapping from values to entries
            - _variable_to_entry: variable (canonical home to entry)
        """
        self._entries = []
        self._value_to_entry = {}
        self._variable_to_entry = {}
        self._identifiers = {}

    def add_entry(self, instruction):
        """Value Numbering table only allows addition to the table
           Typically, there are four cases:
            - new value, new variable: generate new entry
            - new value, old variable: rename old variable, and generate
                                       entry
            - old value, new variable: map new variable to the old entry
            - old value, old variable: slient store

        """
        # get variable, the destintation identifier for building entry
        variable = self._get_variable(instruction)

        # We will based on the value the construction table entries
        value = self._encode_to_value(instruction)
        if value is None:
            return None

        # rename the same variable name if it's previously used
        conflict_entry = self.get_entry_by_identifier(variable)
        if conflict_entry is not None and conflict_entry.value != value:
            conflict_entry.variable = self.rename_variable(
                conflict_entry.number.get_number()
            )
            self._identifiers[variable] = None
            self._identifiers[conflict_entry.variable] = conflict_entry

        # copy propagation
        value = self.get_referenced_value(value)

        # the value is previously seen, do not update the table
        if value in self._value_to_entry:
            self._identifiers[variable] = self._value_to_entry[value]
            return None

        number = base.LVNIdentifier(len(self._entries))
        entry = ValueNumberingTableEntry(
            number, value, variable
        )
        self._entries.append(entry)
        self._value_to_entry[entry.value] = entry
        self._variable_to_entry[variable] = entry
        self._identifiers[number] = entry
        self._identifiers[variable] = entry
        return entry

    def get_entry_by_number(self, number):
        if number >= len(self._entries):
            return None
        return self._entries[number]

    def get_entry_by_value(self, value):
        if value not in self._value_to_entry:
            return None
        return self._value_to_entry[value]

    def get_entry_by_variable(self, variable):
        if not isinstance(variable, base.LVNIdentifier):
            return None
        if variable not in self._variable_to_entry:
            return None
        return self._variable_to_entry[variable]

    def get_entry_by_identifier(self, identifier):
        if identifier is None:
            return None
        if identifier not in self._identifiers:
            return None
        return self._identifiers[identifier]

    def rename_variable(self, number):
        return base.LVNIdentifier(f"lvn.{number}")

    def _encode_to_value(self, instruction):
        operator = instruction.get_operator_string()
        if operator in ["jmp", "br"]:
            return None
        op_type = instruction.get_type()
        operands = instruction.get_arguments()
        encoded_operands = []
        for operand in operands:
            if operator == "const":
                primitive = base.LVNPrimitive(operand)
                encoded_operands.append(primitive)
                continue

            # reference entry is None == variable defined outside the
            # basic block (local context)
            identifier = base.LVNIdentifier(operand)
            reference_entry = self.get_entry_by_identifier(identifier)
            if reference_entry is not None:
                identifier = reference_entry.number
            encoded_operands.append(identifier)

        return base.LVNValue(operator, encoded_operands, op_type)

    def identifier_is_in_table(self, identifier):
        if identifier is None:
            return False
        return self.get_entry_by_identifier(identifier) != None

    def show_table(self):
        print(f"|{'#'.rjust(5)}|{'Value'.rjust(25)}|{'Id'.rjust(15)}|")
        print("-" * 50)
        for i, entry in enumerate(self._entries):
            num = str(i).rjust(5)
            val = str(entry.value).rjust(25)
            var = str(entry.variable).rjust(15)
            print(f"|{num}|{val}|{var}|")
        print("-" * 50)

    def _get_variable(self, instruction):
        """ Basically, we don't need instruction that has no destination.
            with one exception: PrintInstruction
        """
        variable = instruction.get_destination()
        if variable is None:
            operator = instruction.get_operator_string()
            if operator in ["br", "jmp"]: # blacklist
                return None
            elif operator in ["print"]: # whitelist
                return self.rename_variable(len(self._entries))
            else:
                print(f"Unhandled instruction {instruction}")
                quit()

        return base.LVNIdentifier(variable)

    def get_referenced_value(self, value):
        if not value.is_id_instruction():
            return value

        reference_id = value.get_operands()[0]

        # Since it's a id instruciton, we don't need to check if this is
        # a primitive value
        # assert isinstance(reference_id)
        if not reference_id.is_number():
            return value

        reference_entry = self.get_entry_by_identifier(reference_id)
        if not reference_entry.value.is_id_instruction():
            return value
        return reference_entry.value
