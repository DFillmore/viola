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

import sys
import copy
import os

import quetzal
import vio.zcode as io
import zcode


returning = False


undolist = []

LARGEST_STACK = 0

interruptstack = []

INT_INPUT = 1
INT_NEWLINE = 2
INT_SOUND = 3

class interruptdata:
    def __init__(self, itype, routine):
        self.routine = routine
        self.type = itype
    routine = None
    type = 0


def setup():
    global PC, evalstack, callstack, lvars, retPC, numargs, interruptroutine, currentframe, timerroutine, timer
    PC = 0
    callstack = []
    if zcode.header.zversion() != 6:
        currentframe = frame()
        currentframe.lvars = []
        currentframe.evalstack = []
    
    interruptroutine = 0
    timerroutine = 0
    timer = None

class frame:
    retPC = 0
    flags = 0
    varnum = 0
    numargs = 0
    evalstacksize = 0
    lvars = []
    evalstack = []
    interrupt = False

class undoframe:
    memory = []
    callstack = []
    currentframe = 0
    PC = 0

def save():
    f = io.openfile(zcode.screen.currentWindow, 'w')
    sd = quetzal.qdata()
    sd.release = zcode.header.release()
    sd.serial = zcode.header.serial()
    sd.checksum = zcode.header.getchecksum()
    sd.PC = PC
    sd.memory = zcode.memory.data[:zcode.header.statmembase()]
    sd.omemory = zcode.memory.originaldata[:zcode.header.statmembase()]
    sd.callstack = copy.deepcopy(callstack)
    sd.currentframe = copy.deepcopy(currentframe)
    return quetzal.save(f, sd)

def save_undo():
    undodata = undoframe()
    undodata.memory = zcode.memory.data[:]
    undodata.callstack = copy.deepcopy(callstack)
    undodata.currentframe = copy.deepcopy(currentframe)
    undodata.PC = PC
    undolist.append(undodata)
    return 1

def restore(filename=None, prompt=1):
    global PC, callstack, currentframe, interruptstack
    zcode.sounds.stopall()
    bis = interruptstack[:] 
    interruptstack = [] # clear the interrupt stack, or it may do weird things after the game is restored
    f = io.openfile(zcode.screen.currentWindow, 'r')
    sd = quetzal.qdata()
    sd.release = zcode.header.release()
    sd.serial = zcode.header.serial()
    sd.checksum = zcode.header.getchecksum()
    sd.omemory = zcode.memory.originaldata[:zcode.header.statmembase()]

    sd = quetzal.restore(f.read(), sd)
    if sd == False:
        interruptstack = bis[:] # if the restore failed, put the interrupt stack back how it was
        return 0

    zcode.memory.setarray(0, sd.memory)
    PC = sd.PC
    callstack = copy.deepcopy(sd.callstack)
    currentframe = copy.deepcopy(sd.currentframe)

    return 1


def restore_undo():
    global callstack, currentframe, PC
    if undolist == []:
        return 3
    undodata = undolist.pop()
    zcode.memory.data = undodata.memory[:]
    callstack = copy.deepcopy(undodata.callstack)
    currentframe = copy.deepcopy(undodata.currentframe)
    PC = undodata.PC
    return 2

def getvar(varnum, indirect=False):
    if varnum == 0:
        return getstack(indirect)
    elif varnum < 0x10:
        return getlocal(varnum - 1)
    else:
        return getglobal(varnum - 0x10)

def setvar(varnum, value, indirect=False): 
    if varnum == 0:
        putstack(value, indirect)
    elif varnum < 0x10:
        setlocal(varnum - 1, value)
    else:
        setglobal(varnum - 0x10, value)

def getstack(indirect=False):
    global currentframe
    try:
        if indirect == True:
            return currentframe.evalstack[-1]
        else:
            return currentframe.evalstack.pop()
    except:
        zcode.error.strictz("Tried to get a value from an empty stack.")
        return 0


def putstack(value, indirect=False):
    global currentframe
    value = zcode.numbers.unsigned(value)
    if indirect == True:
        currentframe.evalstack[-1] = value
    else:
        currentframe.evalstack.append(value)

def getlocal(varnum):
    global currentframe
    return currentframe.lvars[varnum]

def getglobal(varnum):
    table = zcode.header.globalsloc()
    return zcode.memory.getword(table + (varnum * 2))

def setlocal(varnum, value):
    global currentframe
    value = zcode.numbers.unsigned(value)
    currentframe.lvars[varnum] = value

def setglobal(varnum, value):
    value = zcode.numbers.unsigned(value)
    table = zcode.header.globalsloc()
    zcode.memory.setword(table + (varnum * 2), value)


def interrupt_call():
    global PC   
    if zcode.routines.quit:
        return None
    oldPC = PC
    if len(interruptstack) > 0 and not returning:# and currentframe.interrupt == False : # if there are calls on the interrupt stack ~~and we're not in an interrupt routine
        i = interruptstack.pop()
        if zcode.instructions.inputInstruction:
            PC = zcode.routines.oldpc
        address = i.routine
        call(address, [], 0, 1)
        zcode.routines.execloop()
        PC = oldPC


        
