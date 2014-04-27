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

import string

import zcode


def importdict(address):
    numcodes = zcode.memory.getbyte(address)
    entrylength = zcode.memory.getbyte(address + numcodes + 1)
    numofentries = zcode.memory.getword(address + numcodes + 2)
    address += numcodes + 4
    entries = []
    for a in range(numofentries):
        offset = address + (a * entrylength)
        if zcode.header.zversion() < 4:
            entries.append(list(zcode.memory.getarray(offset,4)))
        else:
            entries.append(list(zcode.memory.getarray(offset,6)))
    return entries

def getseperators(address):
    seperators = []
    numcodes = zcode.memory.getbyte(address)
    for a in range(numcodes):
        seperators.append(chr(zcode.memory.getbyte(address+a+1)))
    return seperators


def splitinput(text, seperators):
    for a in range(len(seperators)):
        x = seperators[a]
        x2 = x.center(3)
        text = text.replace(x, x2)
    text = text.split()
    return text

def findword(word, dictionary): # attempts to find a word in a dictionary, returning the address if found, or 0
    if dictionary == 0:
        dictionary = zcode.header.dictionaryloc()
    dictlist = importdict(dictionary)
    numcodes = zcode.memory.getbyte(dictionary)
    entrylength = zcode.memory.getbyte(dictionary + numcodes + 1)
    if dictlist.count(zcode.text.encodetext(word)) != 0: # found the word
        return (dictlist.index(zcode.text.encodetext(word)) * entrylength) + dictionary + numcodes + 4
    else:
        return 0
        
def findstarts(textarray, seperators): # this is old code from old viola, and it actually works! AMAZING!
    x = []
    newword = 0
    inword = 0
    for a in range(len(textarray)):
        if (textarray[a-1] == ' ') and (textarray[a] != ' '): # if the previous byte was a space and this one isn't
            newword = 1 # this byte is the start of a new word
        elif seperators.count(textarray[a]) != 0: # otherwise, if this byte is a seperator
            newword = 1 # this byte is the start of a new word
        elif (a == 0) and (textarray[a] != ' '): # otherwise, if this is the first byte, and it's not a space
            newword = 1 # this byte is the start of a new word
        elif seperators.count(textarray[a-1]) != 0: # othewise, if the *previous* byte is a seperator
            newword = 1
        else: # otherwise
            newword = 0 # this byte is NOT the start of a new word
        if newword == 1: # if this byte is the start of a new word
            x.append(a) # write the position of this byte into the list

    for a in range(len(x)):
        if zcode.header.zversion() < 5:
            x[a] += 1
        else:
            x[a] += 2
    return x
            
def tokenise(intext, parseaddress=0, dictionary=0, flag=0): # this should work, I think
    if zcode.header.zversion() > 4 and parseaddress == 0:
        pass
    else:
        if dictionary == 0: # default dictionary
            dictionary = zcode.header.dictionaryloc()
        seperators = getseperators(dictionary)
        words = splitinput(intext, seperators)
        maxparse = zcode.memory.getbyte(parseaddress)
        while len(words) > maxparse:
            words.pop()
        zcode.memory.setbyte(parseaddress + 1, len(words))
        address = parseaddress + 2
        starts = findstarts(intext, seperators)
        for a in range(len(words)):
            dictloc = findword(words[a], dictionary)
            if dictloc == 0 and flag == 1:
                pass
            else:
                zcode.memory.setword(address, dictloc)
                zcode.memory.setbyte(address + 2, len(words[a]))
                zcode.memory.setbyte(address + 3, starts[a])
            address += 4
