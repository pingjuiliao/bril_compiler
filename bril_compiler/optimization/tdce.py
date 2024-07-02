#!/usr/bin/env python3

from bril_compiler.optimization import compiler_pass

class TrivilDeadCodeEliminationPass(compiler_pass.BrilPass):
    def __init__(self):
        self.modules = 0

    def optimize(self, module):
        self.dead_store_elimination(module)
        self.unused_instruction_elimination(module)

    def unused_instruction_elimination(self, module):
        """remove instruction that is never used by the function"""

        for function in module.get_functions():
            program_changed = True
            while program_changed:
                program_changed = False
                used = set()
                for basic_block in function.get_basic_blocks():
                    for instruction in basic_block.get_instructions():
                        for arg in instruction.get_arguments():
                            used.add(arg)
                for basic_block in function.get_basic_blocks():
                    instructions = basic_block.get_instructions()
                    # iterate instructions and delete unused
                    for i, instruction in enumerate(instructions):
                        destination = instruction.get_destination()
                        if (destination is not None and
                            destination not in used):
                            program_changed = True
                            instructions[i] = None

                    # delete the unusd instruction that previously mark
                    # as None
                    new_instructions = [
                        instruction for instruction in instructions
                        if instruction is not None
                    ]
                    basic_block.transform_into(new_instructions)



    def dead_store_elimination(self, module):
        """Eliminate a store of value without clear use
        a = 4;
        a = 2;
        print a;
        """
        last_defined = {}
        for function in module.get_functions():
            for basic_block in function.get_basic_blocks():
                instructions = basic_block.get_instructions()

                # algorithm starts
                last_defined = {}
                for i, instruction in enumerate(instructions):
                    # cancel all the use of arguments
                    for arg in instruction.get_arguments():
                        if arg in last_defined:
                            last_defined[arg] = None

                    # check for definition
                    dest = instruction.get_destination()
                    if (dest in last_defined and
                        last_defined[dest] is not None):
                        instructions[last_defined[dest]] = None
                    last_defined[dest] = i

                # update the BasicBlock object
                new_instructions = [
                    instruction for instruction in instructions
                    if instruction is not None
                ]
                basic_block.transform_into(new_instructions)


