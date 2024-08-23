#!/usr/bin/env python3

import enum

from bril_compiler.optimization.redundancy.numbering import base

class NumberingExtensionType(enum.Enum):
    PRE_BUILD_TABLE_EXTENSION = 1
    POST_BUILD_TABLE_EXTENSION = 2
    RECONSTRUCTION_EXTENSION = 3


class NumberingExtension:
    def get_type(self):
        return self.type

    def _should_update(self, numbering_value):
        return numbering_value[0] == "id" and numbering_value[1].is_number()

    def _update_value(self, numbering_value, table):
        raise NotImplementedError

    def reset(self):
        return True

    def update(self, numbering_value, table):
        if not self._should_update(numbering_value):
            return numbering_value
        return self._update_value(numbering_value, table)


class CommutativityExtension(NumberingExtension):
    def __init__(self):
        self.type = NumberingExtensionType.PRE_BUILD_TABLE_EXTENSION
        self.COMMUTATIVITY_LIST = [
            "add", "mul", "sub", "div",
            "and", "or", "xor",
        ]

    def _should_update(self, numbering_value):
        op = numbering_value.get_operator()
        return op in self.COMMUTATIVITY_LIST

    def _update_value(self, numbering_value, table):
        operands = numbering_value.get_operands()
        if operands[0] < operands[1]:
            return numbering_value
        return base.NumberingValue(
            numbering_value.get_operator(),
            [operands[1], operands[0]],
            numbering_value.get_type()
        )


class IdentityPropagationExtension(NumberingExtension):
    def __init__(self):
        self.type = NumberingExtensionType.RECONSTRUCTION_EXTENSION
        self.sources = {}

    def _should_update(self, numbering_value):
        return numbering_value.get_operator() != "const"

    def _find_source_identifier(self, identifier, table):
        if identifier in self.sources:
            return self.sources[identifier]

        if not identifier.is_number():
            self.sources[identifier] = identifier
            return identifier

        referred_entry = table.get_entry_by_identifier(identifier)
        if not referred_entry.value.get_operator() == "id":
            self.sources[identifier] = identifier
            return identifier

        source_identifier = self._find_source_identifier(
            referred_entry.value.get_operands()[0], table
        )
        self.sources[identifier] = source_identifier
        return source_identifier

    def _update_value(self, numbering_value, table):
        new_operands = []
        for operand in numbering_value.get_operands():
            source_identifier = self._find_source_identifier(operand, table)
            new_operands.append(source_identifier)

        # print("numbering_value")
        # print([(k, v) for k, v in self.sources.items()])
        return base.NumberingValue(
            numbering_value.get_operator(),
            new_operands,
            numbering_value.get_type()
        )

    def reset(self):
        self.sources.clear()
        return True


class ConstantPropagationExtension(NumberingExtension):
    """The constant propagation extension, which should also work
    """

    def __init__(self):
        self.type = NumberingExtensionType.PRE_BUILD_TABLE_EXTENSION
        self.SIMULATIONS = {
            "add": lambda a: a[0] + a[1],
            "sub": lambda a: a[0] - a[1],
            "mul": lambda a: a[0] * a[1],
            "div": lambda a: a[0] // a[1],
            # "mod": lambda a: a[0] % a[1],
            "and": lambda a: a[0] and a[1],
            "or": lambda a: a[0] or a[1],
            "xor": lambda a: a[0] ^ a[1],
            "not": lambda a: not a[0],
            "lt": lambda a: a[0] < a[1],
            "gt": lambda a: a[0] > a[1],
            "eq": lambda a: a[0] == a[1],
            "le": lambda a: a[0] <= a[1],
            "ge": lambda a: a[0] >= a[1],
        }

    def _should_update(self, numbering_value):
        return numbering_value.get_operator() in self.SIMULATIONS

    def _presume_result(self, operator, operands):
        # print(f"presuming {operator} {operands}")
        if operator == "or" and True in operands:
            return True
        elif operator == "and" and False in operands:
            return False
        elif (operator in ["eq", "le", "ge"] and
              operands[0] == operands[1]):
            return True
        return None

    def _update_value(self, numbering_value, table):
        arguments = []
        for operand in numbering_value.get_operands():
            if not operand.is_number():
                arguments.append(operand)
                continue
            referred_entry = table.get_entry_by_identifier(operand)
            referred_value = referred_entry.value
            if referred_value.get_operator() != "const":
                arguements.append(operand)
                continue
            constant_primitive = referred_value.get_operands()[0]
            arguments.append(constant_primitive.get_value())

        operator = numbering_value.get_operator()
        presumed_result = self._presume_result(operator, arguments)
        if presumed_result is not None:
            presumed_result_primitive = base.NumberingPrimitive(presumed_result)
            return base.NumberingValue(
                "const", [presumed_result_primitive],
                numbering_value.get_type())

        for argument in arguments:
            if isinstance(argument, base.NumberingIdentifier):
                return numbering_value

        result = self.SIMULATIONS[operator](arguments)
        result_primitive = base.NumberingPrimitive(result)
        return base.NumberingValue(
            "const",
            [result_primitive],
            numbering_value.get_type()
        )

class IdentityToConstantInstructionExtension(NumberingExtension):
    def __init__(self):
        self.type = NumberingExtensionType.RECONSTRUCTION_EXTENSION

    def _should_update(self, numbering_value):
        return numbering_value.get_operator() == "id"

    def _update_value(self, numbering_value, table):
        source_value = numbering_value
        while True:
            if source_value.get_operator() != "id":
                return numbering_value
            operand = source_value.get_operands()[0]
            referred_entry = table.get_entry_by_identifier(operand)
            if referred_entry is None:
                return numbering_value
            source_value = referred_entry.value
            if source_value.get_operator() == "const":
                break
        # print(source_value)
        return source_value