def call(address, args, useret, introutine=0, initial=0): # initial is for the initial routine call by z6 games
    global LARGEST_STACK
    global callstack
    global currentframe
    global PC
    if len(callstack) > LARGEST_STACK:
        LARGEST_STACK = len(callstack)



    if address == 0:
        if useret == 1:
            zcode.instructions.store(0)
    else:
        # okay, there is always a current frame (except for the initial call in z6 games)
        # the current frame holds the current lvars and the current evalstack
        # when a new routine is called, the current frame is merely shoved onto the call stack
        # then a new frame is created
        # the new frame is given a fresh evalstack and lvars
        # then the flag for whether a value should be returned is set, and the return variable is set
        # then the return PC is set
        # then the lvars are setup and the new PC is set
        try:
            if currentframe.interrupt:
                introutine = 1
        except:
            pass
        if initial == 0:
            newframe = frame()
            newframe.lvars = currentframe.lvars[:]
            newframe.flags = currentframe.flags
            newframe.retPC = currentframe.retPC
            newframe.varnum = currentframe.varnum
            newframe.numargs = currentframe.numargs
            newframe.evalstack = currentframe.evalstack[:]
            newframe.evalstacksize = len(currentframe.evalstack)
            newframe.interrupt = currentframe.interrupt
            callstack.append(newframe)


        currentframe = frame()
        currentframe.evalstack = []
        currentframe.lvars = []

        if useret == 0:
            currentframe.flags = (1 << 4)
            currentframe.varnum = 0
        else:
            retvar = zcode.memory.getbyte(PC)
            PC += 1
            currentframe.flags = 0
            currentframe.varnum = retvar
        currentframe.retPC = PC
        currentframe.numargs = len(args)
        currentframe.evalstacksize = 0
        if initial == 1:
            currentframe.retPC = 0
        if introutine:
            currentframe.interrupt = True

        # then we find out where the new routine is
        address = zcode.memory.unpackaddress(address, 1)
        # then we set up said routine
        PC = zcode.routines.setuproutine(address)
        currentframe.flags += len(currentframe.lvars)
        while len(args) > len(currentframe.lvars): # now we throw away any arguments that won't fit
            args.pop()

        for lvar, arg in enumerate(args): # overlay the local variables with the arguments
            setlocal(lvar, arg)
        
        if zcode.debug:
            print(' [', end='')
            for a in range(len(currentframe.lvars)):
                print(getlocal(a), end='')
                if a == len(currentframe.lvars) - 1:
                    print(']', end='')
                else:
                    print(', ', end='')

def ret(value):
    global PC
    global retPC
    global numargs
    global callstack
    global evalstack
    global lvars
    global interruptroutine
    global currentframe
    global timer
    global timervalue
    PC = currentframe.retPC
    varnum = currentframe.varnum
    if currentframe.flags & 16 == 16:
        useret = 0
    else:
        useret = 1
    currentframe = callstack.pop()
    if useret == 1:
        setvar(varnum, value)

    if timer and currentframe.interrupt == False:
        timer = False
        zcode.routines.timerreturn = True
        if value != 0:
            timervalue = True
            io.stoptimer()
        # all right, we need to check here if the program has printed anything
        # not sure how, but anyway, if the program has printed, we reprint the
        # input text so far. If the program has not printed, we do not reprint
        # the input text. Yay.
        if zcode.output.streams[1].interruptprinted:
            inp = [chr(a) for a in zcode.input.instring]
            inp = ''.join(inp)  
            inp = inp.lower()
            zcode.output.streams[1].write(inp)
            zcode.output.streams[1].interruptprinted = False
            zcode.screen.currentWindow.flushTextBuffer()


timervalue = False        
        
# user stacks

def pushuserstack(address, value):
    # I'm assuming that if the stack overflows, we don't branch, and don't push the value
    slots = zcode.memory.getword(address)
    if slots == 0:
        return 0
    else:
        zcode.memory.setword(address + (slots*2), value)
        zcode.memory.setword(address, slots - 1)
        return 1

def pulluserstack(address):
    slots = zcode.memory.getword(address)
    topvalue = slots + 1
    value = zcode.memory.getword(address + (topvalue * 2))
    slots += 1
    zcode.memory.setword(address, slots)
    return value

def popuserstack(address, items):
    slots = zcode.memory.getword(address)
    slots += items
    zcode.memory.setword(address, slots)


    
def firetimer():
    global timerreturned
    global timer

    zcode.screen.currentWindow.flushTextBuffer()
    zcode.screen.currentWindow.screen.update()
    timerreturned = 0
    timer = True
    i = interruptdata(INT_INPUT, timerroutine)
    interruptstack.append(i)
    interrupt_call()
    zcode.routines.timerreturn = False

