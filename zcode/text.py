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

import zcode
from zcode.constants import *
import settings


ibm_graphics_chars = {191:0x2510, 192:0x2514, 217:0x2518, 218:0x250C, 196:0x2500, 179:0x2502, 24:0x2191, 25:0x2193}
appleiic_mousetext_chars = {95:0x258f, 90:0x2595, 76:0x2594,  75:0x2191, 74:0x2193}


def setup():
    setupunitable()
    setupreverseunitable()
    setupalphatable()
    if settings.code in beyond_zork_codes:
        if zcode.header.getterpnum() == 9 or zcode.header.getterpnum() == 6 and not zcode.header.getflag(2, 3):
            zcode.screen.specialfont3()

addrwibble = 0
A0 = '      abcdefghijklmnopqrstuvwxyz'
A1 = '      ABCDEFGHIJKLMNOPQRSTUVWXYZ'
A2 = '       \r0123456789.,!?_#\'"/\\-:()'

unitable = { 155: 0xe4,
             156: 0xf6,
             157: 0xfc,
             158: 0xc4,
             159: 0xd6,
             160: 0xdc,
             161: 0xdf,
             162: 0xbb,
             163: 0xab,
             164: 0xeb,
             165: 0xef,
             166: 0xff,
             167: 0xcb,
             168: 0xcf,
             169: 0xe1,
             170: 0xe9,
             171: 0xed,
             172: 0xf3,
             173: 0xfa,
             174: 0xfd,
             175: 0xc1,
             176: 0xc9,
             177: 0xcd,
             178: 0xd3,
             179: 0xda,
             180: 0xdd,
             181: 0xe0,
             182: 0xe8,
             183: 0xec,
             184: 0xf2,
             185: 0xf9,
             186: 0xc0,
             187: 0xc8,
             188: 0xcc,
             189: 0xd2,
             190: 0xd9,
             191: 0xe2,
             192: 0xea,
             193: 0xee,
             194: 0xf4,
             195: 0xfb,
             196: 0xc2,
             197: 0xca,
             198: 0xce,
             199: 0xd4,
             200: 0xdb,
             201: 0xe5,
             202: 0xc5,
             203: 0xf8,
             204: 0xd8,
             205: 0xe3,
             206: 0xf1,
             207: 0xf5,
             208: 0xc3,
             209: 0xd1,
             210: 0xd5,
             211: 0xe6,
             212: 0xc6,
             213: 0xe7,
             214: 0xc7,
             215: 0xfe,
             216: 0xf0,
             217: 0xde,
             218: 0xd0,
             219: 0xa3,
             220: 0x153,
             221: 0x152,
             222: 0xa1,
             223: 0xbf
           }

outputvalues = [0, 9, 11, 13]
outputvalues.extend(list(range(32, 127)))
#outputvalues.extend(list(range(129, 133)))
#outputvalues.extend(list(range(133, 145)))
#outputvalues.extend(list(range(145, 155)))
outputvalues.extend(list(range(155, 252)))

inputvalues = [8, 13, 27]
inputvalues.extend(list(range(32, 127)))
inputvalues.extend(list(range(129, 133)))
inputvalues.extend(list(range(133, 145)))
inputvalues.extend(list(range(145, 155)))
inputvalues.extend(list(range(155, 252)))
inputvalues.extend(list(range(252, 255)))

def setupunitable():
    global unitable
    if zcode.use_standard >= STANDARD_10:
        if zcode.header.zversion() > 4:
            loc = zcode.header.unicodetableloc()
            if loc != 0:
                size = zcode.memory.getbyte(loc)
                loc += 1
                for a in range(size):
                    unitable[155+a] = zcode.memory.getword(loc+(a*2))
    elif zcode.use_standard == STANDARD_00:
        unitable = { 155: 0xe4,
                     156: 0xf6,
                     157: 0xfc,
                     158: 0xc4,
                     159: 0xd6,
                     160: 0xdc,
                     161: 0xdf,
                     162: 0xbb,
                     163: 0xab,
                   }


