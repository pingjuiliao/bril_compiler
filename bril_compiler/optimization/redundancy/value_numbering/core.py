#!/usr/bin/env python

from bril_compiler import ir
from bril_compiler import ir_builder

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
        self._entries = []
        self._value_to_entry = {}
        self._variable_to_entry = {}
        self._irbuilder = ir_builder.IRBuilder()
        self._used_for_reform = set()

    def add_entry(self, instruction):
        """Value Numbering table only allows addition to the table
           Typically, there are four cases:
            - new value, new variable: generate new entry
            - new value, old variable: rename old variable, and generate
                                       entry
            - old value, new variable: map new variable to the old entry
            - old value, old variable: slient store

        """
        # basically, we don't need instruction that has no destination.
        # except PrintInstruction
        variable = instruction.get_destination()
        if variable is None:
            operator = instruction.get_operator_string()
            if operator in ["br", "jmp"]: # blacklist
                return None
            elif operator in ["print"]: # whitelist
                variable = self.rename_variable(len(self._entries))
            else:
                print(f"Unhandled instruction {instruction}")
                quit()

        # We will based on the value the construction table entries
        value = self._encode_to_value(instruction)
        if value is None:
            return None


        # reused variable name
        conflict_entry = self.get_entry_by_variable(variable)
        if conflict_entry is not None and conflict_entry.value != value:
            conflict_entry.variable = self.rename_variable(
                conflict_entry.number
            )
            self._variable_to_entry[variable] = None
            self._variable_to_entry[conflict_entry.variable] = conflict_entry

        # same value
        if value in self._value_to_entry:
            self._variable_to_entry[variable] = (
                self._value_to_entry[value]
            )
            return None

        entry = ValueNumberingTableEntry(
            len(self._entries), value, variable
        )
        self._entries.append(entry)
        self._value_to_entry[entry.value] = entry
        self._variable_to_entry[variable] = entry
        return entry

    def get_entry_by_number(self, number):
        if not isinstance(number, int):
            return None
        if number >= len(self._entries):
            return None
        return self._entries[number]

    def get_entry_by_value(self, value):
        if value not in self._value_to_entry:
            return None
        return self._value_to_entry[value]

    def get_entry_by_variable(self, variable):
        if not isinstance(variable, str):
            return None
        if variable not in self._variable_to_entry:
            return None
        return self._variable_to_entry[variable]

    def rename_variable(self, number):
        return f"lvn.{number}"

    def _encode_to_value(self, instruction):
        operator = instruction.get_operator_string()
        operands = instruction.get_arguments()
        encoded_operands = []
        for operand in operands:
            if operator == "const":
                encoded_operands.append(operand)
                continue

            # reference entry is None == variable defined outside the
            # basic block (local context)
            reference_entry = self.get_entry_by_variable(operand)
            if reference_entry is None:
                encoded_operands.append(operand)
            else:
                encoded_operands.append(reference_entry.number)

        if len(encoded_operands) == 1:
            return (operator, encoded_operands[0])
        elif len(encoded_operands) == 2:
            return (operator, encoded_operands[0], encoded_operands[1])

        print(f"Cannot decode this new type of instruction {instruction}")
        quit()

    def variable_is_in_table(self, variable):
        return self.get_entry_by_variable(variable) != None

    def reform(self, instruction):
        """Query the table and reform instruction.
            Note that we must re-encode the value again to match,
            since the variable name could have been changed due to
            reassignment of the same variable
        """
        if self._should_ignore(instruction):
            return None
        value = self._encode_to_value(instruction)
        if value is None:
            return None

        entry = self.get_entry_by_value(value)
        if entry is None:
            return None

        # if it's a reuse of an value,
        if value in self._used_for_reform:
            return self._irbuilder.build_by_name(
                "id",
                uses=[entry.variable],
                destination=instruction.get_destination(),
                dest_type=instruction.get_type()
            )
        self._used_for_reform.add(value)

        # Now, we are safe to build new instruction
        operator = entry.value[0]
        uses = []
        # const instruction directly uses its value
        if operator == "const":
            uses.append(entry.value[1])
        else:
            for i in range(1, len(entry.value)):
                use_number = entry.value[i]
                # if it's a string, definition outside the local context
                if isinstance(use_number, str):
                    uses.append(entry.value[i])
                    continue
                use_entry = self.get_entry_by_number(use_number)
                if use_entry is None:
                    print("Error in constructing the table")
                    quit()
                uses.append(use_entry.variable)

        #print(operator, uses)
        return self._irbuilder.build_by_name(
            operator,
            uses=uses,
            destination=entry.variable,
            dest_type=instruction.get_type()
        )

    def _should_ignore(self, instruction):
        return instruction.get_operator_string() in ["jmp", "br"]

    def variable_in_table(self, variable):
        return variable in self._variable_to_entry

    def reform_instruction(self, variable_name, variable_type):
        """Query the table and """

        entry = self.get_entry_by_variable(variable_name)
        if entry.variable != variable_name:
            return self._irbuilder.build_by_name(
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

        return self._irbuilder.build_by_name(
            operator,
            uses=uses,
            destination=variable_name,
            dest_type=variable_type
        )

    def show_table(self):
        print("|  #  |   Value    | Variable")
        for i, entry in enumerate(self._entries):
            print(f"| {i} | {entry.value}    | {entry.variable}")
