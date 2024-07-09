#!/usr/bin/env python3

class Instruction(object):
    def __init__(self):
        raise NotImplementedError

    def get_type(self):
        raise NotImplementedError

    def get_operator_string(self):
        raise NotImplementedError

    def get_destination(self):
        raise NotImplementedError

    def get_value(self):
        raise NotImplementedError

    def get_arguments(self):
        raise NotImplementedError

    def is_label(self):
        return False

    def is_terminator(self):
        return False


class UnaryInstruction(Instruction):
    def __init__(self, operand, destination=None, dest_type=None):
        self._destination = destination
        self._operand = operand
        self._dest_type = dest_type

    def get_destination(self):
        return self._destination

    def get_arguments(self):
        return [self._operand]

    def get_type(self):
        return self._dest_type

    def dump_json(self):
        data = {}
        if self._destination is not None:
            data["dest"] = self._destination
            data["type"] = self._dest_type
        data["args"] = [self._operand]
        data["op"] = self.get_operator_string()
        return data


class BinaryInstruction(Instruction):
    def __init__(self, operand0, operand1,
                 destination=None, dest_type=None):
        self._destination = destination
        self._operand0 = operand0
        self._operand1 = operand1
        self._dest_type = dest_type

    def get_destination(self):
        return self._destination

    def get_arguments(self):
        return [self._operand0, self._operand1]

    def get_type(self):
        return self._dest_type

    def dump_json(self):
        data = {}
        if self._destination is not None:
            data["dest"] = self._destination
            data["type"] = self._dest_type
        data["args"] = [self._operand0, self._operand1]
        data["op"] = self.get_operator_string()
        return data


class ConstInstruction(UnaryInstruction):
    def get_value(self):
        return self._value

    def get_operator_string(self):
        return "const"

    def dump_json(self):
        """
        Though Const is an unary operation, the json representation is
        quite different.
        """
        data = {}
        data["op"] = self.get_operator_string()
        data["value"] = self._operand
        data["dest"] = self._destination
        data["type"] = self._dest_type
        return data


class IdInstruction(UnaryInstruction):
    def get_value(self):
        return self._reference

    def get_operator_string(self):
        return "id"


class PrintInstruction(UnaryInstruction):
    def __init__(self, operand, destination=None, dest_type=None):
        """Print instruction is similar to other unary operator yet
            does not have destination
        """
        self._operand = operand
        self._destination = None
        self._dest_type = None

    def get_value(self):
        return None

    def get_operator_string(self):
        return "print"


class LabelInstruction(Instruction):
    def __init__(self, name):
        self._name = name

    def is_label(self):
        return True

    def get_type(self):
        return None

    def get_operator_string(self):
        print("[WARNING] label instruciton does not have instruction")
        return None

    def get_value(self):
        return None

    def dump_json(self):
        data = {}
        data["label"] = self._name
        return data


class JumpInstruction(Instruction):
    def __init__(self, label):
        self._label = label

    def get_value(self):
        return None

    def get_destination(self):
        return None

    def get_operator_string(self):
        return "jmp"

    def get_arguments(self):
        return []

    def get_type(self):
        return None

    def is_terminator(self):
        return True

    def dump_json(self):
        data = {}
        data["op"] = self.get_operator_string()
        data["labels"] = [self._label]
        return data


class BranchInstruction(Instruction):
    def __init__(self, condition, label_on_true, label_on_false):
        self._condition = condition
        self._label_on_true = label_on_true
        self._label_on_false = label_on_false

    def get_value(self):
        return None

    def get_operator_string(self):
        return "br"

    def get_destination(self):
        return None

    def get_arguments(self):
        return [self._condition]

    def get_type(self):
        return None

    def is_termiator(self):
        return True

    def dump_json(self):
        data = {}
        data["op"] = self.get_operator_string()
        data["labels"] = [self._label_on_true,
                          self._label_on_false]
        data["args"] = [self._condition]
        return data


class AddInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "add"


class SubtractInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "sub"


class MultiplyInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "mul"


class DivideInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "div"


class EqualInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "eq"


class LessThanInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "lt"


class LessThanOrEqualToInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "le"


class GreaterThanInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "gt"


class GreaterThanOrEqualToInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "ge"


class NotInstruction(UnaryInstruction):
    def get_operator_string(self):
        return "not"


class AndInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "and"


class OrInstruction(BinaryInstruction):
    def get_operator_string(self):
        return "or"
