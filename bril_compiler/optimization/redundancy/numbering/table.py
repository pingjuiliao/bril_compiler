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

        # In the reconstruction step, we need to change the name
        # of conflicting use of identifier
        # e.g.
        #   a = 4         lvn.0 = 4
        #   a = 3    ->       a = 3
        self._identifier_to_rebuilt_ir = {}

    def add_entry(self, instruction):
        operator = instruction.get_operator_string()
        if operator in self.IGNORE_OPERATIONS:
            return None

        # Resolve the variable/identifier name
        destination = instruction.get_destination()
        if destination is None:
            destination = self.rename_identifier(len(self._entries))
        identifier = base.NumberingIdentifier(destination)


        # if there's conflicting use of identifier,
        #  1) change the table's variable name
        #  2) change the rebuilt instruciton's destination
        if identifier in self._identifiers:
            conflicting_entry = self._identifiers[identifier]
            renamed_destination = self.rename_identifier(
                conflicting_entry.number.get_string()
            )
            conflicting_entry.variable = base.NumberingIdentifier(
                renamed_destination
            )

            # must resolve conflicting ir first
            conflicting_ir = self._identifier_to_rebuilt_ir[identifier]
            conflicting_ir.set_destination(renamed_destination)
            self._identifier_to_rebuilt_ir[conflicting_entry.variable] = conflicting_ir


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

        # when the identifier argument is a number, this is the first time
        # using this entry, we are allowed to use the entry.variable
        if identifier.is_number():
            return self._build_ir(
                numbering_value.get_operator(),
                uses=uses,
                identifier=entry.variable,
                dest_type=numbering_value.get_type(),
            )

        # At this point, it's NOT the first time visiting the entry.
        # We are likely to generate an "id" instruction


        # The "id", "const" operations are special. We simply generate
        # its literal value even it's the second or more times visit
        if numbering_value.get_operator() in ["id", "const"]:
            return self._build_ir(
                numbering_value.get_operator(),
                uses=uses,
                identifier=identifier,
                dest_type=numbering_value.get_type()
            )

        referred_entry = self.get_entry_by_identifier(identifier)
        return self._build_ir(
            "id",
            uses=[referred_entry.variable.get_string()],
            identifier=identifier,
            dest_type=numbering_value.get_type()
        )

    def _build_ir(self, operator_string, uses, identifier, dest_type):
        new_ir = self._ir_builder.build_by_name(
            operator_string,
            uses=uses,
            destination=identifier.get_string(),
            dest_type=dest_type,
        )
        self._identifier_to_rebuilt_ir[identifier] = new_ir
        return new_ir

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
