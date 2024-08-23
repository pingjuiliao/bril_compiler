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

    def clear_instructions(self):
        """Instruction deletion"""
        self._instructions = []

    def transform_into(self, instructions):
        """a update all instructions"""
        self._instructions = instructions


    def add_instruction(self, instruction):
        self._instructions.append(instruction)


class Function(object):
    def __init__(self, identifier):
        self._identifier = identifier
        self._basic_blocks = []
        # tuple (name, type)
        self.arguments = []

    def get_identifier(self):
        return self._identifier

    def get_number_of_basic_blocks(self):
        return len(self._basic_blocks)

    def get_basic_blocks(self):
        return self._basic_blocks

    def add_basic_block(self, block):
        self._basic_blocks.append(block)

    def add_argument(self, name, arg_type):
        self.arguments.append((name, arg_type))

    def dump_json(self):
        function_json = {}
        # function name
        function_json["name"] = self.get_identifier()

        # function arguemnts:
        function_json['args'] = []
        for arg_name, arg_type in self.arguments:
            function_json['args'].append({
                'name': arg_name,
                'type': arg_type
            })

        # instrs
        function_json['instrs'] = []
        for basic_block in self.get_basic_blocks():
            label_instr = basic_block.get_label()
            if label_instr is not None:
                label_json = label_instr.dump_json()
                function_json['instrs'].append(label_json)

            for instr in basic_block.get_instructions():
                instr_json = instr.dump_json()
                function_json['instrs'].append(instr_json)

        return function_json


class Module(object):
    def __init__(self):
        self._functions = []

    def get_functions(self):
        return self._functions

    def add_function(self, function):
        self._functions.append(function)

    def dump_json(self):
        module_json = {}
        module_json["functions"] = []
        for function in self._functions:
            function_json = function.dump_json()
            module_json["functions"].append(function_json)
        # json.dump(module_json, sys.stdout)
        return module_json
