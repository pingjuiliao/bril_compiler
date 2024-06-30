#!/usr/bin/env python3

class BasicBlock(object):
    def __init__(self):
        self._label = None
        self._instructions = []

    def set_label(self, label_instruction):
        self._label = label_instruction

    def get_label(self):
        return self._label

    def is_empty(self):
        return len(self._instructions) == 0

    def get_instructions(self):
        return self._instructions

    def add_instruction(self, instruction):
        self._instructions.append(instruction)


class Function(object):
    def __init__(self, identifier):
        self._identifier = identifier
        self._basic_blocks = []

    def get_identifier(self):
        return self._identifier

    def get_number_of_basic_blocks(self):
        return len(self._basic_blocks)

    def get_basic_blocks(self):
        return self._basic_blocks

    def add_basic_block(self, block):
        self._basic_blocks.append(block)


class Module(object):
    def __init__(self):
        self._functions = []

    def add_function(self, function):
        self._functions.append(function)

    def dump_json(self):
        module_json = {}
        module_json["functions"] = []
        for function in self._functions:
            function_json = {}
            function_json["name"] = function.get_identifier()
            function_json["instrs"] = []
            for basic_block in function.get_basic_blocks():
                # any basic block may contain one label instruction
                label_instr = basic_block.get_label()
                if label_instr is not None:
                    label_json = label_instr.dump_json()
                    function_json["instrs"].append(label_json)

                # append the rest of instruction
                for instruction in basic_block.get_instructions():
                    instr_json = instruction.dump_json()
                    function_json["instrs"].append(instr_json)
            module_json["functions"].append(function_json)
        # json.dump(module_json, sys.stdout)
        return module_json
