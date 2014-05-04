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

import iff
import os
import zio as io


            
class umemchunk(iff.chunk):
    ID = 'UMem'
    data = []
    def write(self, data):
        self.data = data[:]

    def read(self):
        return self.data[:]


class cmemchunk(iff.chunk):
    ID = 'CMem'
    data = []
    def write(self, data, odata):
        #mem = []
        commem = []
        mem = [data[a] ^ odata[a] for a in range(len(data))]

        while mem[-1] == 0:
            mem.pop()
        zerorun = 0
        for a in range(len(mem)):
            if zerorun == 0:
                commem.append(mem[a])
            else:
                if mem[a] == 0:
                    zerorun += 1
                else:
                    commem.append(zerorun - 1)
                    commem.append(mem[a])
                    zerorun = 0
                if zerorun == 256:
                    commem.append(zerorun - 2)
                    commem.append(mem[a])
                    zerorun = 0
            if (mem[a] == 0) and (zerorun == 0):
                zerorun = 1
        self.data = commem[:]

    def read(self, odata):
        commem = self.data[:]
        obmem = []
        zerorun = False
        for a in range(len(commem)): # loop over commpressed memory
            if zerorun == True:
                runlength = commem[a]
                for b in range(runlength):
                    obmem.append(0)
                zerorun = False
            elif commem[a] == 0:
                obmem.append(commem[a])
                zerorun = True
            else:
                obmem.append(commem[a])
        while len(obmem) < len(odata):
            obmem.append(0)
        mem = []
        
        mem = [obmem[a] ^ odata[a] for a in range(len(obmem))]
        return mem

            
class stkschunk(iff.chunk):
    ID = 'Stks'
    data = []
    def write(self, callstack, currentframe):
        global zstack
        for a in range(len(callstack)):
            self.data.append((callstack[a].retPC >> 16) & 0xff)
            self.data.append((callstack[a].retPC >> 8) & 0xff)
            self.data.append(callstack[a].retPC & 0xff)
            self.data.append(callstack[a].flags)
            self.data.append(callstack[a].varnum)
            args = 1
            for b in range(callstack[a].numargs):
                args *= 2
            args -= 1
            self.data.append(args)
            self.data.append((callstack[a].evalstacksize >> 8) & 0xff)
            self.data.append(callstack[a].evalstacksize & 0xff)

            for x in range(len(callstack[a].lvars)):
                self.data.append((callstack[a].lvars[x] >> 8) & 255)
                self.data.append(callstack[a].lvars[x] & 255)
            
            for x in range(callstack[a].evalstacksize):
                self.data.append((callstack[a].evalstack[x] >> 8) & 255)
                self.data.append(callstack[a].evalstack[x] & 255)
        self.data.append((currentframe.retPC >> 16) & 0xff)
        self.data.append((currentframe.retPC >> 8) & 0xff)
        self.data.append(currentframe.retPC & 0xff)
        self.data.append(currentframe.flags)
        self.data.append(currentframe.varnum)
        args = 1
        for a in range(currentframe.numargs):
            args *= 2
        args -= 1
        self.data.append(args)
        self.data.append((len(currentframe.evalstack) >> 8) & 0xff)
        self.data.append(len(currentframe.evalstack) & 0xff)
        for x in range(len(currentframe.lvars)):
            self.data.append((currentframe.lvars[x] >> 8) & 255)
            self.data.append(currentframe.lvars[x] & 255)
            
        for x in range(currentframe.evalstacksize):
            self.data.append((currentframe.evalstack[x] >> 8) & 255)
            self.data.append(currentframe.evalstack[x] & 255)

    def read(self):
        # what we should do here is to read each frame back into a stack object
        # but, obviously, not *the* stack object, just in case something goes wrong.
        callstack = []
        place = 0
        while place < len(self.data):
            callstack.append(frame())
            callstack[-1].lvars = []
            callstack[-1].evalstack = []
            callstack[-1].retPC = (self.data[place] << 16) + (self.data[place+1] << 8) + self.data[place+2]
            callstack[-1].flags = self.data[place+3]
            numvars = self.data[place+3] & 15
            callstack[-1].varnum = self.data[place+4]
            done = 1
            x = 0
            args = self.data[place+5]
            while done != 0:
                x += 1
                done = args & 1
                args = args >> 1
            args -= 1
            callstack[-1].numargs = args
 
            callstack[-1].evalstacksize = (self.data[place+6] << 8) + self.data[place+7]
            
            place += 8
            for x in range(numvars): 
                
                callstack[-1].lvars.append((self.data[place] << 8) + self.data[place+1])
                place += 2
            
            for x in range(callstack[-1].evalstacksize):
                
                callstack[-1].evalstack.append((self.data[place] << 8) + self.data[place+1])
                place += 2
        return callstack
        
        


