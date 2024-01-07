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

instructions = {}
branches = {}

import zcode


def decode(address):
    global operands
    global instructions
    inaddress = address
    if zcode.debug:
        print(hex(address), end=' ')
    operands = []
    
    if address in instructions:
        operands = instructions[address]['operands']
        for a in operands:
            if a['type'] == 2: # variable
                varnum = a['varnum']
                a['value'] = zcode.game.getvar(varnum)
            
        return instructions[address]['raddress']
    optype = zcode.memory.getbyte(address)
    if optype < 0x20: # long 2OP, small constant, small constant
        op1 = {'type':1, 'varnum':None, 'value':zcode.memory.getbyte(address + 1)}
        op2 = {'type':1, 'varnum':None, 'value':zcode.memory.getbyte(address + 2)}
        operands.extend([op1, op2])
        address += 3
    elif optype < 0x40: # long 2OP, small constant, variable
        op1 = {'type':1, 'varnum':None, 'value': zcode.memory.getbyte(address + 1)}
        varnum = zcode.memory.getbyte(address+2)
        op2 = {'type':2, 'varnum':varnum, 'value': zcode.game.getvar(varnum)}
        operands.extend([op1,op2])
        address += 3
    elif optype < 0x60: # long 2OP, variable, small constant
        varnum = zcode.memory.getbyte(address+1)
        op1 = {'type':2, 'varnum':varnum, 'value': zcode.game.getvar(varnum)}
        op2 = {'type':1, 'varnum':None, 'value': zcode.memory.getbyte(address + 2)}
        operands.extend([op1, op2])
        address += 3
    elif optype < 0x80: # long 2OP, variable, variable
        varnum1 = zcode.memory.getbyte(address+1)
        varnum2 = zcode.memory.getbyte(address+2)
        op1 = {'type':2, 'varnum':varnum1, 'value': zcode.game.getvar(varnum1)}
        op2 = {'type':2, 'varnum':varnum2, 'value': zcode.game.getvar(varnum2)}
        operands.extend([op1, op2])
        address += 3
    elif optype < 0x90: # short 1OP, large constant
        op1 = {'type':0, 'varnum':None, 'value': zcode.memory.getword(address + 1)}
        operands.append(op1)
        address += 3
    elif optype < 0xA0: # short 1OP, small constant
        op1 = {'type':1, 'varnum':None, 'value': zcode.memory.getbyte(address + 1)}
        operands.append(op1)
        address += 2
    elif optype < 0xB0: # short 1OP, variable
        varnum = zcode.memory.getbyte(address+1)
        op1 = {'type':2, 'varnum':varnum, 'value': zcode.game.getvar(varnum)}
        operands.append(op1)
        address += 2
    elif optype < 0xC0: # short 0OP
        address += 1
    elif optype < 0xE0: # variable 2OP
        address += 1
        operandtypes = zcode.memory.getbyte(address)
        for x in range(6,-2,-2):
            otype = (operandtypes >> x) & 3
            if otype == 0: # large constant
                address += 1
                operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getword(address)})
                address += 1
            elif otype == 1: # small constant
                address += 1
                operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getbyte(address)})
            elif otype == 2: # variable
                address += 1
                varnum = zcode.memory.getbyte(address)
                operands.append({'type':otype, 'varnum':varnum, 'value':zcode.game.getvar(varnum)})
            else:
                pass
        address += 1
    elif optype < 0x100: # variable VAR  
        address += 1  
        if (optype & 0x1f == 12) or (optype & 0x1f == 26): # if the opcode is call_vs2 or call_vn2, there can be up to 8 operands
            operandtypes = zcode.memory.getword(address) 
            address += 1
            for x in range(14,-2,-2):
                otype = (operandtypes >> x) & 3
                if otype == 0: # large constant
                    address += 1
                    operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getword(address)})
                    address += 1
                elif otype == 1: # small constant
                    address += 1
                    operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getbyte(address)})
                elif otype == 2: # variable
                    address += 1
                    varnum = zcode.memory.getbyte(address)
                    operands.append({'type':otype, 'varnum':varnum, 'value':zcode.game.getvar(varnum)})
                else:
                    pass
        else:
            operandtypes = zcode.memory.getbyte(address)
            for x in range(6,-2,-2):
                otype = (operandtypes >> x) & 3
                if otype == 0: # large constant
                    address += 1
                    operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getword(address)})
                    address += 1
                elif otype == 1: # small constant
                    address += 1
                    operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getbyte(address)})
                elif otype == 2: # variable
                    address += 1
                    varnum = zcode.memory.getbyte(address)
                    operands.append({'type':otype, 'varnum':varnum, 'value':zcode.game.getvar(varnum)})
                else:
                    pass
        address += 1
    if address > zcode.header.statmembase:
        instructions[inaddress] = {'operands':operands, 'raddress':address}
    return address

