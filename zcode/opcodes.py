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
import string
import blorb
import zio as io
import zcode


def unfinished():
    print('unfinished opcode')
    sys.exit()

# all the opcodes in alphabetical order

def z_add():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    result = a + b
    zcode.instructions.store(zcode.numbers.reduce(result))

def z_and():
    a = zcode.instructions.operands[0]
    b = zcode.instructions.operands[1]
    result = a & b
    zcode.instructions.store(result)

def z_art_shift():
    number = zcode.numbers.neg(zcode.instructions.operands[0])
    places = zcode.numbers.neg(zcode.instructions.operands[1])
    if places >= 0:
        result = zcode.numbers.unneg(number << places)
        result = result & 65535
    else:
        places = abs(places)
        result = zcode.numbers.unneg(number >> places)
        result = result & 65535
    zcode.instructions.store(result)

def z_buffer_mode():
    flag = zcode.instructions.operands[0]
    if zcode.header.zversion() != 6:
        window = zcode.screen.getWindow(0)
    else:
        window = zcode.screen.currentWindow
    if flag == 0:
        flag = 2
        window.flushTextBuffer()
    window.setattributes(8, flag) # set the buffer attribute for the lower window

def z_buffer_screen(): # Works as per standard, but doesn't actually do anything.
    zcode.instructions.store(0)

def z_call_1n():
    routine = zcode.instructions.operands[0]
    zcode.game.call(routine, [], 0) # routine address unpacking is done by the call routine

def z_call_1s():
    routine = zcode.instructions.operands[0]
    zcode.game.call(routine, [], 1)

def z_call_2n():
    routine = zcode.instructions.operands[0]
    arg1 = zcode.instructions.operands[1]
    zcode.game.call(routine, [arg1], 0)

def z_call_2s():
    routine = zcode.instructions.operands[0]
    arg1 = zcode.instructions.operands[1]
    zcode.game.call(routine, [arg1], 1)

def z_call_vn():
    routine = zcode.instructions.operands[0]
    args = zcode.instructions.operands[1:len(zcode.instructions.operands)]
    zcode.game.call(routine, args, 0)

def z_call_vs():
    routine = zcode.instructions.operands[0]
    args = zcode.instructions.operands[1:len(zcode.instructions.operands)]
    zcode.game.call(routine, args, 1)

def z_call_vn2():
    routine = zcode.instructions.operands[0]
    args = zcode.instructions.operands[1:len(zcode.instructions.operands)]
    zcode.game.call(routine, args, 0)

def z_call_vs2():
    routine = zcode.instructions.operands[0]
    args = zcode.instructions.operands[1:len(zcode.instructions.operands)]
    zcode.game.call(routine, args, 1)

def z_catch():
    x = len(zcode.game.callstack)
    zcode.instructions.store(x)

def z_check_arg_count():
    argnum = zcode.instructions.operands[0]
    if argnum <= zcode.game.currentframe.numargs:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_check_unicode():
    charnumber = zcode.instructions.operands[0]
    if charnumber < 0x20 or (charnumber >= 0x7f and charnumber <= 0x9f):
        zcode.instructions.store(0) # can't print or read these characters
    #elif charnumber < 128:
    #    zcode.instructions.store(3) # can read and print ASCII
    elif charnumber < 256:
        zcode.instructions.store(3) # can read and print Latin-1
    elif charnumber > 255:
        zcode.instructions.store(1)
    else:
        zcode.instructions.store(0)

def z_clear_attr():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to clear an attribute in object 0')
    else:
        attribute = zcode.instructions.operands[1]
        zcode.objects.clearattr(object, attribute)

def z_copy_table():
    first = zcode.instructions.operands[0]
    second = zcode.instructions.operands[1]
    size = zcode.numbers.neg(zcode.instructions.operands[2])
    if second == 0:
        for a in range(size):
            zcode.memory.setbyte(first + a, 0)
    elif size >= 0:
        size = abs(size)
        if first < second:
            a = size
            while a > 0:
                a -= 1
                zcode.memory.setbyte(second+a, zcode.memory.getbyte(first+a))
        elif second < first:
            for a in range(size):
                zcode.memory.setbyte(second+a, zcode.memory.getbyte(first+a))
    else:
        size = abs(size)
        for a in range(size):
            zcode.memory.setbyte(second+a, zcode.memory.getbyte(first+a))            

def z_dec():
    x = zcode.numbers.neg(zcode.game.getvar(zcode.instructions.operands[0], True))
    x = zcode.numbers.reduce(x-1)
    zcode.game.setvar(zcode.instructions.operands[0], x, True)

def z_dec_chk():
    x = zcode.numbers.neg(zcode.game.getvar(zcode.instructions.operands[0], True))
    value = zcode.numbers.neg(zcode.instructions.operands[1])
    x = zcode.numbers.reduce(x - 1)
    zcode.game.setvar(zcode.instructions.operands[0], x, True)
    if x < value:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_div():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    result = zcode.numbers.div(a, b)
    zcode.instructions.store(zcode.numbers.reduce(result))

def z_draw_picture():
    picture_number = zcode.instructions.operands[0]
    if len(zcode.instructions.operands) > 1:
        y = zcode.instructions.operands[1]
    else:
        y = zcode.screen.currentWindow.getCursor()[1]
    if len(zcode.instructions.operands) > 2:
        x = zcode.instructions.operands[2]
    else:
        x = zcode.screen.currentWindow.getCursor()[0]
  
    zcode.screen.currentWindow.drawpic(picture_number, x, y)

def z_encode_text():
    zsciitext = zcode.instructions.operands[0]
    length = zcode.instructions.operands[1]
    frombyte = zcode.instructions.operands[2]
    codedtext = zcode.instructions.operands[3]
    intext = list(zcode.memory.getarray(zsciitext+frombyte, length))
    outtext = zcode.text.encodetext(intext)
    for a in range(len(outtext)):
        zcode.memory.setbyte(codedtext+a, outtext[a])

def z_erase_line():
    value = zcode.instructions.operands[0]
    if value == 1:
        zcode.screen.currentWindow.eraseline(zcode.screen.currentWindow.getSize()[0])
    elif zcode.header.zversion() != 6:
        pass
    else:
        zcode.screen.currentWindow.eraseline(value - 1)
        

