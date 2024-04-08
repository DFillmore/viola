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

import zcode
from zcode.constants import *

object_location = {}
object_properties_address = {}
object_properties_data_address = {}
object_property_address = {}
object_data = []
largest_object_number = 0
object_data_length = 0

object_list = {}  # not a list


class z_object():
    location = False
    properties_address = False
    parent = False
    sibling = False
    child = False
    attributes = False
    elder_sibling = False


def setup():
    global propdef
    global objstart
    propdef = zcode.header.objtableloc
    if zcode.header.zversion < 4:
        objstart = propdef + 62
    else:
        objstart = propdef + 126


def getDefaultProperty(propnum):
    address = ((propnum - 1) * 2) + propdef
    return zcode.memory.getword(address)


def updateObjectData(wipe=False):
    global object_data
    global object_data_length

    if zcode.header.zversion < 4:
        object_data_length = (9 * largest_object_number) - 9
    else:
        object_data_length = (12 * largest_object_number) - 12

    object_data = zcode.memory.data[objstart:objstart + object_data_length]

    if wipe:  # the object table in the game's memory has been altered unexpectedly, so all our cached data is useless
        object_list = {}
        object_properties_address = {}
        object_properties_data_address = {}
        object_property_address = {}


def findObject(obj):
    """returns the address in memory of the object with the number given"""
    global object_list
    global largest_object_number
    if obj > largest_object_number:
        largest_object_number = obj
        updateObjectData()
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].location:
            return object_list[obj].location
    else:
        updateObjectData(wipe=True)
    if zcode.header.zversion < 4:
        address = objstart + (9 * obj) - 9
    else:
        address = objstart + (14 * obj) - 14
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.location = address
    object_list[obj] = o
    return address


def getParent(obj):
    """returns the number of the parent object of the object with the number given"""
    global object_list
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].parent:
            return object_list[obj].parent
    else:
        updateObjectData(wipe=True)
    address = findObject(obj)
    if zcode.header.zversion < 4:
        parent = zcode.memory.getbyte(address + 4)
    else:
        parent = zcode.memory.getword(address + 6)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.parent = parent
    object_list[obj] = o
    return parent


def getSibling(obj):
    """returns the number of the sibling object of the object with the number given"""
    global object_list
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].sibling:
            return object_list[obj].sibling
    else:
        updateObjectData(wipe=True)
    address = findObject(obj)
    if zcode.header.zversion < 4:
        sibling = zcode.memory.getbyte(address + 5)
    else:
        sibling = zcode.memory.getword(address + 8)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.sibling = sibling
    object_list[obj] = o
    return sibling


def getChild(obj):
    """returns the number of the child object of the object with the number given"""
    global object_list
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].child:
            return object_list[obj].child
    else:
        updateObjectData(wipe=True)
    address = findObject(obj)
    if zcode.header.zversion < 4:
        child = zcode.memory.getbyte(address + 6)
    else:
        child = zcode.memory.getword(address + 10)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.child = child
    object_list[obj] = o
    return child


def getElderSibling(obj):
    """returns the number of the object to which the object with the number given is the sibling"""
    global object_list
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].elder_sibling:
            return object_list[obj].elder_sibling
    else:
        updateObjectData(wipe=True)

    parent = getParent(obj)
    if parent == 0:  # there is no parent, so there is no elder sibling
        eldersibling = 0
    else:
        eldestchild = getChild(parent)
        if eldestchild == obj:  # there is no elder sibling
            eldersibling = 0
        else:
            sibling = getSibling(eldestchild)
            eldersibling = eldestchild
            while sibling != obj:
                eldersibling = getSibling(eldersibling)
                sibling = getSibling(eldersibling)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.elder_sibling = eldersibling
    object_list[obj] = o
    return eldersibling


def setParent(obj, parent):  # sets obj's parent to parent
    global object_list
    address = findObject(obj)
    if zcode.header.zversion < 4:
        zcode.memory.setbyte(address + 4, parent)
    else:
        zcode.memory.setword(address + 6, parent)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.elder_sibling = False
    o.parent = parent
    object_list[obj] = o
    updateObjectData()


def setSibling(obj, sibling):  # sets obj's sibling to sibling
    global object_list
    address = findObject(obj)
    if zcode.header.zversion < 4:
        zcode.memory.setbyte(address + 5, sibling)
    else:
        zcode.memory.setword(address + 8, sibling)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.elder_sibling = False
    o.sibling = sibling
    object_list[obj] = o
    updateObjectData()


def setChild(obj, child):  # sets obj's child to child
    global object_list
    address = findObject(obj)
    if zcode.header.zversion < 4:
        zcode.memory.setbyte(address + 6, child)
    else:
        zcode.memory.setword(address + 10, child)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.child = child
    object_list[obj] = o
    updateObjectData()


def getPropertiesAddress(obj):  # returns the address of the properties table for the object numbered obj
    global object_list
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_list and object_list[obj].properties_address:
            return object_list[obj].properties_address
    else:
        updateObjectData(wipe=True)

    address = findObject(obj)
    if zcode.header.zversion < 4:
        address = zcode.memory.getword(address + 7)
    else:
        address = zcode.memory.getword(address + 12)
    if obj in object_list:
        o = object_list[obj]
    else:
        o = z_object()
    o.properties_address = address
    object_list[obj] = o
    updateObjectData()

    return address


