# Copyright (C) 2001 - 2014 David Fillmore
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
#
# You should have received a copy of the GNU General Public License
# along with Viola; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import zio as io

quit = 0
input = 0
scrolling = 0
restart = 0
timerreturn = False

import zcode

def setup():
    global quit, input, scrolling, restart
    quit = 0
    input = 0
    scrolling = 0
    restart = 0

def setuproutine(address): # sets up the local variables and returns the address of the first instruction
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
    #debug = False

    zcode.screen.cursoroff()
    while (restart == 0) and (quit == 0) and (timerreturn == False) and (scrolling == 0):
        if timerreturn == False:
            zcode.game.interrupt_call()
        oldpc = zcode.game.PC
        zcode.game.PC = zcode.instructions.decode(zcode.game.PC, debug)
        zcode.instructions.runops(oldpc, debug)
        zcode.header.updateFontSize()
        #if (zcode.output.streams[2].active == False) and (zcode.header.getflag(2,0) == 1): # if the transcription bit has just been set, start transcription
        #    zcode.output.openstream(2)
        #if (zcode.output.streams[2].active) and (zcode.header.getflag(2,0) == 0): # if however it has just been unset, stop transcription
        #    zcode.output.closestream(2)
        if (zcode.screen.fixedpitchbit == False) and (zcode.header.getflag(2,1) == 1):
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = True
        if (zcode.screen.fixedpitchbit) and (zcode.header.getflag(2,1) == 0):
            zcode.screen.currentWindow.flushTextBuffer()
            zcode.screen.fixedpitchbit = False
        if input > 0:
            zcode.game.PC = oldpc # if we've hit an input instruction, we'll need to call it again
    timerreturn = False


def execstart(debug=False): # sets up the Z-Machine to start executing instructions
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