def z_erase_picture():
    picture_number = zcode.instructions.operands[0]
    if len(zcode.instructions.operands) > 1:
        y = zcode.instructions.operands[1]
    else:
        y = zcode.screen.currentWindow.getCursor()[1]
    if len(zcode.instructions.operands) > 2:
        x = zcode.instructions.operands[2]
    else:
        x = zcode.screen.currentWindow.getCursor()[0]

    pic = False
    for a in zcode.screen.blorbs:
        pic = a.getPict(picture_number)
        scale = a.getScale(picture_number, zcode.screen.ioScreen.getWidth(), zcode.screen.ioScreen.getHeight())
   
    if pic != False:
        zcode.screen.currentWindow.erasepic(pic, x, y, scale)

def z_erase_window():
    window = zcode.instructions.operands[0]
    zcode.screen.eraseWindow(window)

def z_extended(debug=False): # This isn't really an opcode, but it's easier to treat it as such.
    oldPC = zcode.game.PC
    zcode.game.PC = zcode.instructions.decodeextended(zcode.game.PC)
    opcode = zcode.memory.getbyte(oldPC)
    if debug:
        print(zcode.optables.opext[opcode].__name__)
    zcode.optables.opext[opcode]()

def z_font_size():
    newsize = zcode.numbers.neg(zcode.instructions.operands[0])
    if zcode.header.zversion() != 6:
        if newsize == 0:
            zcode.screen.getWindow(0).getFont().resetSize()
            zcode.screen.getWindow(1).getFont().resetSize()
        if newsize > 0:
            zcode.screen.getWindow(0).getFont().increaseSize(newsize)
            zcode.screen.getWindow(1).getFont().increaseSize(newsize)
        if newsize < 0:
            zcode.screen.getWindow(0).getFont().decreaseSize(abs(newsize))
            zcode.screen.getWindow(1).getFont().decreaseSize(abs(newsize))
        
    else:
        if newsize == 0:
            zcode.screen.currentWindow.getFont().resetSize()
        if newsize > 0:
            zcode.screen.currentWindow.getFont().increaseSize(newsize)
        if newsize < 0:
            zcode.screen.currentWindow.getFont().decreaseSize(abs(newsize))
    result = True
    if result:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)


def z_gestalt(): # a z-spec 1.2 opcode.
    id = zcode.instructions.operands[0]
    arg1 = 0
    arg2 = 0
    arg3 = 0
    if len(zcode.instructions.operands) > 1:
        arg1 = zcode.instructions.operands[1]
    if len(zcode.instructions.operands) > 2:
        arg2 = zcode.instructions.operands[2]
    if len(zcode.instructions.operands) > 3:
        arg3 = zcode.instructions.operands[3]
    x = zcode.header.gestalt(id, arg1, arg2, arg3)
    zcode.instructions.store(zcode.numbers.neg(zcode.header.gestalt(id, arg1, arg2, arg3)))



def z_get_child():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to get child of object 0')
        zcode.instructions.store(0)
        zcode.instructions.branch(0)
    else:
        child = zcode.objects.getchild(object)
        zcode.instructions.store(child)
        if child == 0:
            zcode.instructions.branch(0)
        else:
            zcode.instructions.branch(1)

def z_get_cursor():
    zcode.screen.currentWindow.flushTextBuffer()
    array = zcode.instructions.operands[0]
    window = zcode.screen.currentWindow
    ypos = zcode.screen.pix2units(window.getCursor()[1], 0)
    xpos = zcode.screen.pix2units(window.getCursor()[0], 1)
    zcode.memory.setword(array, ypos)
    zcode.memory.setword(array+2, xpos)

def z_get_next_prop():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to find a property for object 0')
        zcode.instructions.store(0)
    else:
        property = zcode.instructions.operands[1]
        if property == 0:
            address = zcode.objects.getfirstprop(object)
            num = zcode.objects.getpropnum(address)
        else:
            address = zcode.objects.getpropaddr(object, property)
            address = zcode.objects.getnextprop(address)
            num = zcode.objects.getpropnum(address)
        zcode.instructions.store(num)

def z_get_parent():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to find the parent of object 0')
    parent = zcode.objects.getparent(object)
    zcode.instructions.store(parent)

def z_get_prop():
    object = zcode.instructions.operands[0]

    if object == 0:
        zcode.error.strictz('Tried to get a property for object 0')
        zcode.instructions.store(0)
    else:
        property = zcode.instructions.operands[1]
        address = zcode.objects.getpropaddr(object, property)
        if address == 0:
            result = zcode.objects.getdefault(property)
        else:
            size = zcode.objects.getpropsize(address)
            if size == 1:
                result = zcode.memory.getbyte(zcode.objects.getpropdataaddr(object, property))
            elif size == 2:
                result = zcode.memory.getword(zcode.objects.getpropdataaddr(object, property))
            else:
                result = zcode.memory.getword(zcode.objects.getpropdataaddr(object, property))
                zcode.error.strictz('Tried to read from a property with length > 2')
        zcode.instructions.store(result)
    
def z_get_prop_addr():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to find a property address for object 0')
        zcode.instructions.store(0)
    else:
        property = zcode.instructions.operands[1]
        result = zcode.objects.getpropdataaddr(object, property)
        zcode.instructions.store(result)
    

def z_get_prop_len():
    propaddr = zcode.instructions.operands[0]
    if propaddr == 0:
        result = 0
    elif zcode.header.zversion() > 3 and (zcode.memory.getbyte(zcode.instructions.operands[0]-1) >> 7) & 1 == 1:
        result = zcode.objects.getpropsize(propaddr - 2)
    else:
        result = zcode.objects.getpropsize(propaddr - 1)
    zcode.instructions.store(result)

def z_get_sibling():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to get the sibling of object 0')
        zcode.instructions.store(0)
        zcode.instructions.branch(0)
    else:
        sibling = zcode.objects.getsibling(object)
        zcode.instructions.store(sibling)
        if sibling == 0:
            zcode.instructions.branch(0)
        else:
            zcode.instructions.branch(1)

