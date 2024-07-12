#!/usr/bin/env python3

class LVNUse:
    def __init__(self):
        raise NotImplementedError


class LVNPrimitive(LVNUse):
    def __init__(self, literal_value):
        self.value = literal_value

    def get_value(self):
        return self.value

    def __repr__(self):
        return f"{self.value}"


class LVNIdentifier(LVNUse):
    def __init__(self, identifier):
        self._name = None
        self._number = None
        if isinstance(identifier, str):
            self._name = identifier
        elif isinstance(identifier, int):
            self._number = identifier
        else:
            print(hello)
            print(f"Cannot handle this type of identifier {identifier}")
            quit()

    def is_number(self):
        return self._number is not None

    def is_named_identifier(self):
        return self._name is not None

    def get_number(self):
        return self._number

    def get_named_identifier(self):
        return self._name

    def __lt__(self, other):
        if (self._name is not None) ^ (other._name is not None):
            return self._name is not None
        elif self._name is not None:
            return self._name < other._name
        return self._number < other._number

    def __eq__(self, other):
        if self._name is not None:
            return self._name == other._name
        return self._number == other._number

    def __hash__(self):
        if self._name is not None:
            return hash(self._name)
        return hash(self._number)

    def __repr__(self):
        if self._number is not None:
            return f"#{self._number}"
        return f'"{self._name}"'


class LVNValue:
    def __init__(self, operator, operands, value_type):
        self.operator = operator
        self.operands = self._handle_commutativity(operands)
        self.value_type = value_type
        # for hashing
        strings = [operator] + [str(op) for op in operands]
        self.key = ','.join(strings)

    def _handle_commutativity(self, operands):
        if len(operands) == 1:
            return operands
        return sorted(operands)

    def is_id_instruction(self):
        return self.operator == "id"

    def get_operator(self):
        return self.operator

    def get_operands(self):
        return self.operands

    def get_type(self):
        return self.value_type

    def get_reference(self):
        if not self.is_id_instruction():
            return None
        print(f"reference: {self.operands[0]}")
        return self.operands[0]

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        s = f"({self.operator}"
        for operand in self.operands:
            s += f", {operand}"
        s += ")"
        return s
