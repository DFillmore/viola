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

tables = {}

def readTableDirectory(fontFile):
    #offset subtable

    #Type	    Name	        Description
    #uint32	    scaler type	    A tag to indicate the OFA scaler to be used to rasterize this font; see the note on the scaler type below for more information.
    #uint16	    numTables	    number of tables
    #uint16	    searchRange	    (maximum power of 2 <= numTables)*16
    #uint16	    entrySelector	log2(maximum power of 2 <= numTables)
    #uint16	    rangeShift	    numTables*16-searchRange
    b = fontFile.read(4)
    scaler = int.from_bytes(b, byteorder='big')

    b = fontFile.read(2)
    numTables = int.from_bytes(b, byteorder='big')

    b = fontFile.read(2)
    searchRange = int.from_bytes(b, byteorder='big')

    b = fontFile.read(2)
    entrySelector = int.from_bytes(b, byteorder='big')

    b = fontFile.read(2)
    rangeShift = int.from_bytes(b, byteorder='big')


    #The table directory

    #Type	    Name	    Description
    #uint32	    tag	        4-byte identifier
    #uint32	    checkSum	checksum for this table
    #uint32	    offset	    offset from beginning of sfnt
    #uint32	    length	    length of this table in bytes (actual length not padded length)

    for a in range(numTables):
        table = {}

        b = fontFile.read(4)
        t = b.decode('utf-8')

        b = fontFile.read(4)
        table['checkSum'] = int.from_bytes(b, byteorder='big')

        b = fontFile.read(4)
        table['offset'] = int.from_bytes(b, byteorder='big')

        b = fontFile.read(4)
        table['length'] = int.from_bytes(b, byteorder='big')

        tables[t] = table


def readcmap(fontFile):
    o = tables['cmap']['offset']
    fontFile.seek(o)

    #The 'cmap' index
    #Type	    Name	            Description
    #UInt16	    version	            Version number (Set to zero)
    #UInt16	    numberSubtables	    Number of encoding subtables
    strt = fontFile.tell()
    b = fontFile.read(2)
    vers = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    numberSubtables = int.from_bytes(b, byteorder='big')


    #The 'cmap' encoding subtable
    #Type	    Name	            Description
    #UInt16	    platformID	        Platform identifier
    #UInt16	    platformSpecificID	Platform-specific encoding identifier
    #UInt32	    offset	            Offset of the mapping table


    for a in range(numberSubtables):
        b = fontFile.read(2)
        platformID = int.from_bytes(b, byteorder='big')
        b = fontFile.read(2)
        platformSpecificID = int.from_bytes(b, byteorder='big')
        b = fontFile.read(4)
        o = int.from_bytes(b, byteorder='big')
        if platformID == 0: # Unicode
            mapOffset = o



    fontFile.seek(strt)
    fontFile.seek(mapOffset, 1)

    # we're assuming the format of the cmap table is 4. 
    #'cmap' format 4
    #Type	    Name	                    Description
    #UInt16	    format	                    Format number is set to 4
    #UInt16	    length	                    Length of subtable in bytes
    #UInt16	    language	                Language code (see above)
    #UInt16	    segCountX2	                2 * segCount
    #UInt16	    searchRange	                2 * (2**FLOOR(log2(segCount)))
    #UInt16	    entrySelector	            log2(searchRange/2)
    #UInt16	    rangeShift	                (2 * segCount) - searchRange
    #UInt16	    endCode[segCount]	        Ending character code for each segment, last = 0xFFFF.
    #UInt16	    reservedPad	                This value should be zero
    #UInt16	    startCode[segCount]	        Starting character code for each segment
    #UInt16	    idDelta[segCount]	        Delta for all character codes in segment
    #UInt16	    idRangeOffset[segCount]	    Offset in bytes to glyph indexArray, or 0
    #UInt16	    glyphIndexArray[variable]	Glyph index array
    endCodes = []
    startCodes = []
    idDeltas = []
    idRangeOffsets = []
    glyphIndexArrays = []

    b = fontFile.read(2)
    form = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    leng = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    language = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    segCount = int(int.from_bytes(b, byteorder='big') / 2)
    b = fontFile.read(2)
    searchRange = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    entrySelector = int.from_bytes(b, byteorder='big')
    b = fontFile.read(2)
    rangeShift = int.from_bytes(b, byteorder='big')


    for a in range(segCount):
        b = fontFile.read(2)
        endCodes.append(int.from_bytes(b, byteorder='big'))

    b = fontFile.read(2)
    reservedPad = int.from_bytes(b, byteorder='big')

    for a in range(segCount):
        b = fontFile.read(2)
        startCodes.append(int.from_bytes(b, byteorder='big'))

    for a in range(segCount):
        b = fontFile.read(2)
        idDeltas.append(int.from_bytes(b, byteorder='big'))

    for a in range(segCount):
        b = fontFile.read(2)
        idRangeOffsets.append(int.from_bytes(b, byteorder='big'))

    b = fontFile.read(2)
    glyphIndexArray = int.from_bytes(b, byteorder='big')


    #to find if a glyph is available, search endCodes for the first number >= the character number we want. If the corresponding startCode is <= the character number, there is a glyph. If not, not.
    codes = []
    for c in range(segCount):
        endCode = endCodes[c] + 1
        startCode = startCodes[c]
        codes.extend(range(startCode, endCode))
    return codes

def getCodes(fontFileName):
    if fontFileName:
        fontFile = open(fontFileName, 'rb')
        readTableDirectory(fontFile)
        codes = readcmap(fontFile)
        fontFile.close()
    else:
        codes = []
    return codes