def z_get_wind_prop():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    
    propnum = zcode.instructions.operands[1]
    result = window.getprops(propnum)
    zcode.instructions.store(result)

def z_inc():
    x = zcode.numbers.neg(zcode.game.getvar(zcode.instructions.operands[0], True))
    x = zcode.numbers.reduce(x+1)
    zcode.game.setvar(zcode.instructions.operands[0], x, True)
        
def z_inc_chk():
    x = zcode.numbers.neg(zcode.game.getvar(zcode.instructions.operands[0], True))
    value = zcode.numbers.neg(zcode.instructions.operands[1])
    x = zcode.numbers.reduce(x+1)
    zcode.game.setvar(zcode.instructions.operands[0], x, True)
    if x > value:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_input_stream():
    stream = zcode.instructions.operands[0]
    zcode.input.setstream(stream)

def z_insert_obj():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to insert object 0 into an object')
    else:
        # first we have to remove the object from its old parent and siblings
        oldparent = zcode.objects.getparent(object)
        oldsibling = zcode.objects.getsibling(object)
        oldeldersibling = zcode.objects.geteldersibling(object)
        if oldeldersibling != 0: # the object had a valid parent and was not the eldest child
            zcode.objects.setsibling(oldeldersibling, oldsibling) # fill in the gap of siblings left by remove this object
        elif zcode.objects.getchild(oldparent) == object: # if the object was the eldest child
            zcode.objects.setchild(oldparent, oldsibling) # make the object's sibling the new eldest child, filling in the gap

        # then we have to put the object in the new parent
        newparent = zcode.instructions.operands[1]
        newsibling = zcode.objects.getchild(newparent)
        if newsibling == object:
            newsibling = oldsibling
        zcode.objects.setparent(object, newparent) # set the object's parent to newparent
        zcode.objects.setchild(newparent, object) # set the new parent's child to object
        zcode.objects.setsibling(object, newsibling) # set the object's sibling to newsibling

def z_je():
    condition = 0
    for a in range(1, len(zcode.instructions.operands)):
        if zcode.instructions.operands[0] == zcode.instructions.operands[a]:
            condition = 1
    zcode.instructions.branch(condition)
    
def z_jg():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    if a > b:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_jin():
    obj1 = zcode.instructions.operands[0]
    obj2 = zcode.instructions.operands[1]
    if obj1 == 0:
        zcode.error.strictz('Tried to find the parent of object 0')
    if zcode.objects.getparent(obj1) == obj2:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_jl():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    if a < b:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)
    
def z_jump():
    offset = zcode.instructions.operands[0] - 2
    offset = zcode.numbers.neg(offset)
    zcode.game.PC += offset

def z_jz():
    a = zcode.instructions.operands[0]
    if a == 0:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_load():
    var = zcode.instructions.operands[0]
    zcode.instructions.store(zcode.game.getvar(var, True))

def z_loadb():
    array = zcode.instructions.operands[0]
    byteindex = zcode.numbers.neg(zcode.instructions.operands[1])
    zcode.instructions.store(zcode.memory.getbyte(array + byteindex))

def z_loadw():
    array = zcode.instructions.operands[0]
    wordindex = zcode.numbers.neg(zcode.instructions.operands[1])
    zcode.instructions.store(zcode.memory.getword(array + (2 * wordindex)))
    #print hex(zcode.memory.getword(array + (2 * wordindex)))

def z_log_shift():
    number = zcode.instructions.operands[0]
    places = zcode.numbers.neg(zcode.instructions.operands[1])
    if places >= 0:
        result = number << places
        result = result & 65535
    else:
        places = abs(places)
        result = number >> places
        result = result & 65535
    zcode.instructions.store(result)

def z_make_menu():
    number = zcode.instructions.operands[0]
    table = zcode.instructions.operands[1]
    if table == 0:
        result = io.pygame.destroymenu(number)
        zcode.instructions.branch(result)
    else:
        tablelen = zcode.memory.getword(table)
        items = []
        address = table + 2
        for a in range(tablelen):
            stringaddress = zcode.memory.getword(address)
            stringlen = zcode.memory.getbyte(stringaddress)
            stringaddress += 1
            #itemlist = []
            itemlist = [chr(zcode.memory.getbyte(stringaddress+b)) for b in xrange(stringlen)]
            #for b in range(stringlen):
            #    itemlist.append(chr(zcode.memory.getbyte(stringaddress+b)))
            item = string.join(itemlist, '')
            items.append(item)
            address += 2
        result = io.pygame.makemenu(items[0], items[1:len(items)], number)
        zcode.instructions.branch(result)

def z_mod():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    result = zcode.numbers.mod(a, b)
    zcode.instructions.store(zcode.numbers.reduce(result))

def z_mouse_window():
    window = zcode.instructions.operands[0]
    zcode.screen.mouse_window = window

def z_move_window():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    y = zcode.instructions.operands[1]
    x = zcode.instructions.operands[2]
    window.setPosition(x,y)

def z_mul():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    result = a * b
    zcode.instructions.store(zcode.numbers.reduce(result))

def z_new_line():
    zcode.output.printtext('\r')


def z_nop():
    pass

def z_not():
    value = zcode.instructions.operands[0]
    zcode.instructions.store(~value)

def z_or():
    a = zcode.instructions.operands[0]
    b = zcode.instructions.operands[1]
    result = a | b
    zcode.instructions.store(result)

def z_output_stream(): # unfinished (need to fix the width stuff)
    stream = zcode.numbers.neg(zcode.instructions.operands[0])
    if stream == 3:
        table = zcode.instructions.operands[1]
        if zcode.header.zversion() == 6 and len(zcode.instructions.operands) > 2:
            width = zcode.numbers.neg(zcode.instructions.operands[2])
            if width >= 0:
                width = zcode.screen.getWindow(width).getSize()[0]
            elif width < 0:
                width = abs(width)
        else:
            width = None
        zcode.output.openstream(3, table, width)
    elif stream == 5:
        table = zcode.instructions.operands[1]
        zcode.output.openstream(5, table)
    else:
        if stream > 0:
            zcode.output.openstream(abs(stream))
        elif stream < 0:
            zcode.output.closestream(abs(stream))
    
