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

import zcode

import re


def importdict(address):
    numcodes = zcode.memory.getbyte(address)
    entrylength = zcode.memory.getbyte(address + numcodes + 1)
    numofentries = zcode.memory.getword(address + numcodes + 2)
    address += numcodes + 4
    entries = []
    for a in range(numofentries):
        offset = address + (a * entrylength)
        if zcode.header.zversion < 4:
            entries.append(list(zcode.memory.getarray(offset,4)))
        else:
            entries.append(list(zcode.memory.getarray(offset,6)))
    return entries

def getseperators(address):
    numcodes = zcode.memory.getbyte(address)
    seperators = [chr(a) for a in zcode.memory.getarray(address+1, numcodes)]
    return seperators


def splitinput(text, seperators):
    for count, value in enumerate(seperators):
        newvalue = value.center(3)
        text = text.replace(value, newvalue)
    text = text.split()
    return text

def findword(word, dictionary): # attempts to find a word in a dictionary, returning the address if found, or 0
    if dictionary == 0:
        dictionary = zcode.header.dictionaryloc
    dictlist = importdict(dictionary)
    numcodes = zcode.memory.getbyte(dictionary)
    entrylength = zcode.memory.getbyte(dictionary + numcodes + 1)
    if dictlist.count(zcode.text.encodetext(word)) != 0: # found the word
        return (dictlist.index(zcode.text.encodetext(word)) * entrylength) + dictionary + numcodes + 4
    else:
        return 0
        
def findstarts(textarray, seperators):
    if zcode.header.zversion < 5:
        offset = 1
    else:
        offset = 2
    s = '[' + ''.join(seperators) + ']| +'
    p = re.compile(s)
    
    
    wordstarts = []
    for count, value in enumerate(textarray):
        if (textarray[count-1]) == ' ' and (value != ' '): # if the previous character was a space and this one isn't
            wordstarts.append(count+offset) # this byte is the start of a new word

        elif seperators.count(value) != 0: # if the current character is a seperator
            wordstarts.append(count+offset)

        elif (count == 0) and (value != ' '): # if this is the first character, and it's not a space
            wordstarts.append(count+offset)

        elif seperators.count(textarray[count-1]) != 0: # if the *previous* character is a seperator
            wordstarts.append(count+offset)
    
    return wordstarts
            
def tokenise(intext, parseaddress=0, dictionary=0, flag=0):
    if zcode.header.zversion > 4 and parseaddress == 0:
        pass
    else:
        if dictionary == 0: # default dictionary
            dictionary = zcode.header.dictionaryloc
        seperators = getseperators(dictionary)
        words = splitinput(intext, seperators)
        maxparse = zcode.memory.getbyte(parseaddress)
        while len(words) > maxparse:
            words.pop()
        zcode.memory.setbyte(parseaddress + 1, len(words))
        address = parseaddress + 2
        starts = findstarts(intext, seperators)
        for count, value in enumerate(words):
            dictloc = findword(value, dictionary)
            if dictloc == 0 and flag == 1:
                pass
            else:
                zcode.memory.setword(address, dictloc)
                zcode.memory.setbyte(address + 2, len(value))
                zcode.memory.setbyte(address + 3, starts[count])
            address += 4