def setAttribute(obj, attr):  # sets attribute number attr in object number obj
    address = findObject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address + 2)
        shift = attr - 16
    elif attr < 48 and zcode.header.zversion > 3:
        flags = zcode.memory.getword(address + 4)
        shift = attr - 32
    else:  # this is an error condition
        zcode.error.strictz('Tried to set attribute ' + str(attr))
        return None
    flagset = (0x8000 >> shift)
    flags = flags | flagset
    if attr < 16:
        zcode.memory.setbyte(address, (flags >> 8) & 255)
        zcode.memory.setbyte(address + 1, flags & 255)
    elif attr < 32:
        zcode.memory.setbyte(address + 2, (flags >> 8) & 255)
        zcode.memory.setbyte(address + 3, flags & 255)
    elif attr < 48:
        zcode.memory.setword(address + 4, flags)


def clearAttribute(obj, attr):  # clears attribute number attr in object number obj
    address = findObject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address + 2)
        shift = attr - 16
    elif attr < 48 and zcode.header.zversion > 3:
        flags = zcode.memory.getword(address + 4)
        shift = attr - 32
    else:  # this is an error condition
        zcode.error.strictz('Tried to clear attribute ' + str(attr))
        return None
    flagclear = (0x8000 >> shift)
    flagclear = ~flagclear
    flags = flags & flagclear
    if attr < 16:
        zcode.memory.setbyte(address, (flags >> 8) & 255)
        zcode.memory.setbyte(address + 1, flags & 255)
    elif attr < 32:
        zcode.memory.setbyte(address + 2, (flags >> 8) & 255)
        zcode.memory.setbyte(address + 3, flags & 255)
    elif attr < 48:
        zcode.memory.setword(address + 4, flags)


def testAttribute(obj, attr):  # tests if attribute number attr is on in object number obj
    address = findObject(obj)
    if attr < 16:
        flags = zcode.memory.getword(address)
        shift = attr
    elif attr < 32:
        flags = zcode.memory.getword(address + 2)
        shift = attr - 16
    elif zcode.header.zversion > 3 and attr < 48:
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


def getShortName(obj):  # returns the decoded short name of the object
    if obj == 0:
        return 0
    address = getPropertiesAddress(obj) + 1
    if zcode.memory.getbyte(address - 1) == 0:
        return 'NoName'
    return zcode.text.decodetext(address)


# now we get to the properties themselves. This is a bit more difficult


def getPropertySize(address):  # given the address of the size byte of a property, returns the size
    if zcode.header.zversion < 4:
        size = (zcode.memory.getbyte(address) >> 5) + 1
    else:
        if (zcode.memory.getbyte(address) >> 7) & 1 == 1:
            size = (zcode.memory.getbyte(address + 1) & 0x3f)
            if size == 0:
                if zcode.use_standard >= STANDARD_10:  # Standard 1.0 and above
                    size = 64
                else:
                    zcode.error.warning('Property length of 0 (in Standard 1.0 and higher this would mean a length of 64)')
        else:
            if (zcode.memory.getbyte(address) >> 6) & 1 == 1:
                size = 2
            else:
                size = 1
    return size


def getPropertyNumber(address):  # given the address of the size byte of a property, returns the property number
    if zcode.header.zversion < 4:
        size = zcode.memory.getbyte(address) & 0x1F
    else:
        size = zcode.memory.getbyte(address) & 0x3f
    return size


def getNextProperty(address):
    if zcode.header.zversion < 4:
        sizelen = 1  # for z3 and earlier games, there is only one size byte
    else:  # in later versions of the z-machine there may be either one or two bytes
        if zcode.memory.getbyte(address) & 128 == 128:  # if the top bit of the first size byte is set, there are two size bytes
            sizelen = 2
        else:  # if it is unset, there is only one size byte
            sizelen = 1

    newaddress = address + sizelen + getPropertySize(address)
    return newaddress


def getFirstProperty(obj):  # returns the address of obj's first property
    address = getPropertiesAddress(obj)  # find the start of the properties header
    headerlen = zcode.memory.getbyte(address) * 2  # find the length of the short name
    address = address + 1 + headerlen  # find the first byte after the short name
    return address


def getPropertyAddress(obj, prop): # returns the address of the property prop of the object obj (this returns the address of the first byte of the size info, not the first byte of the data)
    global object_property_address
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_property_address:
            if prop in object_property_address[obj]:
                return object_property_address[obj][prop]
    else:
        updateObjectData(wipe=True)

    address = getFirstProperty(obj)
    num = getPropertyNumber(address)
    if num == 0:
        return 0
    while num != prop:
        address = getNextProperty(address)
        num = getPropertyNumber(address)  # find out what property this is
        if num == 0:
            prop = 0
            address = 0
    if obj not in object_property_address:
        object_property_address[obj] = {}
    object_property_address[obj][prop] = address
    return address


def getPropertyDataAddress(obj, prop):  # returns the address of the first byte of the data of the given property of the given object. No, really.
    if object_data == zcode.memory.data[objstart:objstart + object_data_length]:
        if obj in object_properties_data_address:
            if prop in object_properties_data_address[obj]:
                return object_properties_data_address[obj][prop]
    else:
        updateObjectData(wipe=True)

    sizeaddr = getPropertyAddress(obj, prop)
    if sizeaddr != 0:
        if zcode.header.zversion < 4:
            sizeaddr += 1
        elif (zcode.memory.getbyte(sizeaddr) >> 7) & 1 == 1:
            sizeaddr += 2
        else:
            sizeaddr += 1
    if obj not in object_properties_data_address:
        object_properties_data_address[obj] = {}
    object_properties_data_address[obj][prop] = sizeaddr
    return sizeaddr