def setupreverseunitable():
    global reverseunitable
    reverseunitable = {}
    for key in list(unitable.keys()):
        val = unitable[key]
        reverseunitable[val] = key
                

def setupalphatable():
    global A0, A1, A2
    if zcode.header.zversion() == 1:
        A2 = '       0123456789.,!?_#\'"/\\<-:()'
    if (zcode.header.zversion() >= 5) and (zcode.header.alphatableloc() != 0):
        temp = []
        loc = zcode.header.alphatableloc()
        for x in range(6):
            temp.append(' ')
        for x in range(26):
            temp.append(chr(zcode.memory.getbyte(loc+x)))
        A0 = ''.join(temp)
        loc = loc + x + 1
        temp = []
        for x in range(6):
            temp.append(' ')
        for x in range(26):
            temp.append(chr(zcode.memory.getbyte(loc+x)))
        A1 = ''.join(temp)
        loc = loc + x + 1
        temp = []
        for x in range(6):
            temp.append(' ')
        for x in range(26):
            temp.append(chr(zcode.memory.getbyte(loc+x)))
        temp[7] = '\r'
        A2 = ''.join(temp)






def splitwords(word):
    chars = (word >> 10 & 31, word >> 5 & 31, word & 31)
    return chars

def gettextlength(address): # this determines how much space an encoded string takes up
    loc = address
    endbit = 0
    a = 1
    while endbit == 0:
        word = zcode.memory.getword(loc)
        if word & 0x8000:
            endbit = 1
        loc += 2
        a += 1
        
    return loc - address


def convertBZorkCode(code):
    if zcode.screen.currentWindow.getFontNumber() == 3 and zcode.header.getterpnum() == 9: # apple iic
        try:
            return appleiic_mousetext_chars[code]
        except:
            return code
    elif zcode.header.getterpnum() == 6 and not zcode.header.getflag(2, 3): # ibm pc, and graphics not available
        try:
            return ibm_graphics_chars[code]
        except:
            return code
    return code

def getZSCIIchar(code):
    if settings.code in beyond_zork_codes:
        newcode = convertBZorkCode(code)
        if newcode != code:
            return chr(newcode)
        
    if code == 0:
        return ''
    if code == 1 and zcode.header.zversion() == 1:
        return '\r'
    elif code == 9:
        return '\t'
    elif code == 11 and zcode.header.zversion() == 6: # sentence space. (needs to be smaller when using fixed pitch)
        return '  '
    elif code == 13:
        return '\r'
    elif code > 31 and code < 127:
        return chr(code)
    elif code >= 155 and code <= 251: # extra chars
        try:
            char = unitable[code]
            char = chr(char)
        except:
            zcode.error.warning(f'ZSCII character {code} undefined for output.')
            return ''

        return char
    else:
        zcode.error.warning(f'ZSCII character {code} undefined for output.')
        return ''
    
def printabbrev(table, code):
    address = zcode.header.abbrevtableloc()
    loc = 32 * (table-1) + code
    infoaddress = address + (loc * 2)
    wordaddress = zcode.memory.getword(infoaddress)
    textaddress = zcode.memory.wordaddress(wordaddress)
    chars = zcharstozscii(textaddress)
    return chars




