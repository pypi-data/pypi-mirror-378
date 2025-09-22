'''
custom_print module can handle any type of variable.
'''

#pylint: disable=bare-except
#pylint: disable=invalid-name
#pylint: disable=unused-import
#pylint: disable=line-too-long
#pylint: disable=too-many-lines
#pylint: disable=no-else-return
#pylint: disable=unused-variable
#pylint: disable=too-many-locals
#pylint: disable=protected-access
#pylint: disable=too-many-branches
#pylint: disable=consider-using-in
#pylint: disable=chained-comparison
#pylint: disable=too-many-arguments
#pylint: disable=too-many-statements
#pylint: disable=multiple-statements
#pylint: disable=consider-using-join
#pylint: disable=unspecified-encoding
#pylint: disable=unnecessary-negation
#pylint: disable=singleton-comparison
#pylint: disable=too-few-public-methods
#pylint: disable=too-many-nested-blocks
#pylint: disable=too-many-public-methods
#pylint: disable=expression-not-assigned
#pylint: disable=consider-using-enumerate
#pylint: disable=unnecessary-comprehension
#pylint: disable=too-many-return-statements
#pylint: disable=unbalanced-tuple-unpacking
#pylint: disable=consider-using-max-builtin
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-instance-attributes
#pylint: disable=too-many-positional-arguments
#pylint: disable=inconsistent-return-statements
#pylint: disable=possibly-used-before-assignment


