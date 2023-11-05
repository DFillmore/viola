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

import string
import vio.zcode as io
import zcode
from zcode.constants import *

def setup(startstreams=[False, True, False, False, False]):
    global streams
    streams = [None, screenstream(), transcriptstream(), [], commandstream(), interpreterstream()]
    if startstreams[2]:
        streams[2].filename = startstreams[2]
    for stream, start in enumerate(startstreams):
        if start:
            streams[stream].open()





class outputstream:
    active = False
    quiet = False
    def open(self):
        self.active = True
    def close(self):
        self.active = False
    def write(self, data):
        if self.active and self.quiet == False:
            self.output(data)
    def output(self, data):
        pass

class screenstream(outputstream):
    active = True
    interruptprinted = False
    def output(self, data):
        if zcode.game.currentframe.interrupt:
            self.interruptprinted = True
        zcode.screen.printtext(data)

class transcriptstream(outputstream):
    filename = None

    def open(self):
        if self.filename == None:
            self.filename = writefile(b"", filename="TRANSCRIPT.LOG", prompt=True, append=False)
        self.active = True
        zcode.header.setflag(2,0,1)

    def output(self, data):
        data = data.replace('\r', '\n')
        if zcode.screen.currentWindow.testattribute(4):
            file = io.openfile(zcode.screen.currentWindow, 'a', self.filename)
            writefile(data.encode('utf-8'), filename=self.filename, prompt=False, append=True)

    def close(self):
        self.active = False
        zcode.header.setflag(2,0,0) # make sure the transcripting bit reflects the current state of transcription



class memorystream(outputstream):
    location = None
    width = None
    data = ""
    def open(self, location, width=None):
        global stream
        self.location = location
        self.width = width
        self.active = True
        self.data = []
        streams[1].quiet = True
        streams[2].quiet = True
        streams[4].quiet = True

    def close(self):
        global stream
        self.active = False
        streams[1].quiet = False
        streams[2].quiet = False
        streams[4].quiet = False
        if self.width == None:
            zcode.memory.setword(self.location, len(self.data))
            OFFSET = 2
        else:
            OFFSET = 0
        lines = []        
        if self.width != None: # formatted text for z6
            text = ''.join(self.data)
            while len(text) > 0:
                x = zcode.screen.currentWindow.fitText(text, self.width)
                if text[:x].find('\r') != -1:
                    x = text[:x].find('\r')
                line = (len(text[:x]), text[:x])
                lines.append(line)
                text = text[line[0]:]
        if zcode.header.zversion() == 6:
            zcode.header.settextwidth(zcode.screen.currentWindow.getFont().getStringLength(''.join(self.data)))

        c = 0
        data = []
        if self.width == None:
            for a in self.data: # make absolutely certain each value in data fits in a byte
                b = ord(a)
                d = []
                while b > 255:
                    d.append(b&255)
                    b = b >> 8
                data.append(b)
                d.reverse()
                for b in d:
                    data.append(b)


        else:
            for l in lines:
                linelength = l[0]
                line = l[1]
                data.append((linelength >> 8) & 0xff)
                data.append(linelength & 0xff)
                for c in line:
                    data.append(ord(c))
  
        for count, value in enumerate(data):
            zcode.memory.setbyte(self.location+OFFSET+count, value)

        if self.width != None: # if a width operand was passed to output stream 3, we need to add a 0 word on the end of the text
            zcode.memory.setword(self.location+len(data), 0)
        self.data = []

    def output(self, data):
        data = zcode.text.unicodetozscii(data)
        self.data += data

class commandstream(outputstream):
    filename = None

    def open(self):
        if self.filename == None:
            self.filename = writefile(b"", filename="COMMANDS.REC", prompt=True, append=False)
        self.active = True

    def output(self, data):
        file = io.openfile(zcode.screen.currentWindow, 'a', self.filename)
        writefile(data.encode('utf-8'), filename=self.filename, prompt=False, append=True)

class istreamdata():
    data = []


class gibberize(istreamdata):
    ident = 'GIBBERIZE:'
    def processdata(self, data):
        c = data.index(':')
        data = data[c+1:]
        t = ''.join(data).replace('S', '5').replace('A', '4').replace('E', '3').replace('I', '1').replace('O', '0')
        streams[5].outputdata = t