class ifhdchunk(iff.chunk):
    ID = 'IFhd'
    length = 13
    rnumber = 0
    snumber = 0
    checksum = 0
    PC = 0
    data = []
    def write(self, release, serial, checksum, PC):
        self.data.append(release >> 8) # release number
        self.data.append(release & 255)

        for a in serial:
            self.data.append(ord(a))

        self.data.append(checksum >> 8)
        self.data.append(checksum & 255)

        self.data.append(PC >> 16)  # Initial PC
        self.data.append(PC >> 8)
        self.data.append(PC & 255)


    def read(self, release, serial):
        if ((self.data[0] << 8) + self.data[1]) != memory.getword(0x2): # if the release number is wrong, fail
            return -1
        for a in range(6):
            if self.data[a+2] != memory.getbyte(a+0x12): # if the serial number is wrong, fail
                return -1
        PC = (self.data[10] << 16) + (self.data[11] << 8) + self.data[12] 
        return PC

class intdchunk(iff.chunk):
    ID = 'IntD'
    osID = '    '
    flags = 0
    contID = 0
    reserved = 0
    terpID = '    '
    xdata = 0
    data = []

class formchunk(iff.chunk):
    ID = 'FORM'
    subID = 'IFZS'
    data = []

    release = 0
    serial = '      '
    checksum = 0
    memory = []
    omemory = []
    callstack = []
    currentframe = None
    
    def write(self, release, serial, checksum, PC, memory, omemory, callstack, currentframe):
        self.data.append(ord('I')) 
        self.data.append(ord('F'))
        self.data.append(ord('Z'))
        self.data.append(ord('S'))
        c1 = ifhdchunk()
        c2 = umemchunk()
        c3 = stkschunk()
        c1.write(release, serial, checksum, PC)
        c2.write(memory)
        c3.write(callstack, currentframe)
        id = cchunk.writeID() # set id to current chunk's ID
        for b in range(len(id)):
            self.data.append(ord(id[b])) # write current chunk's ID to data
        clen = cchunk.writelen() # write current
            
        for b in range(len(clen)):
            self.data.append(clen[b])
        for b in range(len(cchunk.data)):
            self.data.append(cchunk.data[b])

    def read(self):
        # okay, first, we need to check if this is an IFZS file
        if chr(self.data[0]) != 'I' or chr(self.data[1]) != 'F' or chr(self.data[2]) != 'Z' or chr(self.data[3]) != 'S':
            return -1
        
        data = self.data[4:]
        while len(data) > 0:
            cchunk = iff.chunk()
            cchunk.data = data
            clen = cchunk.readlen()
            id = cchunk.readID()
            
            if id == 'CMem':
                cchunk = cmemchunk()
                
            elif id == 'UMem':
                cchunk = umemchunk()
                
            elif id == 'Stks':
                cchunk = stkschunk()
                
            elif id == 'IFhd':
                cchunk = ifhdchunk()
            else:
                cchunk = iff.chunk()

            cchunk.data = data[8:clen+8]
            if clen % 2 == 1:
                data = data[clen+9:]
            else:
                data = data[clen+8:]
            
            if cchunk.read() == -1:
                return -1



def save(sfile):
    data = []
    cchunk = formchunk() # cchunk is a form chunk
    cchunk.dowrite() # fill cchunk.data with data
    id = cchunk.writeID() # find cchunk's id
    for b in range(len(id)):
        data.append(ord(id[b])) # write ID to data
    clen = cchunk.writelen() # find cchunk's length
    for b in range(len(clen)):
        data.append(clen[b]) # write length to data
    for b in range(len(cchunk.data)):
        data.append(cchunk.data[b]) # write cchunk's data to data
    for a in range(len(data)):
        sfile.write(chr(data[a])) # write data to file
    sfile.close() # close file
    condition = True
    return condition

def restore():
    rd = openfile
    if rd.ShowModal() == io.pygame.ID_OK: # if the user clicks on OK
        rname = rd.GetPath() # get the name of the save file to restore from
        rd.Destroy()
        rfile=open(rname, 'rb')
        data = formchunk()
        filelen = os.path.getsize(rfile.name)
        rfile.seek(8)
        for a in range(filelen-8):
            data.data.append(ord(rfile.read(1)))
        if data.read() == -1:
            return 0
        else:
            # Right, everything's apparently gone correctly, so now we take the values we've extracted
            # from the save file and shove them into the real thing
            for a in range(len(mem)):
                memory.data[a] = mem[a]
            game.PC = PC
            # with any luck, the top frame of the callstack should just slot nicely into the game.currentframe global
            game.currentframe = callstack.pop()
            game.callstack = callstack
            
            return 1
    else:
        return 0


class Quetzal:
    def __init__(self, frameclass, omem): # frameclass is the class used by the VM for stack frames. omem is a list of the game's original memory
        self.frameclass = frameclass
        self.omem = omem

    def save(self, path):
        pass