def zcharstozscii(address):
    global A0, A1, A2
    codes = []
    loc = address
    finished = False
    while not finished:
        w = zcode.memory.getword(loc)
        c = splitwords(w)
        if w & 0x8000 == 0x8000:
            finished = True
                
        for a in c:
            codes.append(a)
                    
        loc += 2

 
    # codes should now be a list of the z-characters, with Unicode string bytes
    # Need to convert this to ZSCII (and Unicode strings bytes)
    ZSCII = []
    twocode = 0
    abbrev = 0

    temporary = False
    currentalpha = A0
    previousalpha = A0

    for a in codes:
        if abbrev != 0:
            ZSCII.extend(printabbrev(abbrev, a))
            abbrev = 0
        elif twocode == 1: # first 5 bits of a 10-byte zscii code
            ZSCII.append(a << 5)
            twocode = 2
        elif twocode == 2: # last 5 bits of a 10-byte zscii code
            ZSCII[-1] = chr(ZSCII[-1] + a)
            twocode = 0
        elif a < 4 and a > 0 and zcode.header.zversion() >= 3:
            abbrev = a
        elif a == 1 and zcode.header.zversion() == 2:
            abbrev = a
        elif a == 4 and zcode.header.zversion() >= 3:
            previousalpha = currentalpha
            currentalpha = A1
            temporary = True
        elif a == 5 and zcode.header.zversion() >= 3:
            previousalpha = currentalpha
            currentalpha = A2
            temporary = True
        elif (a == 2 or a == 4) and zcode.header.zversion() < 3:
            previousalpha = currentalpha
            if currentalpha == A0:
                currentalpha = A1
            elif currentalpha == A1:
                currentalpha = A2
            elif currentalpha == A2:
                currentalpha = A0
            if a == 2:
                temporary = True
        elif (a == 3 or a == 5) and zcode.header.zversion() < 3:
            previousalpha = currentalpha
            if currentalpha == A0:
                currentalpha = A2
            elif currentalpha == A1:
                currentalpha = A0
            elif currentalpha == A2:
                currentalpha = A1
            if a == 3:
                temporary = True
        
        elif currentalpha == A2 and a == 6: # start a ten-byte zscii code
            twocode = 1
            if temporary == True:
                currentalpha = previousalpha
                temporary = False
        elif a == 1 and zcode.header.zversion() == 1:
            ZSCII.append('\r')
        else:
            ZSCII.append(currentalpha[a])
            if temporary == True:
                currentalpha = previousalpha
                temporary = False
    return ZSCII

def zsciitounicode(zscii):
    text = []
    unitext = []
    for a in zscii:
        text.append(getZSCIIchar(ord(a)).encode('utf-8'))
    return b''.join(text)
            
    


def decodetext(address, antirecurse=0):
    z = zcharstozscii(address)
    u = zsciitounicode(z)
    return u.decode('utf-8')




def unicodetozscii(text):
    # needs to turn characters into '?' if we can't encode them
    w = []
    for a in text:
        if ord(a) in list(reverseunitable.keys()):
            w.append(chr(reverseunitable[ord(a)]))
        else:
            if ord(a) not in outputvalues:
                w.append('?')
            else:
                w.append(a)
    return ''.join(w)

def zsciitozchars(text, maxlen=-1):
    encoded = []
    for a in text:
        if A0.find(a) != -1:
            encoded.append(A0.find(a))
        elif A1.find(a) != -1:
            encoded.append(4)
            encoded.append(A1.find(a))
        elif A2.find(a) != -1:
            encoded.append(5)
            encoded.append(A2.find(a))
        else: # The letter is not in any of the three alphabets
            encoded.append(5)
            encoded.append(6)
            if ord(a) in outputvalues:
                encoded.append(ord(a) >> 5)
                encoded.append(ord(a) & 0x1f)

    if maxlen != -1:
        while len(encoded) > maxlen:
            encoded.pop()
        while len(encoded) < maxlen:
            encoded.append(5)

    words = []
    words.append((encoded[0] << 10) + (encoded[1] << 5) + encoded[2])
    words.append((encoded[3] << 10) + (encoded[4] << 5) + encoded[5])
    if zcode.header.zversion() > 3:
        words.append((encoded[6] << 10) + (encoded[7] << 5) + encoded[8])
    words[-1] = words[-1] | 0x8000
    chars = []
    for a in words:
        chars.append(a >> 8)
        chars.append(a & 0xff)
    return chars


def encodetext(word): # encodes words for matching against the dictionary
    word = unicodetozscii(word)
    if zcode.header.zversion() < 4:
        maxlen = 6
    else:
        maxlen = 9
    chars = zsciitozchars(word, maxlen)
    return chars