def decodeextended(address):
    global operands
    if address in instructions:
        operands = instructions[address]['operands']
        for a in operands:
            if a['type'] == 2: # variable
                varnum = a['varnum']
                a['value'] = zcode.game.getvar(varnum)            
        return instructions[address]['raddress']
        
    inaddress = address
    address += 1
    operandtypes = zcode.memory.getbyte(address)
    for x in range(6,-2,-2):
        otype = (operandtypes >> x) & 3
        if otype == 0: # large constant
            address += 1
            operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getword(address)})
            address += 1
        elif otype == 1: # small constant
            address += 1
            operands.append({'type':otype, 'varnum':None, 'value':zcode.memory.getbyte(address)})
        elif otype == 2: # variable
            address += 1
            varnum = zcode.memory.getbyte(address)
            operands.append({'type':otype, 'varnum':varnum, 'value':zcode.game.getvar(varnum)})
        else:
            pass
    address += 1
    if address > zcode.header.statmembase:
        instructions[inaddress] = {'operands':operands, 'raddress':address}
    return address

inputInstruction = False
    
def runops(address):
    global inputInstruction
    if address in instructions:
        try:
            instructions[address]['optable']['opcode']()
        except:
            pass
    optype = zcode.memory.getbyte(address)
    optable = None
    mask = 0x1f
    if optype < 0x80:
        optable = zcode.optables.op2
    elif optype < 0xb0:
        optable = zcode.optables.op1
        mask = 0xf
    elif optype < 0xc0:
        optable = zcode.optables.op0
        mask = 0xf
    elif optype < 0xe0:
        optable = zcode.optables.op2
    elif optype < 0x100:
        if optype & 0x1f == 0x4 or optype & 0x1f == 0x16:
            inputInstruction = True
        else:
            inputInstruction = False
        optable = zcode.optables.opvar
    opcode = optype & mask
    if zcode.debug:
        print(optable[opcode].__name__.replace('z_', '@'), end=' ')
        b = 0
        for op in operands:
            if op['type'] == 2:
                if op['varnum'] == 0:
                    print('stack(', end='')
                elif op['varnum'] < 0x10:
                    print('l' + str(op['varnum']-1), end='(')
                else:
                    print('g' + str(op['varnum']-0x10), end='(')
                print(op['value'], end=') ')
            elif op['type'] == 1:
                print('#', end='')
                print(f"{op['value']:02d}", end=' ')
            elif op['type'] == 0:
                print('#', end='')
                print(f"{op['value']:04d}", end=' ')
            
    if address > zcode.header.statmembase:
        instructions[address]['optable'] = optable
        instructions[address]['opcode'] = opcode
    optable[opcode]()
    if zcode.debug:
        print()

def store(value):
    value = zcode.numbers.unsigned(value)
    var = zcode.memory.getbyte(zcode.game.PC)
    zcode.game.PC += 1
    zcode.game.setvar(var, value)
    if zcode.debug:
        if var == 0:
            print('-> stack =', zcode.game.currentframe.evalstack, end=' ')
        else:
            if var < 0x10:
                varname = 'local' + str(var-1)
            else:
                varname = 'global' + str(var-0x10) 
            print('->', varname, '=', value, end=' ')


def branch(condition):
    global branches
    if zcode.debug:
        print('?', end='')
    inaddress = zcode.game.PC
    if inaddress in branches:
        bdata = branches[inaddress]
        offset = bdata['offset']
        byte1 = bdata['mode']
        zcode.game.PC = bdata['branchfrom']
    else:
        byte1 = zcode.memory.getbyte(zcode.game.PC)
        zcode.game.PC += 1
        if byte1 & 64: # if bit 6 is set, branch information only occupies 1 byte
            offset = byte1 & 63
        else: # if bit 6 is clear, branch information occupies 2 bytes
            byte2 = zcode.memory.getbyte(zcode.game.PC)
            offset = ((byte1 & 63) << 8) + byte2
            zcode.game.PC += 1

        # the offset is a 14-bit signed number, so we have to convert it a bit.
        
        offset -= ((offset & 0x2000) * 2)

    if zcode.debug and not byte1 & 128:
        print('~', end='')
    
    # if the top bit is set, branch on true
    # if it isn't set, branch on false
    if (byte1 & 128 == condition << 7): 
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
    branchfrom = zcode.game.PC
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
    if inaddress > zcode.header.statmembase:
        branches[inaddress] = {'offset': offset, 'mode': byte1, 'branchfrom': branchfrom}

        
