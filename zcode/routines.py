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

def setuproutine(address): 
    """set up the local variables and returns the address of the first instruction"""
    vars = []
    varnum = zcode.memory.getbyte(address)
    address += 1
    if zcode.header.zversion() < 5:
        for a in range(varnum):
            vars.append(zcode.memory.getword(address))
            address += 2
    else:
        for a in range(varnum):
            vars.append(0)
    zcode.game.currentframe.lvars = vars
    return address


def execloop(debug=False):
    global input
    global restart
    global oldpc
    global timerreturn

    while (restart == 0) and (quit == 0) and (timerreturn == False):
        try:
            if zcode.screen.ioScreen.resized:
                zcode.screen.ioScreen.resized=False
                zcode.screen.resize()
        except:
            pass
        
        if timerreturn == False:
            zcode.game.interrupt_call()
        oldpc = zcode.game.PC
        zcode.game.PC = zcode.instructions.decode(zcode.game.PC, debug)
        zcode.instructions.runops(oldpc, debug)                  
    timerreturn = False


def execstart(debug=False): 
    """set up the Z-Machine to start executing instructions"""
    global quit # if set to 1, game ends
    global restart
    if zcode.header.zversion() != 6:
        zcode.game.PC = zcode.header.initialPC()
    else:
        address = zcode.header.mainroutine()
        zcode.game.call(address, [], 0, 0, 1)
    execloop(debug)
    while restart:
        if zcode.header.zversion() != 6:
            zcode.game.PC = zcode.header.initialPC()
        else:
            address = zcode.header.mainroutine()
            zcode.game.call(address, [], 0, 0, 1)
        restart = 0
        execloop(debug)

