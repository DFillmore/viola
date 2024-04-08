# Copyright (C) 2001 - 2024 David Fillmore
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

class chunk:
    ID = '    '
    subID = '    '
    length = 0
    data = []

    def dowrite(self, input=0):
        if input != 0:
            self.input = input
        self.write()
        self.length = len(self.data)
        if self.length % 2 == 1:
            self.data.append(0)

    def writeID(self):
        return list(self.ID)

    def writelen(self):
        clen = []
        clen.append((self.length >> 24) & 0xff)
        clen.append((self.length >> 16) & 0xff)
        clen.append((self.length >> 8) & 0xff)
        clen.append(self.length & 0xff)
        return clen

    def readID(self):
        id = []
        for a in range(4):
            id.append(chr(self.data[a]))
        id2 = ''.join(id)
        return id2

    def readlen(self):
        string = self.data
        len = (((((string[4] << 8) + string[5]) << 8) + string[6]) << 8) + string[7]
        return len

    def fbnum(self, string):
        num = (((((ord(string[0]) << 8) + ord(string[1])) << 8) + ord(string[2])) << 8) + ord(string[3])
        return num

    def doread(self, data):
        len = self.readlen(data)
        self.data = []
        for a in range(len):
            self.data.append(data[a])
        self.read()

    def read(self):
        pass

    def write(self):
        pass


class authchunk(chunk):
    ID = 'AUTH'


class annochunk(chunk):
    ID = 'ANNO'


class copychunk(chunk):
    ID = '(c) '


class formchunk(chunk):
    ID = 'FORM'
    data = []
    wchunks = []

    def write(self):
        self.data.append(ord(self.subID[0]))
        self.data.append(ord(self.subID[1]))
        self.data.append(ord(self.subID[2]))
        self.data.append(ord(self.subID[3]))
        chunks = self.wchunks  # chunks to write
        for a in chunks:
            cchunk = a()  # set cchunk to current chunk
            cchunk.dowrite(self.input)  # write current chunk's data
            id = cchunk.writeID()  # set id to current chunk's ID
            for b in range(len(id)):
                self.data.append(ord(id[b]))  # write current chunk's ID to data
            clen = cchunk.writelen()  # write current

            for b in clen:
                self.data.append(b)
            for b in cchunk.data:
                self.data.append(b)

    def read(self):
        place = 0
        datachunk = self.data[8:len(self.data)]
        while place < len(self.data):
            clen = self.readlen(datachunk)
            id = self.readID(datachunk)
            datachunk = datachunk[place + 8:clen]
            try:
                cchunk = self.chunks[id]()
            except:
                cchunk = chunk()
            cchunk.read(datachunk)
            place += clen
            if clen % 2 == 1:
                place += 1
