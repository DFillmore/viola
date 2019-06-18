static operandlist_t list_none = { 0, 4, NULL };

static int array_S[1] = { modeform_Store };
static operandlist_t list_S = { 1, 4, array_S };
static int array_LS[2] = { modeform_Load, modeform_Store };
static operandlist_t list_LS = { 2, 4, array_LS };
static int array_LLS[3] = { modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLS = { 3, 4, array_LLS };
static int array_LLLS[4] = { modeform_Load, modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLLS = { 4, 4, array_LLLS };
static int array_LLLLS[5] = { modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLLLS = { 5, 4, array_LLLLS };
static int array_LLLLLS[6] = { modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLLLLS = { 6, 4, array_LLLLLS };
static int array_LLLLLLS[7] = { modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLLLLLS = { 7, 4, array_LLLLLLS };
static int array_LLLLLLLS[8] = { modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Load, modeform_Store };
static operandlist_t list_LLLLLLLS = { 8, 4, array_LLLLLLLS };

static int array_L[1] = { modeform_Load };
static operandlist_t list_L = { 1, 4, array_L };
static int array_LL[2] = { modeform_Load, modeform_Load };
static operandlist_t list_LL = { 2, 4, array_LL };
static int array_LLL[3] = { modeform_Load, modeform_Load, modeform_Load };
static operandlist_t list_LLL = { 3, 4, array_LLL };
static operandlist_t list_2LS = { 2, 2, array_LS };
static operandlist_t list_1LS = { 2, 1, array_LS };
static int array_SL[2] = { modeform_Store, modeform_Load };
static operandlist_t list_SL = { 2, 4, array_SL };
static int array_SS[2] = { modeform_Store, modeform_Store };
static operandlist_t list_SS = { 2, 4, array_SS };

nops = { 0: opcodes.nop }

LLS = { op_add:
op_sub:
 op_mul:
 op_div:
 op_mod:
 op_bitand:
 op_bitor:
op_bitxor:
op_shiftl:
op_sshiftr:
op_ushiftr:

}

LS ={

  case op_neg:
  case op_bitnot:
    return &list_LS;
}

L ={
  case op_jump:
  case op_jumpabs:}

LL = {
  case op_jz:
  case op_jnz:
    return &list_LL;}

LLL = {
  case op_jeq:
  case op_jne:
  case op_jlt:
  case op_jge:
  case op_jgt:
  case op_jle:
  case op_jltu:
  case op_jgeu:
  case op_jgtu:
  case op_jleu:
    return &list_LLL;}



  case op_call:
    return &list_LLS;
  case op_return:
    return &list_L;
  case op_catch:
    return &list_SL;
  case op_throw:
    return &list_LL;
  case op_tailcall:
    return &list_LL;

  case op_sexb:
  case op_sexs:
    return &list_LS;

  case op_copy:
    return &list_LS;
  case op_copys:
    return &list_2LS;
  case op_copyb:
    return &list_1LS;
  case op_aload:
  case op_aloads:
  case op_aloadb:
  case op_aloadbit:
    return &list_LLS;
  case op_astore:
  case op_astores:
  case op_astoreb:
  case op_astorebit:
    return &list_LLL;

  case op_stkcount:
    return &list_S;
  case op_stkpeek:
    return &list_LS;
  case op_stkswap: 
    return &list_none;
  case op_stkroll:
    return &list_LL;
  case op_stkcopy:
    return &list_L;

  case op_streamchar:
  case op_streamunichar:
  case op_streamnum:
  case op_streamstr:
    return &list_L;
  case op_getstringtbl:
    return &list_S;
  case op_setstringtbl:
    return &list_L;
  case op_getiosys:
    return &list_SS;
  case op_setiosys:
    return &list_LL;

  case op_random:
    return &list_LS;
  case op_setrandom:
    return &list_L;

  case op_verify:
    return &list_S;
  case op_restart:
    return &list_none;
  case op_save:
  case op_restore:
    return &list_LS;
  case op_saveundo:
  case op_restoreundo:
    return &list_S;
  case op_protect:
    return &list_LL;

  case op_quit:
    return &list_none;

  case op_gestalt:
    return &list_LLS;

  case op_debugtrap: 
    return &list_L;

  case op_getmemsize:
    return &list_S;
  case op_setmemsize:
    return &list_LS;

  case op_linearsearch:
    return &list_LLLLLLLS;
  case op_binarysearch:
    return &list_LLLLLLLS;
  case op_linkedsearch:
    return &list_LLLLLLS;

  case op_glk:
    return &list_LLS;

  case op_callf:
    return &list_LS;
  case op_callfi:
    return &list_LLS;
  case op_callfii:
    return &list_LLLS;
  case op_callfiii:
    return &list_LLLLS;

  case op_mzero:
    return &list_LL;
  case op_mcopy:
    return &list_LLL;
  case op_malloc:
    return &list_LS;
  case op_mfree:
    return &list_L;

  default: 
    return NULL;
  }
}