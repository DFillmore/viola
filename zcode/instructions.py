# Copyright (C) 2001 - 2019 David Fillmore
#
# This file is part of Viola.
#
# Viola is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Viola is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

operands = []

import zcode


def decode(address):
    global operands
    if zcode.debug:
        print(hex(address), end=' ')
    operands = []
    optype = zcode.memory.getbyte(address)
    if optype < 0x20: # long 2OP, small constant, small constant
        operands.append(zcode.memory.getbyte(address + 1))
        operands.append(zcode.memory.getbyte(address + 2))
        address += 3
    elif optype < 0x40: # long 2OP, small constant, variable
        operands.append(zcode.memory.getbyte(address + 1))
        operands.append(zcode.game.getvar(zcode.memory.getbyte(address+2)))
        address += 3
    elif optype < 0x60: # long 2OP, variable, small constant
        operands.append(zcode.game.getvar(zcode.memory.getbyte(address+1)))
        operands.append(zcode.memory.data[address + 2])
        address += 3
    elif optype < 0x80: # long 2OP, variable, variable
        operands.append(zcode.game.getvar(zcode.memory.getbyte(address+1)))
        operands.append(zcode.game.getvar(zcode.memory.getbyte(address+2)))
        address += 3
    elif optype < 0x90: # short 1OP, large constant
        operands.append(zcode.memory.getword(address + 1))
        address += 3
    elif optype < 0xA0: # short 1OP, small constant
        operands.append(zcode.memory.getbyte(address + 1))
        address += 2
    elif optype < 0xB0: # short 1OP, variable
        operands.append(zcode.game.getvar(zcode.memory.getbyte(address+1)))
        address += 2
    elif optype < 0xC0: # short 0OP
        address += 1
    elif optype < 0xE0: # variable 2OP
        address += 1
        operandtype = zcode.memory.getbyte(address)
        for x in range(6,-2,-2):
            if ((operandtype >> x) & 3) == 0:
                address += 1
                operands.append(zcode.memory.getword(address))
                address += 1
            elif ((operandtype >> x) & 3) == 1:
                address += 1
                operands.append(zcode.memory.getbyte(address))
            elif ((operandtype >> x) & 3) == 2:
                address += 1
                operands.append(zcode.game.getvar(zcode.memory.getbyte(address)))
            else:
                pass
        address += 1
    elif optype < 0x100: # variable VAR  
        address += 1  
        if (optype & 0x1f == 12) or (optype & 0x1f == 26): # if the opcode is call_vs2 or call_vn2, there can be up to 8 operands
            operandtype = zcode.memory.getword(address) 
            address += 1
            for x in range(14,-2,-2):
            
                if ((operandtype >> x) & 3) == 0:
                    address += 1
                    operands.append(zcode.memory.getword(address))
                    address += 1        
                elif ((operandtype >> x) & 3) == 1:
                    address += 1
                    operands.append(zcode.memory.getbyte(address))
                elif ((operandtype >> x) & 3) == 2:
                    address += 1
                    operands.append(zcode.game.getvar(zcode.memory.getbyte(address)))
                else:
                    pass
        else:
            operandtype = zcode.memory.getbyte(address)
            for x in range(6,-2,-2):
                if ((operandtype >> x) & 3) == 0:
                    address += 1
                    operands.append(zcode.memory.getword(address))
                    address += 1
                elif ((operandtype >> x) & 3) == 1:
                    address += 1
                    operands.append(zcode.memory.getbyte(address))
                elif ((operandtype >> x) & 3) == 2:
                    address += 1
                    operands.append(zcode.game.getvar(zcode.memory.getbyte(address)))
                else:
                    pass
        address += 1
    return address