def z_picture_data():
    picnum = zcode.instructions.operands[0]
    array = zcode.instructions.operands[1]
    if picnum == 0:
        picindex = {}
        for a in zcode.screen.blorbs:
            keys = list(a.resindex[b'Pict'].keys())
            for key in keys:
                picindex[key] = a.resindex[b'Pict'][key]
            relnum = a.release
        zcode.memory.setword(array, len(picindex))
        zcode.memory.setword(array+2, relnum)
        # I'm assuming that if no pictures are available, we don't branch
        if len(picindex) > 0:
            zcode.instructions.branch(1)
        else:
            zcode.instructions.branch(0)
    else:
        pic = False
        for a in zcode.screen.blorbs:
            pic = a.getPict(picnum)
            scale = a.getScale(picnum, zcode.screen.ioScreen.getWidth(), zcode.screen.ioScreen.getWidth())

        if pic != False:
            if len(pic) == 8: # If it's only eight bytes long, it should be a Rect.
                pic = blorb.rect(pic)
            else:
                pic = io.pygame.image(pic)

            height = int(pic.getHeight()) * scale
            width = int(pic.getWidth()) * scale
            zcode.memory.setword(array, height)
            zcode.memory.setword(array+2, width)
            zcode.instructions.branch(1)
        else:

            zcode.instructions.branch(0)

def z_picture_table():
    pass

def z_piracy():
    zcode.instructions.branch(1)

def z_pop():
    zcode.game.currentframe.evalstack.pop()

def z_pop_stack():
    items = zcode.instructions.operands[0]
    if len(zcode.instructions.operands) > 1:
        stack = zcode.instructions.operands[1]
    else:
        stack = None
    if stack == None:
        for a in range(items):
            zcode.game.currentframe.evalstack.pop()
    else:
        zcode.game.popuserstack(stack, items)

def z_print(): #int
    address = zcode.game.PC
    textlen = zcode.text.gettextlength(address)
    zcode.game.PC = textlen + address
    zcode.output.printtext(zcode.text.decodetext(address))
    

def z_print_addr():
    byteaddress = zcode.instructions.operands[0]
    zcode.output.printtext(zcode.text.decodetext(byteaddress))

def z_print_char():
    char = zcode.text.getZSCIIchar(zcode.instructions.operands[0])
    zcode.output.printtext(char)

def z_print_form(): # unfinished (it sort of works, but doesn't do line breaks right)
    linestart = zcode.instructions.operands[0]
    linelen = zcode.memory.getword(linestart)
    x, y = zcode.screen.currentWindow.getCursor()
    while linelen != 0:
        linestart += 2
        for a in range(linelen):
            char = chr(zcode.memory.getbyte(linestart+a))
            zcode.output.printtext(char)
        linestart += linelen
        linelen = zcode.memory.getword(linestart)
        y += zcode.screen.currentWindow.getFont().getHeight()
        zcode.screen.currentWindow.setCursor(x, y)
        zcode.screen.currentWindow.flushTextBuffer()

def z_print_num():
    num = zcode.numbers.neg(zcode.instructions.operands[0])
    zcode.output.printtext(str(num))

def z_print_obj():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to print short name of object 0')
    else:
        result = zcode.objects.getshortname(object)
        zcode.output.printtext(zcode.objects.getshortname(object))

def z_print_paddr():
    packedaddress = zcode.instructions.operands[0]
    zcode.output.printtext(zcode.text.decodetext(zcode.memory.unpackaddress(packedaddress, 2)))

def z_print_ret(): #int
    address = zcode.game.PC
    textlen = zcode.text.gettextlength(address)
    zcode.game.PC = address + textlen
    zcode.game.ret(1)
    zcode.output.printtext(zcode.text.decodetext(address))
    zcode.output.printtext('\r')

def z_print_table():
    zcode.screen.currentWindow.flushTextBuffer()
    zsciitext = zcode.instructions.operands[0]
    width = zcode.instructions.operands[1]
    if len(zcode.instructions.operands) > 2:
        height = zcode.instructions.operands[2]
    else:
        height = 1
    if len(zcode.instructions.operands) > 3:
        skip = zcode.instructions.operands[3]
    else:
        skip = 0

    x,y = zcode.screen.currentWindow.getCursor()
    c = 0

    for a in range(height):
        for b in range(width):
            t = zcode.text.getZSCIIchar(zcode.memory.getbyte(zsciitext + c))
            zcode.output.printtext(t)
            c += 1
        c += skip
        if a != height - 1:
            if zcode.header.zversion() != 6 and zcode.screen.currentWindow.window_id == '0': # special behaviour for lower window in most versions
                zcode.output.printtext('\r')
            else:
                y += zcode.screen.currentWindow.getFont().getHeight()
                zcode.screen.currentWindow.setCursor(x, y)
                zcode.screen.currentWindow.flushTextBuffer()
    zcode.screen.currentWindow.flushTextBuffer()
            
    

def z_print_unicode():
    try:
        char = chr(zcode.instructions.operands[0])
    except:
        char = '?'
    zcode.output.printtext(char)


def z_pull():
    if zcode.header.zversion() == 6:
        if len(zcode.instructions.operands) > 0:
            address = zcode.instructions.operands[0]
            zcode.instructions.store(zcode.game.pulluserstack(address))
        else:
            zcode.instructions.store(zcode.game.getvar(0, True))
    else:
        zcode.game.setvar(zcode.instructions.operands[0], zcode.game.getvar(0), True)
        

def z_push():
    value = zcode.instructions.operands[0]
    zcode.game.setvar(0, value)

def z_push_stack():
    value = zcode.instructions.operands[0]
    stack = zcode.instructions.operands[1]
    zcode.instructions.branch(zcode.game.pushuserstack(stack, value))

