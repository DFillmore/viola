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

quit = 0
input = 0
restart = 0
timerreturn = False

import zcode
import vio.zcode as io

def setup():
    global quit, input, restart
    quit = 0
    input = 0
    restart = 0
    
static_routines = {}

def setuproutine(address): 
    """set up the local variables and returns the address of the first instruction"""
    global static_routines
    if address in static_routines:
        zcode.game.currentframe.lvars = static_routines[address]['vars'][:]
        return static_routines[address]['address']
    inaddress = address
    vars = []
    varnum = zcode.memory.getbyte(address)
    address += 1
    if zcode.header.zversion < 5:
        for a in range(varnum):
            vars.append(zcode.memory.getword(address))
            address += 2
    else:
        for a in range(varnum):
            vars.append(0)
    zcode.game.currentframe.lvars = vars
    if zcode.debug:
        print()
        print(varnum, 'local variables', end='')
    if address > zcode.header.statmembase:
        routine = {'address':address, 'vars':vars[:]}
        static_routines[inaddress] = routine
    return address


def execloop():
    global input
    global restart
    global oldpc
    global timerreturn
    global quit
    
    while (restart == 0) and (quit == 0) and (timerreturn == False):
        try:
            if zcode.screen.ioScreen.resized:
                zcode.screen.ioScreen.resized=False
                zcode.screen.resize()
        except:
            pass
        
        if len(zcode.game.interruptstack) > 0:
            zcode.game.interrupt_call()
        oldpc = zcode.game.PC
        zcode.game.PC = zcode.instructions.decode(zcode.game.PC)
        zcode.instructions.runops(oldpc)             
    timerreturn = False


def execstart(): 
    """set up the Z-Machine to start executing instructions"""
    global quit # if set to 1, game ends
    global restart
    if zcode.header.zversion != 6:
        zcode.game.PC = zcode.header.initialPC
    else:
        address = zcode.header.mainroutine
        zcode.game.call(address, [], 0, 0, 1)
    execloop()
    while restart:
        if zcode.header.zversion != 6:
            zcode.game.PC = zcode.header.initialPC
        else:
            address = zcode.header.mainroutine
            zcode.game.call(address, [], 0, 0, 1)
        restart = 0
        execloop()

