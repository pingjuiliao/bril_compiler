#!/usr/bin/env python3

from bril_compiler.optimization import compiler_pass

class TrivilDeadCodeEliminationPass(compiler_pass.BrilPass):
    def __init__(self):
        self.modules = 0

    def optimize(self, module):
        while (self.unused_instruction_elimination(module) or
               self.dead_store_elimination(module)):
            pass

        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                instructions = basic_block.get_instructions()
                new_instructions = [
                    instruction for instruction in instructions
                    if instruction is not None
                ]
                basic_block.transform_into(new_instructions)

        return True

    def unused_instruction_elimination(self, module):
        program_changed = False
        for function in module.get_functions():
            program_changed |= (
                self.unused_instruction_elimination_algorithm(function)
            )
        return program_changed


    def unused_instruction_elimination_algorithm(self, function):
        program_changed = False
        used = set()
        for basic_block in function.get_basic_blocks():
            for instruction in basic_block.get_instructions():
                if instruction is None:
                    continue
                for arg in instruction.get_arguments():
                    used.add(arg)

        for basic_block in function.get_basic_blocks():
            instructions = basic_block.get_instructions()
            for i, instruction in enumerate(instructions):
                if instruction is None:
                    continue
                destination = instruction.get_destination()
                if (destination is not None and
                    destination not in used):
                    program_changed = True
                    instructions[i] = None # mark as deleted

        return program_changed

    def dead_store_elimination(self, module):
        program_changed = False
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                program_changed |= (
                    self.dead_store_elimination_algorithm(basic_block)
                )
        return program_changed

    def dead_store_elimination_algorithm(self, basic_block):
        program_changed = False
        last_defined = {}
        instructions = basic_block.get_instructions()
        for i, instruction in enumerate(instructions):
            if instruction is None:
                continue
            for arg in instruction.get_arguments():
                if arg in last_defined:
                    last_defined[arg] = None

            destination = instruction.get_destination()
            if destination is None:
                continue

            if (destination in last_defined and
                last_defined[destination] is not None):
                program_changed = True
                last_defined_index = last_defined[destination]
                instructions[last_defined_index] = None
            last_defined[destination] = i

        return program_changed