def z_put_prop():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to write to a property in object 0')
    else:
        property = zcode.instructions.operands[1]
        value = zcode.instructions.operands[2]
        address = zcode.objects.getpropaddr(object, property)
        if address == 0:
            zcode.error.strictz('Tried to write to a non-existent property')
        propsize = zcode.objects.getpropsize(address)
        if propsize == 1:
            zcode.memory.setbyte(zcode.objects.getpropdataaddr(object, property), value)
        elif propsize == 2:
            zcode.memory.setword(zcode.objects.getpropdataaddr(object, property), value)
        else:
            zcode.error.strictz('Tried to write to a property of length > 2')
            zcode.memory.setword(zcode.objects.getpropdataaddr(object, property), value)


def z_put_wind_prop():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    propnum = zcode.instructions.operands[1]
    value = zcode.instructions.operands[2]
    window.setprops(propnum, value)

def z_quit():
    zcode.game.interruptstack = [] # clear the interrupt stack so that it doesn't call a routine after we're supposed to have quit
    zcode.sounds.stopall()
    zcode.screen.currentWindow.getFont().resetSize()
    zcode.screen.currentWindow.printText('\r[Press any key to quit]')
    zcode.screen.currentWindow.flushTextBuffer()
    inp = None
    while inp == None:
        inp = zcode.input.getinput()
    sys.exit()

def z_random():
    range = zcode.numbers.neg(zcode.instructions.operands[0])
    if range > 0:
        zcode.instructions.store(zcode.numbers.getrandom(range))
    else:
        zcode.numbers.randomize(abs(range))
        zcode.instructions.store(0)

def z_read():
    zcode.screen.currentWindow.showCursor()
    zcode.screen.currentWindow.line_count = 0
    if zcode.header.zversion() < 4:
        zcode.screen.updatestatusline()

    zcode.screen.currentWindow.flushTextBuffer()

    text = zcode.instructions.operands[0]
    if len(zcode.instructions.operands) > 1:
        parse = zcode.instructions.operands[1]
    else:
        parse = 0

    if zcode.header.zversion() >= 4 and len(zcode.instructions.operands) > 2:
        t = zcode.instructions.operands[2]
        r = zcode.instructions.operands[3]
        zcode.game.timerroutine = r
        zcode.game.timerreturned = 1
        io.pygame.starttimer(t, zcode.game.firetimer)


    if zcode.header.zversion() >= 5:
        leftover = zcode.memory.getbyte(text+1)
    else:
        leftover = 0
    
    maxinput = zcode.memory.getbyte(text)
    if zcode.header.zversion() < 5:
        maxinput += 1
        start = 1
    else:
        start = 2

    for a in range(leftover):
        zcode.input.instring.append(zcode.memory.getbyte(text+2+a))
    inchar = None
    while inchar not in zcode.input.gettermchars() and inchar != 13 and zcode.game.timervalue == False:
        if len(zcode.input.instring) < maxinput:
            display = True
        else:
            display = False
        inchar = zcode.input.getinput(display)
        if inchar == 8:
            if zcode.input.instring:
                c = zcode.input.instring.pop()
                zcode.screen.currentWindow.backspace(chr(c))
        elif inchar and display:
            zcode.input.instring.append(inchar)
            zcode.screen.currentWindow.showCursor()
    zcode.screen.currentWindow.hideCursor()
    if zcode.game.timervalue == True:
        termchar = 0
        zcode.game.timervalue = False
    else:
        termchar = zcode.input.instring.pop()
    io.pygame.stoptimer()

    zcode.input.commandhistory.reverse()
    zcode.input.commandhistory.append(zcode.input.instring)
    zcode.input.commandhistory.reverse()

    inp = [chr(a) for a in zcode.input.instring]
    inp = ''.join(inp)
    inp = inp.lower()



    zcode.output.streams[4].write(inp)
    zcode.output.streams[4].write('\n')

    zcode.input.instring = []

    chplace = -1

    for a in range(len(inp)):
        zcode.memory.setbyte(text + start + a, ord(inp[a]))

    if zcode.header.zversion() < 5:
        zcode.memory.setbyte(text+1+len(inp), 0)
    else:
        zcode.memory.setbyte(text+1, len(inp))

    if zcode.header.zversion() < 5 or parse != 0:
        zcode.dictionary.tokenise(inp, parse)

    if zcode.header.zversion() >= 5:
        zcode.instructions.store(termchar)
    


            

def z_read_char():
    zcode.screen.currentWindow.flushTextBuffer()
    zcode.screen.currentWindow.line_count = 0
    if zcode.header.zversion() >= 4 and len(zcode.instructions.operands) > 1 and zcode.game.timervalue == False:
        t = zcode.instructions.operands[1]
        r = zcode.instructions.operands[2]
        zcode.game.timerroutine = r
        zcode.game.timerreturned = 1
        io.pygame.starttimer(t, zcode.game.firetimer)
    inchar = None
    zcode.screen.currentWindow.showCursor()
    while inchar == None:
        if zcode.game.timervalue == True:
            inchar = 0
            zcode.game.timervalue = False
        else:
            inchar = zcode.input.getinput(False)
    io.pygame.stoptimer()
    zcode.screen.currentWindow.hideCursor()
    zcode.instructions.store(inchar)


def z_read_file():
    nameloc = zcode.instructions.operands[0]
    table = zcode.instructions.operands[1]
    length = zcode.instructions.operands[2]
    seek = zcode.instructions.operands[3]
    namelen = zcode.memory.getbyte(nameloc)
    if namelen == 0: # prompt for a filename
        filename = None
        prompt = True
    else:
        name = list(zcode.memory.getarray(nameloc+1, namelen))
        filename = []
        try:
            for a in name:
                filename.append(chr(a))
        except:
            filename = []
    if len(filename) > 0:
        filename = ''.join(filename)
        prompt = False
    else:
        filename = None
    try:
        data = zcode.input.readfile(length, filename, prompt, seek)
        zcode.memory.setarray(table, data)

        zcode.instructions.store(len(data))
    except:
        zcode.instructions.store(0)

def z_read_mouse():
    array = zcode.instructions.operands[0]
    zcode.memory.setword(array, zcode.input.mouse.ypos)
    zcode.memory.setword(array+2, zcode.input.mouse.xpos)

    mmap = zcode.input.mouse.buttons[:]
    #mmap.reverse()
    val = 1
    buttonbits = 0
    for a in mmap:
        buttonbits += val*a
        val *= 2
    zcode.memory.setword(array+4, buttonbits)

    zcode.memory.setword(array+6, 0) # menus not supported yet

