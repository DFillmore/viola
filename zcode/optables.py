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

op2 = [ zcode.opcodes.z_badop,
        zcode.opcodes.z_je,
        zcode.opcodes.z_jl,
        zcode.opcodes.z_jg,
        zcode.opcodes.z_dec_chk,
        zcode.opcodes.z_inc_chk,
        zcode.opcodes.z_jin,
        zcode.opcodes.z_test,
        zcode.opcodes.z_or,
        zcode.opcodes.z_and,
        zcode.opcodes.z_test_attr,
        zcode.opcodes.z_set_attr,
        zcode.opcodes.z_clear_attr,
        zcode.opcodes.z_store,
        zcode.opcodes.z_insert_obj,
        zcode.opcodes.z_loadw,
        zcode.opcodes.z_loadb,
        zcode.opcodes.z_get_prop,
        zcode.opcodes.z_get_prop_addr,
        zcode.opcodes.z_get_next_prop,
        zcode.opcodes.z_add,
        zcode.opcodes.z_sub,
        zcode.opcodes.z_mul,
        zcode.opcodes.z_div,
        zcode.opcodes.z_mod,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop
      ]
        
op1 = [ zcode.opcodes.z_jz,
        zcode.opcodes.z_get_sibling,
        zcode.opcodes.z_get_child,
        zcode.opcodes.z_get_parent,
        zcode.opcodes.z_get_prop_len,
        zcode.opcodes.z_inc,
        zcode.opcodes.z_dec,
        zcode.opcodes.z_print_addr,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_remove_obj,
        zcode.opcodes.z_print_obj,
        zcode.opcodes.z_ret,
        zcode.opcodes.z_jump,
        zcode.opcodes.z_print_paddr,
        zcode.opcodes.z_load,
        zcode.opcodes.z_not
      ]

op0 = [ zcode.opcodes.z_rtrue,
        zcode.opcodes.z_rfalse,
        zcode.opcodes.z_print,
        zcode.opcodes.z_print_ret,
        zcode.opcodes.z_nop,
        zcode.opcodes.z_save,
        zcode.opcodes.z_restore,
        zcode.opcodes.z_restart,
        zcode.opcodes.z_ret_popped,
        zcode.opcodes.z_pop,
        zcode.opcodes.z_quit,
        zcode.opcodes.z_new_line,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop,
        zcode.opcodes.z_badop
      ]

opvar = [ zcode.opcodes.z_call_vs,
          zcode.opcodes.z_storew,
          zcode.opcodes.z_storeb,
          zcode.opcodes.z_put_prop,
          zcode.opcodes.z_read,
          zcode.opcodes.z_print_char,
          zcode.opcodes.z_print_num,
          zcode.opcodes.z_random,
          zcode.opcodes.z_push,
          zcode.opcodes.z_pull,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop,
          zcode.opcodes.z_badop
        ]

opext = [zcode.opcodes.z_badop] * 256


def setup():
    global op2, op1, op0, opvar, opext

    if zcode.memory.data[0] >= 3:
        op0[0xc] = zcode.opcodes.z_show_status
        op0[0xd] = zcode.opcodes.z_verify
        opvar[0xa] = zcode.opcodes.z_split_window
        opvar[0xb] = zcode.opcodes.z_set_window
        opvar[0x13] = zcode.opcodes.z_output_stream
        opvar[0x14] = zcode.opcodes.z_input_stream
        opvar[0x15] = zcode.opcodes.z_sound_effect

    if zcode.memory.data[0] >= 4:
        op2[0x19] = zcode.opcodes.z_call_2s
        op1[0x8] = zcode.opcodes.z_call_1s
        op0[0xc] = zcode.opcodes.z_badop
        opvar[0xc] = zcode.opcodes.z_call_vs2
        opvar[0xd] = zcode.opcodes.z_erase_window
        opvar[0xe] = zcode.opcodes.z_erase_line
        opvar[0xf] = zcode.opcodes.z_set_cursor
        opvar[0x10] = zcode.opcodes.z_get_cursor
        opvar[0x11] = zcode.opcodes.z_set_text_style
        opvar[0x12] = zcode.opcodes.z_buffer_mode
        opvar[0x16] = zcode.opcodes.z_read_char
        opvar[0x17] = zcode.opcodes.z_scan_table

    if zcode.memory.data[0] >= 5:
        op2[0x1a] = zcode.opcodes.z_call_2n
        op2[0x1b] = zcode.opcodes.z_set_colour
        op2[0x1c] = zcode.opcodes.z_throw
        op1[0xf] = zcode.opcodes.z_call_1n
        op0[0x5] = zcode.opcodes.z_badop
        op0[0x6] = zcode.opcodes.z_badop
        op0[0x9] = zcode.opcodes.z_catch
        op0[0xe] = zcode.opcodes.z_extended
        op0[0xf] = zcode.opcodes.z_piracy
        opvar[0x18] = zcode.opcodes.z_not
        opvar[0x19] = zcode.opcodes.z_call_vn
        opvar[0x1a] = zcode.opcodes.z_call_vn2
        opvar[0x1b] = zcode.opcodes.z_tokenise
        opvar[0x1c] = zcode.opcodes.z_encode_text
        opvar[0x1d] = zcode.opcodes.z_copy_table
        opvar[0x1e] = zcode.opcodes.z_print_table
        opvar[0x1f] = zcode.opcodes.z_check_arg_count
        opext[0x0] = zcode.opcodes.z_save
        opext[0x1] = zcode.opcodes.z_restore
        opext[0x2] = zcode.opcodes.z_log_shift
        opext[0x3] = zcode.opcodes.z_art_shift
        opext[0x4] = zcode.opcodes.z_set_font
        opext[0x9] = zcode.opcodes.z_save_undo
        opext[0xa] = zcode.opcodes.z_restore_undo
        if zcode.use_standard >= STANDARD_10:  # Standard 1.0 or later
            opext[0xb] = zcode.opcodes.z_print_unicode
            opext[0xc] = zcode.opcodes.z_check_unicode
        if zcode.use_standard >= STANDARD_11:  # Standard 1.1 or later
            opext[0xd] = zcode.opcodes.z_set_true_colour

    if zcode.memory.data[0] == 6:
        opext[0x5] = zcode.opcodes.z_draw_picture
        opext[0x6] = zcode.opcodes.z_picture_data
        opext[0x7] = zcode.opcodes.z_erase_picture
        opext[0x8] = zcode.opcodes.z_set_margins
        opext[0x10] = zcode.opcodes.z_move_window
        opext[0x11] = zcode.opcodes.z_window_size
        opext[0x12] = zcode.opcodes.z_window_style
        opext[0x13] = zcode.opcodes.z_get_wind_prop
        opext[0x14] = zcode.opcodes.z_scroll_window
        opext[0x15] = zcode.opcodes.z_pop_stack
        opext[0x16] = zcode.opcodes.z_read_mouse
        opext[0x17] = zcode.opcodes.z_mouse_window
        opext[0x18] = zcode.opcodes.z_push_stack
        opext[0x19] = zcode.opcodes.z_put_wind_prop
        opext[0x1a] = zcode.opcodes.z_print_form
        opext[0x1b] = zcode.opcodes.z_make_menu
        opext[0x1c] = zcode.opcodes.z_picture_table
        if zcode.use_standard >= STANDARD_11:  # Standard 1.1 or later
            opext[0x1d] = zcode.opcodes.z_buffer_screen
