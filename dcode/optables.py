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

import zcode
from zcode.constants import *
#define EXT_OP 192
#define XQEQU	EXT_OP + OPQEQU
#define OPCALL	224
#define OPPUT	225
#define OPPUTB	226
#define OPINPUT	227
#define OPSHOWI	228
#define OPSETI	229
#define OPSWAPI	230
#define OPSOUND	231
#define OPRAND	232
#define OPCLEAR	233
#define OPSHOWN	234
#define OPWIND	235
#define OPITER	236
#define OPLOAD	237
#define OPDUMP	238
#define OPREST	239
#define OPSAVE	240



















op2 = [ zcode.opcodes.z_badop,   #define OPUNDF 0
        zcode.opcodes.z_add,     #define OPADD  1
        zcode.opcodes.z_sub,     #define OPSUB  2
        zcode.opcodes.z_mul,     #define OPMUL  3
        zcode.opcodes.z_div,     #define OPDIV  4
        zcode.opcodes.z_mod,     #define OPMOD  5
        zcode.opcodes.z_and,     #define OPBAND 6
        zcode.opcodes.z_or,      #define OPBOR  7
        zcode.opcodes.z_badop, #zcode.opcodes.z_BXOR,     #define OPBXOR 8
        zcode.opcodes.z_test,    #define OPBTST 9
        zcode.opcodes.z_je,      #define OPQEQU 10
        zcode.opcodes.z_jl,      #define OPQLES 11
        zcode.opcodes.z_dec_chk, #define OPQDLE 12
        zcode.opcodes.z_jg,      #define OPQGRT 13
        zcode.opcodes.z_inc_chk, #define OPQIGR 14
        zcode.opcodes.z_store,   #define OPSET  15
        zcode.opcodes.z_loadw,   #define OPGET  16
        zcode.opcodes.z_loadb,   #define OPGETB 17
      ]

op1 = [ zcode.opcodes.z_push, #define OPPUSH	128
        zcode.opcodes.z_pull, #define OPPOP	129
        zcode.opcodes.z_load, #define OPVALU	130
        zcode.opcodes.z_inc,  #define OPINC	131
        zcode.opcodes.z_dec,  #define OPDEC	132
        zcode.opcodes.z_jz,   #define OPQZER	133
        zcode.opcodes.z_not,  #define OPBCOM	134	/* "BNOT" */
        zcode.opcodes.z_jump, #define OPJUMP	135
        zcode.opcodes.z_ret,  #define OPRETU	136
      ]

op0 = [ zcode.opcodes.z_nop,        #define OPNOOP 176
        zcode.opcodes.z_rtrue,      #define OPRTRU 177
        zcode.opcodes.z_rfalse,     #define OPRFAL 178
        zcode.opcodes.z_ret_popped, #define OPRSTA 179
        zcode.opcodes.z_pop,        #define OPFSTA 180
        zcode.opcodes.z_quit,       #define OPQUIT 181
        zcode.opcodes.z_piracy,     #define OPCOPY 182
        zcode.opcodes.z_verify,     #define OPVERI 183
      ]

opvar = [ zcode.opcodes.z_call_vs,#define OPCALL	224
          zcode.opcodes.z_storew,#define OPPUT	225
          zcode.opcodes.z_storeb,#define OPPUTB	226
          zcode.opcodes.z_read_char,#define OPINPUT	227
          zcode.opcodes.z_badop,#zcode.opcodes.SHOWI#define OPSHOWI	228
          zcode.opcodes.z_badop,#zcode.opcodes.SETI #define OPSETI	229
          zcode.opcodes.z_badop,#zcode.opcodes.SWAPI #define OPSWAPI	230
          zcode.opcodes.z_sound_effect,#define OPSOUND	231
          zcode.opcodes.z_random,#define OPRAND	232
          zcode.opcodes.z_erase_window,#define OPCLEAR	233
          zcode.opcodes.z_badop,#zcode.opcodes.SHOWN,#define OPSHOWN	234
          zcode.opcodes.z_badop,#zcode.opcodes.OPWIND,#define OPWIND	235
          zcode.opcodes.z_badop,# zcode.opcodes.OPITER,#define OPITER	236
          zcode.opcodes.z_badop,#zcode.opcodes.LOAD,#define OPLOAD	237
          zcode.opcodes.z_badop,#zcode.opcodes.DUMP,#define OPDUMP	238
          zcode.opcodes.z_save,#define OPREST	239
          zcode.opcodes.z_restore,#define OPSAVE	240
        ]

opext = [ zcode.opcodes.z_restore, #define XQEQU	EXT_OP + OPQEQU
        ]

def setup():
    pass