def z_remove_obj():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to remove object 0 from the object tree')
    else:
        parent = zcode.objects.getparent(object) # find out what the parent is
        sibling = zcode.objects.getsibling(object) # find out what the sibling is
        eldersibling = zcode.objects.geteldersibling(object) # find out what the elder sibling is

        zcode.objects.setparent(object, 0) # set the object's parent to 0
        if eldersibling == 0: # if there was no elder sibling, sibling is now the child of parent
            zcode.objects.setchild(parent, sibling)
        else: # otherwise, sibling is now the sibling of eldersibling
            zcode.objects.setsibling(eldersibling, sibling)

def z_restart():
    zcode.sounds.stopall()
    zcode.game.interruptstack = [] # clear the interrupt stack so that it doesn't call a routine after we've restarted
    zcode.screen.eraseWindow(zcode.numbers.unneg(-1))
    # should really make sure the transcription bit stays set 
    zcode.memory.data = zcode.memory.originaldata[:] # reset the memory contents
    zcode.game.setup() # reset all the module contents
    zcode.header.setup()
    zcode.objects.setup()
    zcode.screen.setup(zcode.screen.blorbs, zcode.screen.ioScreen.getWidth(), zcode.screen.ioScreen.getHeight(), restarted=True)
    zcode.text.setup()
    zcode.optables.setup()
    zcode.routines.restart = 1

def z_restore():

    if len(zcode.instructions.operands) > 0:
        table = zcode.instructions.operands[0]
        bytes = zcode.instructions.operands[1]
        try:
            nameloc = zcode.instructions.operands[2]
            namelen = zcode.memory.getbyte(nameloc)
            name = list(zcode.memory.getarray(nameloc+1, namelen))
            filename = []
            for a in name:
                filename.append(chr(a))
        except:
            filename = []
        if len(filename) > 0:
            filename = ''.join(filename)
        else:
            filename = None
        try:
            prompt = zcode.instructions.operands[3]
        except:
            prompt = 1
        #data = zcode.game.restore(''.join(filename), prompt)
        data = zcode.input.readfile(bytes, filename, prompt)
            
        if data == 0:
            zcode.instructions.store(0)
        else:
            data = data[:bytes]
            for a in range(len(data)):
                zcode.memory.setbyte(table+a, data[a])
            zcode.instructions.store(len(data))
                 
    else:       
        result = zcode.game.restore()
        if result == 0:
            if zcode.header.zversion() < 5:
                zcode.instructions.branch(0)
            else:
                zcode.instructions.store(0)
        else:
            # if we're here, all the memory stuff ought to be set up. We just need to return the correct value. Maybe.
            #zcode.screen.erasewindow(zcode.numbers.unneg(-1))
            zcode.header.setup()
            if zcode.header.zversion() < 5:
                zcode.instructions.branch(1)
            else:
                zcode.instructions.store(2)
        

def z_restore_undo():
    zcode.instructions.store(zcode.game.restore_undo())

def z_ret():
    value = zcode.instructions.operands[0]
    zcode.game.ret(value)

def z_ret_popped():
    value = zcode.game.getvar(0) # get the value off of the top of the stack
    zcode.game.ret(value)

def z_rfalse():
    zcode.game.ret(0)

def z_rtrue():
    zcode.game.ret(1)

def z_save(): 
    if zcode.header.zversion() < 5:
        result = zcode.game.save()
        zcode.instructions.branch(result)
    else:
        if len(zcode.instructions.operands) > 0:
            table = zcode.instructions.operands[0]
            bytes = zcode.instructions.operands[1]
            data = zcode.memory.getarray(table, bytes)
            try:
                nameloc = zcode.instructions.operands[2]
                namelen = zcode.memory.getbyte(nameloc)
                name = list(zcode.memory.getarray(nameloc+1, namelen))
                filename = []
                for a in name:
                    filename.append(chr(a))
            except:
                filename = []
            if len(filename) > 0:
                filename = ''.join(filename)
            else:
                filename = None
            try:
                prompt = zcode.instructions.operands[3]
            except:
                prompt = 1
            try:
                zcode.output.writefile(data, filename, prompt, False)
                result = 1
            except:
                result = 0
        else:
            result = zcode.game.save()
        zcode.instructions.store(result) 

def z_save_undo():
    zcode.instructions.store(zcode.game.save_undo())

def z_scan_table():
    x = zcode.instructions.operands[0]
    table = zcode.instructions.operands[1]
    length = zcode.instructions.operands[2]
    if len(zcode.instructions.operands) > 3:
        form = zcode.instructions.operands[3]
    else:
        form = 0x82
    result = 0
    fieldlen = form & 127
    place = 0
    for a in range(length):
        if (result == 0):
            if form & 128 == 128:
                y = zcode.memory.getword(table+(a*fieldlen))
                if x == zcode.memory.getword(table+(a*fieldlen)):
                    result = 1
                    place = table + (a*fieldlen)
            else:
                if x == zcode.memory.getbyte(table+(a*fieldlen)):
                    result = 1
                    place = table + (a*fieldlen)
    zcode.instructions.store(place)
    zcode.instructions.branch(result)

def z_scroll_window():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    window.flushTextBuffer()
    pixels = zcode.numbers.neg(zcode.instructions.operands[1])
    if pixels < 0:
        dir = 1
    else:
        dir = 0
    window.scroll(abs(pixels), dir)

def z_set_attr():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to set an attribute in object 0')
    else:
        attribute = zcode.instructions.operands[1]
        zcode.objects.setattr(object, attribute)