istreamidents = {'GIBBERIZE:': gibberize()}



class interpreterstream(outputstream):
    data = []
    tempdata = []
    location = None
    outputdata = []
    def open(self, location):
        self.tempdata = []
        self.active = True
        self.location = location

    def output(self, data):
        self.tempdata.extend(data)

    def close(self):
        self.active = False
        # here we should actually process the data
        # first, search the tempdata stream for a :
        c = self.tempdata.index(':')
       
        # then, use all data up to and including the : as an identifier string
        identdata = self.tempdata[:c+1]
        ident = ''.join(identdata)
        # check the identifier string against istreamidents dictionary, to see if we recognize it
        if ident not in istreamidents:
            # if we don't, do nothing, throw the tempdata away
            self.tempdata = []
        else:
            # if we do, send the tempdata to the class object for the ident type, and let that deal with what to do next
            istreamidents[ident].processdata(self.tempdata) # this should set up the output data for us if it needs to
            self.tempdata = []
        
        # check to see if there's any output data to write back to the game memory
        if len(self.outputdata) > 0 and self.location:
            tablelen = zcode.memory.getword(self.location)
            l = self.location + 2
            d = list(self.outputdata[:])
            z = 0
            d2 = []
            for a in d: # make absolutely certain each value in data fits in a byte
                z += 1
                try:
                    b = ord(a)
                except:
                    pass
                while b > 255:
                    d2.append(b&255)
                    b = b >> 8
                d2.append(b)
            d = d2[:tablelen] # lose any data that will not fit (we should have checked before this to make sure this won't happen, though)
            zcode.memory.setarray(self.location+2, d)
        self.outputdata = []


def checkident(address):
    i = []
    a = address
    lastchar = None
    while lastchar != ':':
        i.append(chr(zcode.memory.getbyte(a)))
        lastchar = i[-1]
        a += 1
    ident = ''.join(i)
    if ident in istreamidents:
        return 1
    else:
        return 0


    



def numopenstreams(stream):
    if stream == 3: # should probably have a better check to see if this is a list or an instance
        return len(streams[3])
    else:
        try:
            if streams[stream].active:
                return 1
            return 0
        except:
            return 0

        

def openstream(stream, location=None, width=None): # area is only used for stream 3, width only for z6 stream 3
    global streams
    if stream == 3:
        if zcode.use_standard <= STANDARD_02:
            if len(streams[3]) == 0:
                m = memorystream()
                streams[3].append(m)
            try:
                streams[3][0].close()
            except:
                pass
            streams[3][0].open(location, width)
        else:
            if len(streams[3]) < 16:
                m = memorystream()
                m.open(location, width)
                streams[3].append(m)
            else:
                zcode.error.fatal('Tried to open too many memory streams.')
    else:
        try:
            streams[stream].open()
        except:
            zcode.error.strictz("Tried to open stream ' + str(stream) + ', which doesn't exist")


def closestream(stream):
    global streams
    if stream != 3:
        streams[stream].close()
    else:
        if zcode.use_standard <= STANDARD_02:
            try:
                streams[3][0].close()
            except:
                pass
        else:
            m = streams[3].pop()
            m.close()
        
def printtext(text, special=False, error=False): # All text to be printed anywhere should be printed here. It will then be sorted out.
    if error:
        if not io.error(text): # if the io module doesn't have a special case for printing errors, print them to the screen normally
            streams[1].write(text)
    else:
        streams[1].write(text)
    if len(streams[3]) > 0 and not error:
        streams[3][-1].write(text)
    text = text.replace('\r', '\n')
    streams[2].write(text)
    if special and not error:
        streams[4].write(text)



    
def writefile(data, filename=None, prompt=False, append=False):
    """Opens a file, writes data to it, and returns the filename"""
    if append:
        f = io.openfile(zcode.screen.currentWindow, 'a', filename, prompt)
    else:
        f = io.openfile(zcode.screen.currentWindow, 'w', filename, prompt)
    f.write(data)
    filename = f.name
    f.close()
    return filename

            
        
        
