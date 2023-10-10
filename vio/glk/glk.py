# gestalt






    

# window






# From the Glk Spec
# --------
# 1.1: Your Program's Main Function
#
# The top level of the program -- the main() function in C, for example -- belongs to Glk. [This means that Glk isn't really a 
# library. In a sense, you are writing a library, which is linked into Glk. This is bizarre to think about, so forget it.]
#
# You define a function called glk_main(), which the library calls to begin running your program. glk_main() should run until 
# your program is finished, and then return.
#
# Glk does all its user-interface work in a function called glk_select(). This function waits for an event -- typically the 
# player's input -- and returns an structure representing that event. This means that your program must have an event loop. In 
# the very simplest case, you could write
#
# void glk_main()
# {
#    event_t ev;
#    while (1) {
#        glk_select(&ev);
#        switch (ev.type) {
#            default:
#                /* do nothing */
#                break;
#        }
#    }
#}
# 
# --------
#
# This is not true for this python implementation of Glk.
# Instead, you would write something like:
#
# import glk
#
# def glk_main(): # this routine can be called anything you like
#   
#   while True:
#     ev = glk.select() # waits for an event to happen, and then returns the event object
#
# glk.init(glk_main) # start the glk process, passing your main routine to it