def z_set_colour():
    foreground = zcode.numbers.neg(zcode.instructions.operands[0])
    background = zcode.numbers.neg(zcode.instructions.operands[1])
    # if the colours are out of the range expected, use the default colours
    # this can happen if Beyond Zork is run on a terp with an unexpected
    # interpreter number
    if foreground > 12:
        foreground = zcode.header.getdeffgcolour()
    if background > 12 and background != 15:
        background = zcode.header.getdefbgcolour()
    if foreground == 1:
        foreground = zcode.header.getdeffgcolour()
    if background == 1:
        background = zcode.header.getdefbgcolour()

    if zcode.header.zversion() != 6:
        if foreground == 0:
            foreground = zcode.screen.zwindow[0].getBasicColours()[1]
        if background == 0:
            background = zcode.screen.zwindow[0].getBasicColours()[0]
        zcode.screen.zwindow[0].setBasicColours(foreground, background)
        zcode.screen.zwindow[1].setBasicColours(foreground, background)
    else:
        if len(zcode.instructions.operands) > 2:
            window = zcode.screen.getWindow(zcode.instructions.operands[2])
        else:
            window = zcode.screen.currentWindow
        if foreground == 0:
            foreground = window.getBasicColours()[1]
        if background == 0:
            background = window.getBasicColours()[0]
        if foreground == -1:
            foreground = window.getPixelColour(window.getCursor()[0], window.getCursor()[1])
            foreground = window.getTrueFromReal(foreground)
            foreground = zcode.screen.reverseSpectrumLookup(foreground)
            if foreground == False:
                foreground = 16
        if background == -1:
            background = window.getPixelColour(window.getCursor()[0], window.getCursor()[1])
            background = window.getTrueFromReal(background)
            background = zcode.screen.reverseSpectrumLookup(background)
            if background == False:
                background = 16
        window.setBasicColours(foreground, background)
    

def z_set_cursor():
    y = zcode.numbers.neg(zcode.instructions.operands[0])
    if len(zcode.instructions.operands) > 1:
        x = zcode.instructions.operands[1]
    else:
        x = None
    if len(zcode.instructions.operands) > 2:
        window = zcode.screen.getWindow(zcode.instructions.operands[2])
    else:
        window = zcode.screen.currentWindow
    window.flushTextBuffer()
    if zcode.header.zversion() == 6 and y < 0:
        if y == -1:
            zcode.screen.cursoroff()
        elif y == -2:
            zcode.screen.cursoron()
    elif x:
        window.setCursor(zcode.screen.units2pix(x, horizontal=True, coord=True), zcode.screen.units2pix(y, horizontal=False, coord=True))
        window.setCursorToMargin()

def z_set_font():
    font = zcode.instructions.operands[0]
    if zcode.header.zversion() != 6:
        zcode.screen.zwindow[0].setFontByNumber(font)
        result = zcode.screen.zwindow[1].setFontByNumber(font)
        zcode.instructions.store(result)
    else:
        if len(zcode.instructions.operands) > 1:
            window = zcode.screen.getWindow(zcode.instructions.operands[1])
        else:
            window = zcode.screen.currentWindow
        result = window.setFontByNumber(font)
        zcode.instructions.store(result)


def z_set_margins():
    left = zcode.instructions.operands[0]
    right = zcode.instructions.operands[1]
    if len(zcode.instructions.operands) > 2:
        window = zcode.screen.getWindow(zcode.instructions.operands[2])
    else:
        window = zcode.screen.currentWindow
    window.setMargins(left, right)

def z_set_text_style():
    style = zcode.instructions.operands[0]
    if zcode.header.zversion() != 6:
        zcode.screen.zwindow[0].setStyle(style)
        zcode.screen.zwindow[1].setStyle(style)
    else:
        zcode.screen.currentWindow.setStyle(style)


def z_set_true_colour(): # a z-spec 1.1 opcode.
    foreground = zcode.numbers.neg(zcode.instructions.operands[0])
    background = zcode.numbers.neg(zcode.instructions.operands[1])
    fgtc=False
    bgtc=False

    if foreground == -1:
        foreground = zcode.header.gettruedefaultforeground()
    if background == -1:
        background = zcode.header.gettruedefaultbackground()
    if zcode.header.zversion() != 6:
        if foreground == -2:
            foreground = zcode.screen.zwindow[0].getTrueColours()[0]
        if background == -2:
            background = zcode.screen.zwindow[0].getTrueColours()[1]
        zcode.screen.zwindow[0].setTrueColours(foreground, background)
        zcode.screen.zwindow[1].setTrueColours(foreground, background)
    else:
        if len(zcode.instructions.operands) > 2:
            window = zcode.screen.getWindow(zcode.instructions.operands[2])
        else:
            window = zcode.screen.currentWindow
        if foreground == -2:
            foreground = window.getTrueColours()[0]
        if background == -2:
            background = window.getTrueColours()[1]
        window.setTrueColours(foreground, background)

def z_set_window():
    zcode.screen.currentWindow.flushTextBuffer()
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    zcode.screen.currentWindow = window


def z_show_status():
    zcode.screen.updatestatusline()

def z_sound_effect():
    number = zcode.instructions.operands[0]
    if number < 3:
        zcode.sounds.beep(number)
    else:
        effect = zcode.instructions.operands[1]
        if len(zcode.instructions.operands) > 2:
            volume = zcode.instructions.operands[2] & 255
            repeats = zcode.instructions.operands[2] >> 8
        else:
            volume = 8
            repeats = 1
        if volume == 255:
            volume = 8
        volume = (1/8) * volume
        if len(zcode.instructions.operands) > 3:
            routine = zcode.instructions.operands[3]
        else:
            routine = 0
        zcode.sounds.playsound(number, effect, volume, repeats, routine)

def z_sound_channel(): # a z-spec 1.2 opcode.
    type = zcode.instructions.operands[0] 
    channel = zcode.instructions.operands[1]
    effect = zcode.instructions.operands[2] 
    if len(zcode.instructions.operands) > 3:
        val = zcode.instructions.operands[3]
    if effect == 1:
        if channel > len(zcode.sounds.soundchannels[type]):
            rvalue = 0
        else:
            zcode.sounds.currentchannel[type] = channel
            rvalue = 1
    elif effect == 2:
        if val == 255:
            val = 8
        volume = (1/8) * val
        rvalue = 1 

        zcode.sounds.soundchannels[type][channel-1].setvolume(volume)
    else:
        rvalue = 0
    zcode.instructions.store(rvalue)

