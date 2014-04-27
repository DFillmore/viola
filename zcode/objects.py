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

import sys


import zcode


def setup():
    global propdef
    global objstart 
    propdef = zcode.header.objtableloc()
    if zcode.header.zversion() < 4:
        objstart = propdef + 62
    else:
        objstart = propdef + 126

def getdefault(propnum):
    address = ((propnum - 1) * 2) + propdef
    return zcode.memory.getword(address)

def findobject(obj): # returns the address in memory of the object numbered obj
    if zcode.header.zversion() < 4:
        address = objstart + (9 * obj) - 9
    else:
        address = objstart + (14 * obj) - 14
    return address

def getparent(obj): # returns the number of the parent of the object with number obj
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        return zcode.memory.getbyte(address + 4)
    else:
        return zcode.memory.getword(address + 6)
        
def getsibling(obj): # returns the number of the sibling of the object with number obj
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        return zcode.memory.getbyte(address + 5)
    else:
        return zcode.memory.getword(address + 8)

def getchild(obj): # return the number of the child of the object with number obj
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        return zcode.memory.getbyte(address + 6)
    else:
        return zcode.memory.getword(address + 10)

def geteldersibling(obj): # returns the number of the object to which this object is the sibling
    parent = getparent(obj)
    if parent == 0: # there is no parent, so there is no elder sibling (hopefully)
        return 0 
    eldestchild = getchild(parent)
    if eldestchild == obj: # there is no elder sibling
        return 0
    sibling = getsibling(eldestchild)
    eldersibling = eldestchild
    while sibling != obj:
        eldersibling = getsibling(eldersibling)
        sibling = getsibling(eldersibling)
    return eldersibling

def setparent(obj, parent): # sets obj's parent to parent
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        zcode.memory.setbyte(address + 4, parent)
    else:
        zcode.memory.setword(address + 6, parent)

def setsibling(obj, sibling): # sets obj's sibling to sibling
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        zcode.memory.setbyte(address + 5, sibling)
    else:
        zcode.memory.setword(address + 8, sibling)

def setchild(obj, child): # sets obj's child to child
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        zcode.memory.setbyte(address + 6, child)
    else:
        zcode.memory.setword(address + 10, child)

def getpropertiesaddress(obj): # returns the address of the properties table for the object numbered obj
    address = findobject(obj)
    if zcode.header.zversion() < 4:
        return zcode.memory.getword(address + 7)
    else:
        return zcode.memory.getword(address + 12)

def setattr(obj, attr): # sets attribute number attr in object number obj
    address = findobject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address+2)
        shift = attr - 16
    elif attr < 48 and zcode.header.zversion() > 3:
        flags = zcode.memory.getword(address+4)
        shift = attr - 32
    else: # this is an error condition
        zcode.error.strictz('Tried to set attribute ' + str(attr))
        return None
    flagset = (0x8000 >> shift)
    flags = flags | flagset
    if attr < 16:
        zcode.memory.setbyte(address, (flags >> 8) & 255)
        zcode.memory.setbyte(address+1, flags & 255)
    elif attr < 32:
        zcode.memory.setbyte(address+2, (flags >> 8) & 255)
        zcode.memory.setbyte(address+3, flags & 255)
    elif attr < 48:
        zcode.memory.setword(address+4, flags)

def clearattr(obj, attr): # clears attribute number attr in object number obj
    address = findobject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address+2)
        shift = attr - 16
    elif attr < 48 and zcode.header.zversion() > 3:
        flags = zcode.memory.getword(address+4)
        shift = attr - 32
    else: # this is an error condition
        zcode.error.strictz('Tried to clear attribute ' + str(attr))
        return None
    flagclear = (0x8000 >> shift)
    flagclear = ~flagclear
    flags = flags & flagclear
    if attr < 16:
        zcode.memory.setbyte(address, (flags >> 8) & 255)
        zcode.memory.setbyte(address+1, flags & 255)
    elif attr < 32:
        zcode.memory.setbyte(address+2, (flags >> 8) & 255)
        zcode.memory.setbyte(address+3, flags & 255)
    elif attr < 48:
        zcode.memory.setword(address+4, flags)




def testattr(obj, attr): # tests if attribute number attr is on in object number obj
    address = findobject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address + 2)
        shift = attr - 16
    elif zcode.header.zversion() > 3 and attr < 48:
        flags = zcode.memory.getword(address + 4)
        shift = attr - 32
    else:
        zcode.error.strictz('Tried to test attribute ' + str(attr))
        return 0
    flagtest = (0x8000 >> shift)
    if flagtest & flags == flagtest:
        return 1
    else:
        return 0

def getshortname(obj): # returns the decoded short name of the object
    if obj == 0:
        return 0
    address = getpropertiesaddress(obj) + 1
    if zcode.memory.getbyte(address-1) == 0:
        return 'NoName'
    return zcode.text.decodetext(address)
    
# now we get to the properties themselves. This is a bit more difficult


def getpropsize(address): # given the address of the size byte of a property, returns the size
    if zcode.header.zversion() < 4:
        size = (zcode.memory.getbyte(address) >> 5) + 1
    else:
        if (zcode.memory.getbyte(address) >> 7) & 1 == 1:
            size = (zcode.memory.getbyte(address+1) & 0x3f)
            if size == 0:
                size = 64
        else:
            if (zcode.memory.getbyte(address) >> 6) & 1 == 1:
                size = 2
            else:
                size = 1
    return size

def getpropnum(address): # given the address of the size byte of a property, returns the property number
    if zcode.header.zversion() < 4:
        size = zcode.memory.getbyte(address) & 0x1F
    else:
        size = zcode.memory.getbyte(address) & 0x3f
    return size

def getnextprop(address):
    if zcode.header.zversion() < 4:
        sizelen = 1 # for z3 and earlier games, there is only one size byte
    else: #  in higher versions of the z-machine there may be either one or two bytes
        if zcode.memory.getbyte(address) & 128 == 128: # if the top bit of the first size byte is set, there are two size bytes
            sizelen = 2
        else: # if it is unset, there is only one size byte
            sizelen = 1
    address += sizelen + getpropsize(address)
    return address

def getfirstprop(obj): # returns the address of obj's first property
    address = getpropertiesaddress(obj) # find the start of the properties header
    headerlen = zcode.memory.getbyte(address) * 2 # find the length of the short name
    address = address + 1 + headerlen # find the first byte after the short name
    return address

def getpropaddr(obj, prop): # returns the address of the property prop of the object obj (this returns the address of the first byte of the size info, not the first byte of the data)
    address = getfirstprop(obj)
    num = getpropnum(address)
    if num == 0:
        return 0
    while num != prop:
        address = getnextprop(address)
        num = getpropnum(address) # find out what property this is
        if num == 0:
            prop = 0
            address = 0
    return address

def getpropdataaddr(obj, prop): # returns the address of the first byte of the data of the given property of the given object. No, really.
    sizeaddr = getpropaddr(obj, prop)
    if sizeaddr == 0:
        return 0
    if zcode.header.zversion() < 4:
        return sizeaddr + 1
    elif (zcode.memory.getbyte(sizeaddr) >> 7) & 1 == 1:
        return sizeaddr + 2
    else:
        return sizeaddr + 1
