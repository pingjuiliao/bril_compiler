#!/usr/bin/env python3

import json
import os
import sys

from bril_compiler import program
from bril_compiler import constant
from bril_compiler import ir

class BrilParser(object):
    def __init__(self):
        raise NotImplementedError

    def parse(self, filename):
        raise NotImplementedError


class JSonToBrilParser(BrilParser):
    def __init__(self):
        self._num_file_parsed = 0
        self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP = {
            "add": ir.AddInstruction,
            "sub": ir.SubtractInstruction,
            "mul": ir.MultiplyInstruction,
            "div": ir.DivideInstruction,
        }
        self.UNARY_OPERATOR_CONSTRUCTOR_MAP = {
            "id": ir.IdInstruction,
            "print": ir.PrintInstruction,
        }


    def parse(self, file_path):
        data = self._text_to_json(file_path)
        module = program.Module()
        for function_json in data['functions']:
            # function
            function = program.Function(function_json['name'])

            # parse JSon and generate a list of instructions
            instructions = []
            for instr_json in function_json['instrs']:
                instruction = self._json_to_instruction(instr_json)
                instructions.append(instruction)

            # form basic blocks
            self._form_basic_blocks(function, instructions)

            # add function into module
            module.add_function(function)
        return module

    def _form_basic_blocks(self, function, instructions):
        """
        Setup instrucitons in function in place
        """
        curr_block = program.BasicBlock()
        for instruction in instructions:
            # Do not include the label instruction
            if instruction.is_label():
                if not curr_block.is_empty():
                    function.add_basic_block(curr_block)
                    curr_block = program.BasicBlock()
                curr_block.set_label(instruction)
                continue

            # not a label: add instruction anyway
            curr_block.add_instruction(instruction)
            if instruction.is_terminator():
                function.add_basic_block(curr_block)
                curr_block = program.BasicBlock()

        if not curr_block.is_empty():
            function.add_basic_block(curr_block)

    def _text_to_json(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error {file_path} does not exist.")
            quit()
        TMP_FILE = "./tmp.json"
        os.system(f"bril2json < {file_path} > {TMP_FILE}")
        fp = open(TMP_FILE, "rb")
        return json.load(fp)

    def _json_to_instruction(self, instr_json):
        operator = instr_json["op"]
        if operator == "label":
            return ir.LabelInstruction(instr_json["label"])
        elif operator == "const":
            return ir.ConstInstruction(instr_json["value"],
                                       instr_json["dest"],
                                       instr_json["type"])
        elif operator in self.UNARY_OPERATOR_CONSTRUCTOR_MAP:
            if "dest" not in instr_json:
                instr_json["dest"] = None
                instr_json["type"] = None
            return self.UNARY_OPERATOR_CONSTRUCTOR_MAP[operator](
                instr_json["args"][0],
                instr_json["dest"],
                instr_json["type"]
            )
        elif operator in self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP:
            return self.BINARY_ARITHMETIC_CONSTRUCTOR_MAP[operator](
                instr_json["args"][0],
                instr_json["args"][1],
                instr_json["dest"],
                instr_json["type"]
            )
        else:
            print(f"instr_json.op == {instr_json.op}")
            raise NotImplementedError

if __name__ == "__main__":
    parser = JSonToBrilParser()
    module = parser.parse("test/bril/tdce/simple.bril")
    data = module.dump_json()
    json.dump(data, sys.stdout)