def decodeextended(address):
    global operands
    address += 1
    operandtype = zcode.memory.getbyte(address)
    y = 8
    for x in range(1,5):
        y = y - 2
        if ((operandtype >> y) & 3) == 0:
            address += 1
            operands.append(zcode.memory.getword(address))
            address += 1
        elif ((operandtype >> y) & 3) == 1:
            address += 1
            operands.append(zcode.memory.getbyte(address))
        elif ((operandtype >> y) & 3) == 2:
            address += 1
            operands.append(zcode.game.getvar(zcode.memory.getbyte(address)))
        else:
            pass
    address += 1
    return address

inputInstruction = False
    
def runops(address):
    global inputInstruction
    optype = zcode.memory.getbyte(address)
    optable = None
    mask = 0x1f
    if optype < 0x80:
        if zcode.debug:
            print(zcode.optables.op2[optype & 0x1f].__name__.replace('z_', '@'), end=' ')
        optable = zcode.optables.op2
        #zcode.optables.op2[optype & 0x1f]()
    elif optype < 0xb0:
        if zcode.debug:
            print(zcode.optables.op1[optype & 0xf].__name__.replace('z_', '@'), end=' ')
        optable = zcode.optables.op1
        mask = 0xf
        #zcode.optables.op1[optype & 0xf]()
    elif optype < 0xc0:
        if zcode.optables.op0[optype & 0xf].__name__ != 'z_extended' and zcode.debug:
            print(zcode.optables.op0[optype & 0xf].__name__.replace('z_', '@'), end=' ')
        optable = zcode.optables.op0
        mask = 0xf
        #zcode.optables.op0[optype & 0xf]()
    elif optype < 0xe0:
        if zcode.debug:
            print(zcode.optables.op2[optype & 0x1f].__name__.replace('z_', '@'), end=' ')
        optable = zcode.optables.op2
        #zcode.optables.op2[optype & 0x1f]()
    elif optype < 0x100:
        if zcode.debug:
            print(zcode.optables.opvar[optype & 0x1f].__name__.replace('z_', '@'), end=' ')
        if optype & 0x1f == 0x4 or optype & 0x1f == 0x16:
            inputInstruction = True
        else:
            inputInstruction = False
        optable = zcode.optables.opvar
        #zcode.optables.opvar[optype & 0x1f]()
    if zcode.debug:
        for a in operands:
            print(a, end=' ')
    optable[optype & mask]()
    if zcode.debug:
        print()

def store(value):
    value = zcode.numbers.unsigned(value)
    var = zcode.memory.getbyte(zcode.game.PC)
    if zcode.debug:
        print('->', var, end=' ')
    zcode.game.PC += 1
    zcode.game.setvar(var, value)

def branch(condition):
    if zcode.debug:
        print('?', end='')
    byte1 = zcode.memory.getbyte(zcode.game.PC)
    zcode.game.PC += 1
    if byte1 & 64 == 64: # if bit 6 is set, branch information only occupies 1 byte
        offset = byte1 & 63
    else: # if bit 6 is clear, branch information occupies 2 bytes
        byte2 = zcode.memory.getbyte(zcode.game.PC)
        offset = ((byte1 & 63) << 8) + byte2
        zcode.game.PC += 1

    # the offset is a 14-bit signed number, so we have to convert it a bit.
    if ((offset >> 13) & 1 == 1) and (offset != 0): 
        offset = offset - 0x4000
        
    if (byte1 & 128 == 128) and (condition == 1): # if the top bit is set, branch on true
        dobranch = 1
    elif (byte1 & 128 != 128) and (condition == 0): # if it isn't set, branch on false
        if zcode.debug:
            print('~', end='')
        dobranch = 1
    else:
        dobranch = 0
    if zcode.debug:
        if offset == 0:
            print('rfalse', end=' ')
        elif offset == 1:
            print('rtrue', end=' ')
        else:
            print(hex(zcode.game.PC + offset - 2), end=' ')
    if dobranch == 1:
        if zcode.debug:
            print('(success)', end=' ')
        if offset == 0:
            zcode.game.ret(0)
        elif offset == 1:
            zcode.game.ret(1)
        else:
            zcode.game.PC = zcode.game.PC + offset - 2
    elif zcode.debug:
        print('(fail)', end=' ')

        
