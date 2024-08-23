#!/usr/bin/env python3

from bril_compiler import ir
from bril_compiler import ir_builder
from bril_compiler.optimization.redundancy.numbering import base
from bril_compiler.optimization.redundancy.numbering import extensions

class NumberingTableEntry:
    def __init__(self, number, value, variable):
        self.number = number
        self.value = value
        self.variable = variable


class NumberingTable:
    IGNORE_OPERATIONS = ["jmp", "br"]
    def __init__(self, numbering_extensions):
        self._entries = []
        self._value_to_entry = {}
        self._identifiers = {}
        self._extensions = numbering_extensions
        self._ir_builder = ir_builder.IRBuilder()

    def add_entry(self, instruction):
        operator = instruction.get_operator_string()
        if operator in self.IGNORE_OPERATIONS:
            return None

        # Resolve the variable/identifier name
        destination = instruction.get_destination()
        if destination is None:
            destination = self.rename_identifier(len(self._entries))
        identifier = base.NumberingIdentifier(destination)

        if identifier in self._identifiers:
            conflicting_entry = self._identifiers[identifier]
            conflicting_identifier = conflicting_entry.variable
            renamed_destination = self.rename_identifier(
                conflicting_entry.number.get_string()
            )
            conflicting_identifier.rename_as(renamed_destination)
            # conflicting_entry.variable = base.NumberingIdentifier(
            #     renamed_destination)
            self._identifiers[conflicting_identifier] = conflicting_entry
        assert isinstance(identifier, base.NumberingIdentifier)

        # Get encoded value, if used before, simply add the new identifier
        #  to the target
        value = self._encode_to_value(instruction)

        for extension in self._extensions:
            if (extension.type != extensions.
                NumberingExtensionType.PRE_BUILD_TABLE_EXTENSION):
                continue
            value = extension.update(value, self)

        duplicated_entry = self.get_entry_by_value(value)
        if duplicated_entry is not None:
            self._identifiers[identifier] = duplicated_entry
            return identifier

        # building new entry
        number = base.NumberingIdentifier(len(self._entries))
        new_entry = NumberingTableEntry(
            number, value, identifier
        )
        self._entries.append(new_entry)
        self._value_to_entry[value] = new_entry
        self._identifiers[number] = new_entry
        self._identifiers[identifier] = new_entry
        return new_entry.number

    def reconstruct_instruction(self, identifier):
        entry = self.get_entry_by_identifier(identifier)
        if entry is None:
            print(f"{identifier} not in table")
            quit()

        numbering_value = entry.value
        for extension in self._extensions:
            if (extension.type != extensions.
                NumberingExtensionType.RECONSTRUCTION_EXTENSION):
                continue
            numbering_value = extension.update(numbering_value, self)

        uses = []
        for use in numbering_value.get_operands():
            if isinstance(use, base.NumberingPrimitive):
                use_value = use.get_value()
            elif use.is_number():
                used_entry = self.get_entry_by_identifier(use)
                use_value = used_entry.variable.get_string()
            elif use.is_named_identifier():
                use_value = use.get_string()
            else:
                raise ValueError
            uses.append(use_value)

        if identifier.is_number():
            return self._ir_builder.build_by_name(
                numbering_value.get_operator(),
                uses=uses,
                destination=entry.variable.get_string(),
                dest_type=numbering_value.get_type()
            )

        if numbering_value.get_operator() in ["id", "const"]:
            return self._ir_builder.build_by_name(
                numbering_value.get_operator(),
                uses=uses,
                destination=identifier.get_string(),
                dest_type=numbering_value.get_type()
            )

        referred_entry = self.get_entry_by_identifier(identifier)
        return self._ir_builder.build_by_name(
            "id",
            uses=[referred_entry.variable.get_string()],
            destination=identifier.get_string(),
            dest_type=numbering_value.get_type()
        )

    def get_entry_by_value(self, numbering_value):
        if numbering_value not in self._value_to_entry:
            return None
        return self._value_to_entry[numbering_value]

    def get_entry_by_identifier(self, key):
        if key not in self._identifiers:
            return None
        return self._identifiers[key]

    def _encode_to_value(self, instruction, extensions=[]):
        """We need three things:
            1. operator string
            2. a list of operands, which should refer to the table
            3. the operation type
        """
        operator = instruction.get_operator_string()
        op_type = instruction.get_type()
        encoded_operands = []
        for operand in instruction.get_arguments():
            # const operation works on primitive values
            if operator == "const":
                primitive = base.NumberingPrimitive(operand)
                encoded_operands.append(primitive)
                continue

            # reference entry is None == variable defined outside the
            # basic block (local context)
            operand_id = base.NumberingIdentifier(operand)
            reference_entry = self.get_entry_by_identifier(operand_id)
            if reference_entry is not None:
                operand_id = reference_entry.number
            encoded_operands.append(operand_id)

        return base.NumberingValue(operator, encoded_operands, op_type)

    def show_table(self, out_file=None):
        s = f"|{'#'.rjust(5)}|{'Value'.rjust(25)}|{'Id'.rjust(15)}|\n"
        s += "-" * 50 + "\n"
        for i, entry in enumerate(self._entries):
            num = str(i).rjust(5)
            val = str(entry.value).rjust(25)
            var = str(entry.variable).rjust(15)
            s += f"|{num}|{val}|{var}\n"
        s += "-" * 50 + "\n"
        if out_file is None:
            print(s)
            return

        with open(out_file, "wb") as f:
            f.write(s.encode('ascii'))
            f.close()


    def rename_identifier(self, entry_id):
        return f"lvn.{entry_id}"
