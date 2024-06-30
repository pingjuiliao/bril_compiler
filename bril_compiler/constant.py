#!/usr/bin/env python3

import enum

BrilType = enum.Enum('BrilType', [
                     'INT', 'FLOAT'])

BrilOperator = enum.Enum('BrilOperator', [
                         'CONST', 'ID', 'PRINT', 'JMP',
                         'ADD', 'SUBTRACT', 'MUTIPLY', 'DIVIDE'])


