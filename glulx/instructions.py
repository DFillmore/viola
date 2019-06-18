def decode(address):
    fl = memory.getbyte(address) >> 6
    if fl == 0:
        opnum = memory.getbyte(address)
    elif fl == 2:
        opnum = memory.gethalfword(address)
    elif fl == 3:
        opnum = memory.getword(address)
    
