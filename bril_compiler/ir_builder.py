#!/usr/bin/env python3

from bril_compiler import ir

class IRBuilder:
    """An utility builder provides ways to build instructions.
        Not necessarily to use it.
    """
    def __init__(self):
        self.num_built = 0
        self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP = {
            "add": ir.AddInstruction,
            "sub": ir.SubtractInstruction,
            "mul": ir.MultiplyInstruction,
            "div": ir.DivideInstruction
        }
        self.UNARY_OPERATOR_CONSTRUCTOR_MAP = {
            "id": ir.IdInstruction,
            "print": ir.PrintInstruction,
            "const": ir.ConstInstruction,
        }

    def build_by_name(self, operator, destination=None, uses=[],
                      dest_type=None):
        if operator == "label":
            print("[Error] cannot create Label instruction by builder")
            quit()

        if operator == "jmp":
            return ir.JumpInstruction(uses[0])
        elif operator == "br":
            return ir.BranchInstruction(
                uses[0], uses[1], uses[2])
        elif operator in self.UNARY_OPERATOR_CONSTRUCTOR_MAP:
            return self.UNARY_OPERATOR_CONSTRUCTOR_MAP[operator](
                uses[0],
                destination,
                dest_type
            )
        elif operator in self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP:
            return self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP[operator](
                uses[0],
                uses[1],
                destination,
                dest_type
            )
        else:
            print(f"IRBuilder.build_by_name: Cannot handle {operator}")
            quit()
