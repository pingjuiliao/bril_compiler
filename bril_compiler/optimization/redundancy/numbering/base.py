#!/usr/bin/env python3

class NumberingUse:
    def __init__(self):
        raise NotImplementedError


class NumberingPrimitive(NumberingUse):
    def __init__(self, literal_value):
        self.value = literal_value

    def get_value(self):
        return self.value

    def __repr__(self):
        return f"{self.value}"


class NumberingIdentifier(NumberingUse):
    """The identifier class for the Numbering table.
        We consider both the number and the named identifier as the identifier since they should be uniquely refering to the same value.
    """
    def __init__(self, identifier):
        self._name = None
        self._number = None
        if isinstance(identifier, str):
            self._name = identifier
        elif isinstance(identifier, int):
            self._number = identifier
        else:
            print(f"NumberingIdentifier.__init__(): unsupported identifier")
            quit()

    def get_string(self):
        if self.is_number():
            return str(self._number)
        return self._name

    def rename_as(self, new_name):
        if self.is_number():
            return False
        self._name = new_name
        return True

    def is_number(self):
        return self._number is not None

    def is_named_identifier(self):
        return self._name is not None

    def __eq__(self, another):
        if self.is_number() ^ another.is_number():
            return False
        return (self._number == another._number or
                self._name == another._name)

    def __lt__(self, another):
        if self.is_number() ^ another.is_number():
            return self.is_number() # number go first
        if self.is_number():
            return self._number < another._number
        return self._name < another._name

    def __hash__(self):
        if self.is_number():
            return hash(self._number)
        return hash(self._name)

    def __repr__(self):
        if self._number is not None:
            return f"#{self._number}"
        return self._name


class NumberingValue:
    def __init__(self, operator, operands, value_type):
        self.operator = operator
        self.operands = operands
        self.type = value_type

        strings = [operator] + [str(op) for op in operands]
        self.key = ','.join(strings)

    def get_operator(self):
        return self.operator

    def get_operands(self):
        return self.operands

    def get_type(self):
        return self.type

    def __eq__(self, another):
        return self.key == another.key

    def __hash__(self):
        return hash(self.key)

    def __repr__(self):
        s = f"({self.operator}"
        for operand in self.operands:
            s += f", {operand}"
        s += ")"
        return s