#-----------------------------------------------------------------------------------------------------------------------------------------------------
#12345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
#        1         2         3         4         5         6         7         8         9         A         B         C         D         E         F
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Required Modules                                                                                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
from custom_print.ref_names import Align
from custom_print.fancy_message import FancyMessage
from custom_print.fancy_functions import move_cursor_right

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Font Style Class. Manipulate Font In The Terminal                                                                                                 --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# ansi codes
# reset_all : "\033[0m"         Terminal_Bell : "\a"
# bold_on   : "\033[1m"         underline_on  : "\033[4m"         hidden_on    : "\033[8m"
# bold_off  : "\033[22m"        underline_off : "\033[24m"        hidden_off   : "\033[28m"
# dim_on    : "\033[2m"         blinking_on   : "\033[5m"         strike_on    : "\033[9m"
# dim_off   : "\033[22m"        blinking_off  : "\033[25m"        strike_off   : "\033[29m"
# italic_on : "\033[3m"         reverse_on    : "\033[7m"         background   : "\033[48;5;{str(bg)}m"
# italic_off: "\033[23m"        reverse_off   : "\033[27m"        foreground   : "\033[38;5;{str(fg)}m"
# backspace : "\b"              horizontal tab: "\t"              vertical tab : "\v"
class FontStyle:
    '''
    FontStyle class print fancy text
    '''
    def __init__(self):
        # General Use
        self.bg  = -1;       self.bold      = False;    self.hidden    = False;    self.italic    = False
        self.fg  = -1;       self.underline = False;    self.strike    = False;    self.inverse   = False
        self.dim = False;    self.blinking  = False

        # Print_Style
        self.align = Align.JUSTIFY;    self.bg_top_lines    = 0
        self.forced_align = False;      self.bg_bottom_lines = 0

        # self.indent is used for style_on and for print_style when using justify
        self.indent    = 0

    def set_font_style(self)->str:

        '''  This function changes the attributes of the font (bold=bool, bg=int, fg=int).

        Colors range from -1 to 256, where -1 or 256 is the defualt one.  '''


        # bg_color and fg_color, are int values but we convert then to str values
        reset = "\033[0m"
        if self.bg < 0 or self.bg > 255:  bgc = "reset"
        else:                             bgc = str(self.bg)

        if self.fg < 0 or self.fg > 255:  fgc = "reset"
        else:                             fgc = str(self.fg)


        if (bgc == "reset" and fgc == "reset"):  settings = reset
        elif bgc == "reset" and fgc != "reset":  settings = reset+"\033[38;5;"+fgc+"m"
        elif bgc != "reset" and fgc == "reset":  settings = reset+"\033[48;5;"+bgc+"m"
        elif bgc != "reset" and fgc != "reset":  settings = reset+"\033[48;5;"+bgc+";38;5;"+fgc+"m"
        else:                                    settings = reset


        if   (self.bold == True and self.dim  == False): settings = settings + "\033[1m"
        elif (self.bold == True and self.dim  == True):  settings = settings + "\033[1m"
        elif (self.bold == False and self.dim == True):  settings = settings + "\033[2m"
        else:                                            pass   # (bold == False and dim == False):


        if self.italic == True:      settings = settings + "\033[3m"
        else:                        settings =  settings + "\033[23m"

        if self.underline == True:   settings = settings + "\033[4m"
        else:                        settings = settings + "\033[24m"

        if self.blinking == True:    settings = settings + "\033[5m"
        else:                        settings = settings + "\033[25m"

        if self.inverse == True:     settings = settings + "\033[7m"
        else:                        settings = settings + "\033[27m"

        if self.hidden == True:      settings = settings + "\033[8m"
        else:                        settings = settings + "\033[28m"

        if self.strike == True:      settings = settings + "\033[9m"
        else:                        settings = settings + "\033[29m"

        return settings



    def reset_style(self):
        '''
        Reset the FontStyle class
        '''
        # General Use
        self.bg  = -1;       self.bold      = False;    self.hidden    = False;    self.italic    = False
        self.fg  = -1;       self.underline = False;    self.strike    = False;    self.inverse   = False
        self.dim = False;    self.indent    = 0;        self.blinking  = False

        # print_style
        self.align = Align.JUSTIFY;    self.bg_top_lines     = 0
        self.forced_align = False;      self.bg_bottom_lines = 0



    def style_on(self)->str:
        '''
        Activate the style
        '''
        if self.indent <= 0:
            settings = self.set_font_style()# + f"\033[0C"
        else:                 settings = self.set_font_style() + f"\033[{str(self.indent)}C"
        return settings



    def style_off(self)->str:
        '''
        Deactivate the style
        '''
        return "\033[0m"



    def print_style(self, msg)->None:
        '''
        print_style will help to print a fancy statement on the terminal
        '''
        #---------------------------------------------------------------------------------------------------------------------------------
        def print_bg_lines(move_crs, insert_sp, settings, lines):
            if lines == 0:
                pass

            else:
                n = lines
                while n>0:
                    print(f"{move_crs}{settings}{insert_sp}\033[0m")
                    n -= 1

        #---------------------------------------------------------------------------------------------------------------------------------
        def terminal_cols_smaller_than_biggest_line():
            message_lst = msg.split()
            print(f"{settings}",end="")
            for l in range(len(message_lst)):
                for n in message_lst[l]:
                    print(f"{n}",end="")
                print(" ", end="")

            suma = 0
            for w in message_lst:
                suma += len(w) + 1

            if tncols > suma:
                diff = tncols - suma
                print(move_cursor_right(diff, True),end="")

            else:
                done = True
                while done:
                    suma = suma - tncols
                    if suma < 0:
                        done = False

                diff = suma * (-1)
                print(move_cursor_right(diff, True),end="")
            print("\033[0m",end="") # reset font


        #---------------------------------------------------------------------------------------------------------------------------------
        reset = "\033[0m"
        fm = FancyMessage()
        fm.left_indent = 0; fm.right_indent = 0
        tnrows, tncols, space_available, number_letter_line_list, adj_diff_space, new_msg, n_lines = fm.get_msg_attributes(msg,True)
        settings = self.set_font_style()

        cnt_l = 0     # counting the number of letter in the new message
        cnt_p = 0     # counting the position of the list containing the letters
        wd_line = ""  # keeps the line info
        wd_list = []  # keep the text of the lines as list

        for l in range(len(new_msg)):
            wd_line += new_msg[l]
            cnt_l += 1
            if cnt_l == number_letter_line_list[cnt_p]:
                cnt_l  = 0
                cnt_p += 1
                wd_list.append(wd_line)
                wd_line = ""

        biggets_line  = max(number_letter_line_list)
        bg_space_line = move_cursor_right(biggets_line,option_space=True)

        if biggets_line < tncols:
            #-----------------------------------------------------------------------------------------------------------------------------------------
            if self.align.lower() == Align.CENTER or self.align.lower() == "c":
            #-----------------------------------------------------------------------------------------------------------------------------------------
                move_cursor  = move_cursor_right(n=(int((tncols - biggets_line)/2)),option_space=False)
                print_bg_lines(move_cursor, bg_space_line , settings,self.bg_top_lines)
                if self.forced_align == True:
                    #---------------------------------------------------------------------------------------------------------------------------------
                    for l in wd_list:
                        l2 = int((biggets_line - len(l))/2)
                        r = int((biggets_line - len(l))%2)
                        print(f"{move_cursor}{settings}{move_cursor_right(n=l2,option_space=True)}{l}{move_cursor_right(n=l2+r,option_space=True)}{reset}")

                else:   # Center (force = False)
                    #---------------------------------------------------------------------------------------------------------------------------------
                    for l in wd_list:
                        adj = biggets_line - len(l)
                        print(f"{move_cursor}{settings}{l}{move_cursor_right(n=adj,option_space=True)}{reset}")
                print_bg_lines(move_cursor, bg_space_line , settings,self.bg_bottom_lines)


            #-----------------------------------------------------------------------------------------------------------------------------------------
            elif self.align.lower() == Align.RIGHT or self.align.lower() == "r":
            #-----------------------------------------------------------------------------------------------------------------------------------------
                move_cursor = move_cursor_right(n=(int(tncols - biggets_line)), option_space=False)
                print_bg_lines(move_cursor, bg_space_line , settings, self.bg_top_lines)
                if self.forced_align == True:
                    #---------------------------------------------------------------------------------------------------------------------------------
                    for l in wd_list:
                        l2 = int(tncols - biggets_line)
                        ll = biggets_line - len(l)
                        print(f"{move_cursor_right(n=l2,option_space=False)}{settings}{move_cursor_right(n=ll,option_space=True)}{l}{reset}")

                else:   # Right (forced = False)
                    #---------------------------------------------------------------------------------------------------------------------------------
                    for l in wd_list:
                        l2 = int(tncols - biggets_line)
                        ll = biggets_line - len(l)
                        print(f"{move_cursor_right(n=l2,option_space=False)}{settings}{l}{move_cursor_right(n=ll,option_space=True)}{reset}")

                print_bg_lines(move_cursor, bg_space_line , settings,self.bg_bottom_lines)


            #-----------------------------------------------------------------------------------------------------------------------------------------
            elif self.align.lower() == Align.LEFT or self.align.lower() == "l":
            #-----------------------------------------------------------------------------------------------------------------------------------------
                move_cursor = move_cursor_right(n=0, option_space=False)
                print_bg_lines(move_cursor, bg_space_line , settings, self.bg_top_lines)
                if self.forced_align == True:
                    for l in wd_list:
                        ll = biggets_line - len(l)
                        print(f"{settings}{l}{move_cursor_right(n=ll,option_space=True)}{reset}")

                else:   # Left (forced = False)
                    for l in wd_list:
                        ll = biggets_line - len(l)
                        print(f"{settings}{move_cursor_right(n=ll,option_space=True)}{l}{reset}")

                print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)


            #-----------------------------------------------------------------------------------------------------------------------------------------
            elif self.align.lower() == Align.JUSTIFY or self.align.lower() == "j":
            #-----------------------------------------------------------------------------------------------------------------------------------------
                move_cursor = move_cursor_right(n=self.indent, option_space=False)
                print_bg_lines(move_cursor, bg_space_line , settings, self.bg_top_lines)

                if self.forced_align == True:
                    for l in wd_list:
                        ll = biggets_line - len(l)
                        print(f"{move_cursor_right(n=self.indent,option_space=False)}{settings}{l}{move_cursor_right(n=ll,option_space=True)}{reset}")

                else:   # Justify (forced = False)
                    for l in wd_list:
                        ll = biggets_line - len(l)
                        print(f"{move_cursor_right(n=self.indent,option_space=False)}{settings}{move_cursor_right(n=ll,option_space=True)}{l}{reset}")

                print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)

            #-----------------------------------------------------------------------------------------------------------------------------------------
            else:
            #-----------------------------------------------------------------------------------------------------------------------------------------
                carry = 0
                if self.forced_align == True:
                    for l in range(len(number_letter_line_list)):
                        print(f"{move_cursor_right(self.indent,False)}{settings}",end="")
                        for n in range(number_letter_line_list[l]):
                            print(f"{new_msg[n+carry]}",end="")
                        carry += number_letter_line_list[l]
                        print(reset)
                else:
                    bg_space_line = move_cursor_right(tncols,option_space=True)
                    move_cursor = ""
                    print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)
                    terminal_cols_smaller_than_biggest_line()
                    print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)

        else:
            # It will come in only if the condition is = if biggets_line < tncols:
            bg_space_line = move_cursor_right(tncols,option_space=True)
            move_cursor = ""
            print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)
            terminal_cols_smaller_than_biggest_line()
            print_bg_lines(move_cursor, bg_space_line , settings, self.bg_bottom_lines)
