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


import zcode
        
def setup():
    global op2, op1, op0, opvar, opext
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
            zcode.opcodes.z_call_2s,
            zcode.opcodes.z_call_2n,
            zcode.opcodes.z_set_colour,
            zcode.opcodes.z_throw,
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
            zcode.opcodes.z_call_1s,
            zcode.opcodes.z_remove_obj,
            zcode.opcodes.z_print_obj,
            zcode.opcodes.z_ret,
            zcode.opcodes.z_jump,
            zcode.opcodes.z_print_paddr,
            zcode.opcodes.z_load,
            zcode.opcodes.z_call_1n
          ]

    op0 = [ zcode.opcodes.z_rtrue,
            zcode.opcodes.z_rfalse,
            zcode.opcodes.z_print,
            zcode.opcodes.z_print_ret,
            zcode.opcodes.z_nop,
            zcode.opcodes.z_badop,
            zcode.opcodes.z_badop,
            zcode.opcodes.z_restart,
            zcode.opcodes.z_ret_popped,
            zcode.opcodes.z_catch,
            zcode.opcodes.z_quit,
            zcode.opcodes.z_new_line,
            zcode.opcodes.z_badop,
            zcode.opcodes.z_verify,
            zcode.opcodes.z_extended,
            zcode.opcodes.z_piracy
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
              zcode.opcodes.z_split_window,
              zcode.opcodes.z_set_window,
              zcode.opcodes.z_call_vs2,
              zcode.opcodes.z_erase_window,
              zcode.opcodes.z_erase_line,
              zcode.opcodes.z_set_cursor,
              zcode.opcodes.z_get_cursor,
              zcode.opcodes.z_set_text_style,
              zcode.opcodes.z_buffer_mode,
              zcode.opcodes.z_output_stream,
              zcode.opcodes.z_input_stream,
              zcode.opcodes.z_sound_effect,
              zcode.opcodes.z_read_char,
              zcode.opcodes.z_scan_table,
              zcode.opcodes.z_not,
              zcode.opcodes.z_call_vn,
              zcode.opcodes.z_call_vn2,
              zcode.opcodes.z_tokenise,
              zcode.opcodes.z_encode_text,
              zcode.opcodes.z_copy_table,
              zcode.opcodes.z_print_table,
              zcode.opcodes.z_check_arg_count
            ]

    opext = [ zcode.opcodes.z_save,
              zcode.opcodes.z_restore,
              zcode.opcodes.z_log_shift,
              zcode.opcodes.z_art_shift,
              zcode.opcodes.z_set_font,
              zcode.opcodes.z_draw_picture,
              zcode.opcodes.z_picture_data,
              zcode.opcodes.z_erase_picture,
              zcode.opcodes.z_set_margins,
              zcode.opcodes.z_save_undo,
              zcode.opcodes.z_restore_undo,
              zcode.opcodes.z_print_unicode,
              zcode.opcodes.z_check_unicode,
              zcode.opcodes.z_set_true_colour,
              zcode.opcodes.z_sound_channel,
              zcode.opcodes.z_sound_data,
              zcode.opcodes.z_move_window,
              zcode.opcodes.z_window_size,
              zcode.opcodes.z_window_style,
              zcode.opcodes.z_get_wind_prop,
              zcode.opcodes.z_scroll_window,
              zcode.opcodes.z_pop_stack,
              zcode.opcodes.z_read_mouse,
              zcode.opcodes.z_mouse_window,
              zcode.opcodes.z_push_stack,
              zcode.opcodes.z_put_wind_prop,
              zcode.opcodes.z_print_form,
              zcode.opcodes.z_make_menu,
              zcode.opcodes.z_picture_table,
              zcode.opcodes.z_buffer_screen,
              zcode.opcodes.z_gestalt,
              zcode.opcodes.z_font_size,
              zcode.opcodes.z_write_file,
              zcode.opcodes.z_read_file
            ]
    if zcode.header.zversion() < 3:
        op0[0xc] = zcode.opcodes.z_badop
        op0[0xd] = zcode.opcodes.z_badop
        opvar[0xa] = zcode.opcodes.z_badop
        opvar[0xb] = zcode.opcodes.z_badop
        opvar[0x13] = zcode.opcodes.z_badop
        opvar[0x14] = zcode.opcodes.z_badop
        opvar[0x15] = zcode.opcodes.z_badop
    if zcode.header.zversion() < 4:
        op2[0x19] = zcode.opcodes.z_badop
        op1[0x8] = zcode.opcodes.z_badop
        op0[0xc] = zcode.opcodes.z_show_status
        opvar[0xc] = zcode.opcodes.z_badop
        opvar[0xd] = zcode.opcodes.z_badop
        opvar[0xe] = zcode.opcodes.z_badop
        opvar[0xf] = zcode.opcodes.z_badop
        opvar[0x10] = zcode.opcodes.z_badop
        opvar[0x11] = zcode.opcodes.z_badop
        opvar[0x12] = zcode.opcodes.z_badop
        opvar[0x16] = zcode.opcodes.z_badop
        opvar[0x17] = zcode.opcodes.z_badop
    if zcode.header.zversion() < 5:
        op2[0x1a] = zcode.opcodes.z_badop
        op2[0x1b] = zcode.opcodes.z_badop
        op2[0x1c] = zcode.opcodes.z_badop
        op1[0xf] = zcode.opcodes.z_not
        op0[0x5] = zcode.opcodes.z_save
        op0[0x6] = zcode.opcodes.z_restore
        op0[0x9] = zcode.opcodes.z_pop
        op0[0xe] = zcode.opcodes.z_badop
        op0[0xf] = zcode.opcodes.z_badop
        opvar[0x18] = zcode.opcodes.z_badop
        opvar[0x19] = zcode.opcodes.z_badop
        opvar[0x1a] = zcode.opcodes.z_badop
        opvar[0x1b] = zcode.opcodes.z_badop
        opvar[0x1c] = zcode.opcodes.z_badop
        opvar[0x1d] = zcode.opcodes.z_badop
        opvar[0x1e] = zcode.opcodes.z_badop
        opvar[0x1f] = zcode.opcodes.z_badop
        opext[0x0] = zcode.opcodes.z_badop
        opext[0x1] = zcode.opcodes.z_badop
        opext[0x2] = zcode.opcodes.z_badop
        opext[0x3] = zcode.opcodes.z_badop
        opext[0x4] = zcode.opcodes.z_badop
        opext[0x9] = zcode.opcodes.z_badop
        opext[0xa] = zcode.opcodes.z_badop
        opext[0xb] = zcode.opcodes.z_badop
        opext[0xc] = zcode.opcodes.z_badop
        opext[0xf] = zcode.opcodes.z_badop
        opext[0x1d] = zcode.opcodes.z_badop
    if zcode.header.zversion() != 6:
        opext[0x5] = zcode.opcodes.z_badop
        opext[0x6] = zcode.opcodes.z_badop
        opext[0x7] = zcode.opcodes.z_badop
        opext[0x8] = zcode.opcodes.z_badop
        opext[0x10] = zcode.opcodes.z_badop
        opext[0x11] = zcode.opcodes.z_badop
        opext[0x12] = zcode.opcodes.z_badop
        opext[0x13] = zcode.opcodes.z_badop
        opext[0x14] = zcode.opcodes.z_badop
        opext[0x15] = zcode.opcodes.z_badop
        opext[0x16] = zcode.opcodes.z_badop
        opext[0x17] = zcode.opcodes.z_badop
        opext[0x18] = zcode.opcodes.z_badop
        opext[0x19] = zcode.opcodes.z_badop
        opext[0x1a] = zcode.opcodes.z_badop
        opext[0x1b] = zcode.opcodes.z_badop
        opext[0x1c] = zcode.opcodes.z_badop
    for a in range(0x1e, 255):
        opext.append(zcode.opcodes.z_badop)