def z_sound_data(): # a z-spec 1.2 opcode.
    number = zcode.instructions.operands[0] 
    arr = zcode.instructions.operands[1]
    branch = 0
    if number == 0:
        for a in zcode.sounds.blorbs:
            keys = list(a.resindex[b'Pict'].keys())
            relnum = a.release
        zcode.memory.setword(arr, len(keys))
        zcode.memory.setword(arr+2, relnum)
        if len(keys) > 0:
            branch = 1
    else:
        s = zcode.sounds.Sound(number)
        if s.sound != None: # if the sound actually has data, it's valid
            branch = 1
            zcode.memory.setword(arr, s.type)
            c = zcode.sounds.currentchannel[s.type]
            if zcode.sounds.soundchannels[s.type][c-1].sound.number == s.number: 
                t = zcode.sounds.soundchannels[s.type][c-1].getpos()
                t /= 100
                if t > 32767:
                    t =  32767
            else:
                t = zcode.numbers.unneg(-1)
            
            zcode.memory.setword(arr+2, t)
    zcode.instructions.branch(branch) 

def z_split_window():
    if zcode.header.zversion() != 6:
        lines = zcode.instructions.operands[0]
        size = lines * zcode.screen.getWindow(1).getFont().getHeight()
    else:
        size = zcode.instructions.operands[0]
    zcode.screen.split(size)

def z_store():
    var = zcode.instructions.operands[0]
    value = zcode.instructions.operands[1]
    zcode.game.setvar(var, value, True)

def z_storeb():
    array = zcode.instructions.operands[0]
    byteindex = zcode.numbers.neg(zcode.instructions.operands[1])
    value = zcode.instructions.operands[2]
    zcode.memory.setbyte(array + byteindex, value)

def z_storew():
    array = zcode.instructions.operands[0]
    wordindex = zcode.numbers.neg(zcode.instructions.operands[1])
    value = zcode.instructions.operands[2]
    zcode.memory.setword(array + (2 * wordindex), value)

def z_sub():
    a = zcode.numbers.neg(zcode.instructions.operands[0])
    b = zcode.numbers.neg(zcode.instructions.operands[1])
    result = a - b
    zcode.instructions.store(zcode.numbers.reduce(result))

def z_test():
    bitmap = zcode.instructions.operands[0]
    flag = zcode.instructions.operands[1]
    if bitmap & flag == flag:
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)
        
def z_test_attr():
    object = zcode.instructions.operands[0]
    if object == 0:
        zcode.error.strictz('Tried to test an attribute in object 0')
        zcode.instructions.branch(0)
    else:
        attribute = zcode.instructions.operands[1]
        if zcode.objects.testattr(object, attribute):
            zcode.instructions.branch(1)
        else:
            zcode.instructions.branch(0)

def z_throw():
    value = zcode.instructions.operands[0]
    frame = zcode.instructions.operands[1]
    while len(zcode.game.callstack) > frame:
        zcode.game.callstack.pop() # remove frames from the stack until the top frame is the one in value
    zcode.game.ret(value)

def z_tokenise():
    text = zcode.instructions.operands[0]
    parse = zcode.instructions.operands[1]
    if len(zcode.instructions.operands) > 2:
        dictionaryaddress = zcode.instructions.operands[2]
    else:
        dictionaryaddress = 0
    if len(zcode.instructions.operands) > 3:
        flag = zcode.instructions.operands[3]
    else:
        flag = 0
    if zcode.header.zversion() < 5:
        address = text
        byte = 1
        while byte != 0:
            address += 1
            byte = zcode.memory.getbyte(address)
        length = address-(text+1)
        temp = zcode.memory.getarray(text+1, length)
        intext = ''.join([chr(b) for b in temp])
    else:
        textlen = zcode.memory.getbyte(text+1)
        temp = zcode.memory.getarray(text+2, textlen)
        intext = ''.join([chr(b) for b in temp])
    zcode.dictionary.tokenise(intext, parse, dictionaryaddress, flag)

def z_verify():
    if zcode.memory.verify():
        zcode.instructions.branch(1)
    else:
        zcode.instructions.branch(0)

def z_window_size():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    y = zcode.instructions.operands[1]
    x = zcode.instructions.operands[2]
    window.setSize(x, y)
    if window.getCursor()[0] > window.getSize()[0] or window.getCursor()[1] > window.getSize()[1]:
        window.setCursor(1,1)

def z_window_style():
    window = zcode.screen.getWindow(zcode.instructions.operands[0])
    flags = zcode.instructions.operands[1]
    if len(zcode.instructions.operands) > 2:
        operation = zcode.instructions.operands[2]
    else:
        operation = 0
    window.setattributes(flags, operation)

def z_write_file():
    nameloc = zcode.instructions.operands[0]
    table = zcode.instructions.operands[1]
    length = zcode.instructions.operands[2]
    mode = zcode.instructions.operands[3]
    namelen = zcode.memory.getbyte(nameloc)
    data = zcode.memory.getarray(table, length)
    if namelen == 0: # prompt for a filename
        filename = None
        prompt = True
    else:
        name = list(zcode.memory.getarray(nameloc+1, namelen))
        filename = []
        try:
            for a in name:
                filename.append(chr(a))
        except:
            filename = []
    if len(filename) > 0:
        filename = ''.join(filename)
        prompt = False
    else:
        filename = None
    if mode == 2:
        append = True
    else:
        append = False
    try:
        zcode.output.writefile(data, filename, prompt, append)
        zcode.instructions.store(1)
    except:
        zcode.instructions.store(0)
    
def z_badop(): # not really an opcode, this is called when the opcode is unknown
    zcode.error.fatal('Unknown opcode at ' + hex(zcode.game.PC))

# not part of any standard or standard proposal I know of, I think I just made these two up.

def z_get_pixel_array(): 
    y = zcode.instructions.operands[0]
    x = zcode.instructions.operands[1]
    width = zcode.instructions.operands[2]
    height = zcode.instructions.operands[3]
    zcode.screen.io.pygame.screen.getpixelarray(x, y, width, height)

def z_draw_pixel_array(): 
    drawfrom = zcode.instructions.operands[0]
    drawto = zcode.instructions.operands[1]
    if drawfrom == 0:
        zcode.instructions.operands[2] 
