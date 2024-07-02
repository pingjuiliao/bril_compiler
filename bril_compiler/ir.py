#!/usr/bin/env python3

class Instruction(object):
    def __init__(self):
        raise NotImplementedError

    def get_type(self):
        return self._bril_type

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

    def dump_json(self):
        data = {}
        if self._destination is not None:
            data["dest"] = self._destination
            data["type"] = self._dest_type
        data["args"] = [self._operand]
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

    def dump_json(self):
        data = {}
        if self._destination is not None:
            data["dest"] = self._destination
            data["type"] = self._dest_type
        data["args"] = [self._operand0, self._operand1]
        return data


class ConstInstruction(UnaryInstruction):
    def get_value(self):
        return self._value

    def dump_json(self):
        """
        Though Const is an unary operation, the json representation is
        quite different.
        """
        data = {}
        data["op"] = "const"
        data["value"] = self._operand
        data["dest"] = self._destination
        data["type"] = self._dest_type
        return data


class IdInstruction(UnaryInstruction):
    def get_value(self):
        return self._reference

    def dump_json(self):
        data = super().dump_json()
        data["op"] = "id"
        return data


class PrintInstruction(UnaryInstruction):
    def get_value(self):
        return None

    def dump_json(self):
        data = super().dump_json()
        data["op"] = "print"
        return data


class LabelInstruction(Instruction):
    def __init__(self, name):
        self._name = name

    def is_label(self):
        return True

    def get_value(self):
        return None

    def dump_json(self):
        data = {}
        data["label"] = self._name
        return data


class JmpInstruction(UnaryInstruction):
    def get_value(self):
        return None

    def is_terminator(self):
        return True

    def dump_json(self):
        data = {}
        data["op"] = "jmp"
        data["labels"] = [self._operand]
        return data


class AddInstruction(BinaryInstruction):
    def get_value(self):
        return self._operand0 + self._operand1

    def dump_json(self):
        data = super().dump_json()
        data["op"] = "add"
        return data


class SubtractInstruction(BinaryInstruction):
    def get_value(self):
        return self._operand0 - self._operand1;

    def dump_json(self):
        data = super().dump_json()
        data["op"] = "sub"
        return data


class MultiplyInstruction(BinaryInstruction):
    def get_value(self):
        return self._operand0 * self._operand1

    def dump_json(self):
        data = super().dump_json()
        data["op"] = "mul"
        return data


class DivideInstruction(BinaryInstruction):
    def get_value(self):
        return self._operand0 // self._operand1;

    def dump_json(self):
        data["op"] = "div"
        return data
