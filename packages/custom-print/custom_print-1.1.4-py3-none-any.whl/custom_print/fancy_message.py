'''
custom_print module can handle any type of variable.
'''

#pylint: disable=bare-except
#pylint: disable=invalid-name
#pylint: disable=unused-import
#pylint: disable=line-too-long
#pylint: disable=too-many-lines
#pylint: disable=no-else-return
#pylint: disable=wildcard-import
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
import os
from custom_print.fancy_cursor import*            # cursor already import Move Class

from custom_print.ref_names import Align
from custom_print.ref_names import Length_bg
from custom_print.ref_names import Line_Style

from custom_print.fancy_format import FancyFormat

from custom_print.fancy_functions import ins_chr
from custom_print.fancy_functions import set_font
from custom_print.fancy_functions import reset_font
from custom_print.fancy_functions import move_cursor_right
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Fancy Message Class (Single line or a Paragraph Text in the Terminal)                                                                             --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
class FancyMessage(Cursor):
    '''
    FancyMessage class
    '''
    def __init__(self):
        super().__init__()          # Super Class to use all (vars and funs) from Cursor Class
                                    # with the Initialization Draw Class(self), ex. self.gotoxy(x,y)
        self.body_bg        = 4;          self.body_underline = False     # 4         False
        self.body_fg        = 231;        self.body_blinking  = False     # 231       False
        self.body_bold      = False;      self.body_inverse   = False     # False     False
        self.body_dim       = False;      self.body_hidden    = False     # False     False
        self.body_italic    = False;      self.body_strike    = False     # False     False

        self.body_msg = "Body Msg";       self.help_lines = False

        self.left_indent = 2;             self.right_indent = 2
        self.top_lines = 1;               self.bottom_lines = 1

        self.length = Length_bg.ALL_ROW
        # These two options don't do anything when length = Length_bg.All_ROW
        self.adj_bg_lines_to_right_indent = False     # True or False
        self.adj_bg_msg_to_space_available = False    # True or False



        #--------------------------------------------------------------------
        # Note Settings Here, print_fancy_note
        self.note_msg = " Note: "
        self.note_align = Align.JUSTIFY;    self.note_position = 1
        self.note_bg = 231;                 self.note_fg = 0;                 self.note_bold      = False
        self.note_dim = False;              self.note_italic  = False;        self.note_underline = False
        self.note_blinking = False;         self.note_inverse = False;        self.note_hidden    = False
        self.note_strike = False;           self.note_left_space = 2;         self.note_right_space = 2

        # Title Settings Here, print_fancy_message
        self.title_align = Align.LEFT;      self.title_indent = 2;            self.title_msg = "" # title_indent works with Align.JUSTIFY
        self.lines_title_body = 1;          self.title_strike = False
        self.title_bg = 4;                  self.title_fg = 231;              self.title_bold  = False
        self.title_dim = False;             self.title_italic = False;        self.title_underline = False
        self.title_blinking = False;        self.title_inverse = False;       self.title_hidden = False

        # Footnote Settings Here, print_fancy_message
        self.footnote_align = Align.RIGHT;  self.footnote_indent = 2;         self.footnote_msg = "" # footnote_indent works with Align.JUSTIFY
        self.footnote_lines_body = 1;       self.footnote_strike = False
        self.footnote_bg = 4;               self.footnote_fg = 231;           self.footnote_bold  = False
        self.footnote_dim = False;          self.footnote_italic = False;     self.footnote_underline = False
        self.footnote_blinking = False;     self.footnote_inverse = False;    self.footnote_hidden = False


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Get Message Attributes                                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def get_msg_attributes(self,data:str="Message",all_attribute:bool=False):
        '''
            getting the attributes from the message
        '''
        msg = str(data)
        tncols, tnrows = os.get_terminal_size()

        space_available = tncols - self.left_indent - self.right_indent

        longest_line   = 0;                       quotient = 0
        letter_counter = 0;                       residue  = 0
        msg_type       = "single_line";           new_msg  = ""


        quotient_number_letter_line_list = [];    fit_number_letter_line_list   = []
        residue_number_letter_line_list  = [];    carry_number_letter_line_list = []

        adj_diff_space     = [];                  number_letter_line_list = []
        result_multi_lines = []


        for l in msg:
            if l=="\n":
                number_letter_line_list.append(letter_counter)
                letter_counter = 0
                msg_type="multiple_lines"

            else:
                new_msg += l
                letter_counter += 1


        if msg_type == "single_line":
            quotient = int(letter_counter/space_available)
            residue  = letter_counter%space_available
            while quotient>0:
                number_letter_line_list.append(space_available)
                quotient -= 1
            number_letter_line_list.append(residue)

            for n in number_letter_line_list:
                adj_diff_space.append(space_available - n)


        else:   # multiple lines
            number_letter_line_list.append(letter_counter) # the last one not added
            longest_line = max(number_letter_line_list)
            # first item when only enter it's deleted
            if number_letter_line_list[0] == 0:  number_letter_line_list.pop(0)
            # last item when only enter it's deleted
            if number_letter_line_list[(len(number_letter_line_list))-1] == 0:
                number_letter_line_list.pop((len(number_letter_line_list))-1)

            if space_available > longest_line:
                for n in number_letter_line_list:
                    adj_diff_space.append(space_available-n)

            else:
                for line in range(len(number_letter_line_list)):
                    if number_letter_line_list[line] <= space_available:
                        fit_number_letter_line_list.append(number_letter_line_list[line])

                    else:
                        quotient = int(number_letter_line_list[line]/space_available)
                        residue  = number_letter_line_list[line]%space_available
                        n = quotient

                        while n > 0:
                            quotient_number_letter_line_list.append(space_available)
                            n -= 1

                        residue_number_letter_line_list.append(residue)
                        carry_number_letter_line_list.append(quotient+1)

                ctrl = 0
                for r in number_letter_line_list:
                    if r > space_available:
                        last_one = carry_number_letter_line_list[ctrl] - 1

                        for n in range(carry_number_letter_line_list[ctrl]):
                            if last_one == n:
                                result_multi_lines.append(residue_number_letter_line_list[ctrl])
                                ctrl += 1
                            else:
                                result_multi_lines.append(space_available)
                    else:
                        result_multi_lines.append(r)


                number_letter_line_list = result_multi_lines

                for n in number_letter_line_list:
                    adj_diff_space.append(space_available - n)

        if all_attribute == True:
            return tnrows, tncols, space_available, number_letter_line_list, adj_diff_space, new_msg, len(number_letter_line_list)

        else:
            return len(number_letter_line_list), space_available, tncols


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Send the Data To the Terminal                                                                                                                  -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def send_msg_terminal(self,data="Message"):
        '''
            printing the message
        '''
        def print_bg_lines(lines, bg_format_line_color="\033[0m"):
            if lines == 0:
                print("\033[0m",end="")
            else:
                n = lines
                while n>0:
                    print(bg_format_line_color)
                    n -= 1

        tnrows, tncols, space_available, number_letter_line_list, adj_diff_space, new_msg, n_lines = FancyMessage.get_msg_attributes(self,data,True)

        color = set_font(self.body_bold, self.body_bg, self.body_fg, self.body_italic, self.body_underline, self.body_strike,
                         self.body_blinking, self.body_dim, self.body_hidden, self.body_inverse)
        color2= set_font(bg=self.body_bg, fg=self.body_fg, inverse=self.body_inverse)

        # from here we need: tncols, space_available, number_letter_line_list, adj_diff_space, new_msg
        longest_line = max(number_letter_line_list)

        # self.adj_bg_lines_to_right_indent by default  = False
        # self.adj_bg_msg_to_space_available by default = False

        if self.length == Length_bg.ALL_ROW:
            bg_format_line_color = f"{color2}{ins_chr(tncols)}{reset_font()}"
            # change color for color2 to delete at the beginning the strike, and/or underline option(s)
            start_line = f"{color2}{ins_chr(self.left_indent)}"

        elif self.length == Length_bg.ONLY_WORD:
            if self.adj_bg_lines_to_right_indent == True:
                bg_format_line_color = f"{color2}{move_cursor_right(self.left_indent)}{ins_chr(space_available)}{reset_font()}"  # change color for color2

            else:  # elif (self.adj_bg_lines_to_right_indent == False):
                bg_format_line_color = f"{move_cursor_right(self.left_indent)}{color2}{ins_chr(longest_line)}{reset_font()}"     # change color for color2

            start_line = f"{move_cursor_right(self.left_indent)}{color2}"                                                        # change color for color2

        else: pass

        carry = 0; last_one = n_lines - 1
        print_bg_lines(self.top_lines, bg_format_line_color)       # bg_line

        print(start_line,end="")

        # start printing the message
        for nl in range(n_lines):
            for n in range(number_letter_line_list[nl]):
                print(f"{color}{new_msg[carry+n]}",end="")          # added color because the color2 can be slightly different

            carry += number_letter_line_list[nl]

            if self.length == Length_bg.ALL_ROW:
                for n in range(adj_diff_space[nl]+self.right_indent):
                    print(color2+" ",end="")                        # to delete at the end the strike, and/or underline option(s)

            elif self.length == Length_bg.ONLY_WORD:
                if self.adj_bg_msg_to_space_available == True:
                    for n in range(space_available -  number_letter_line_list[nl]):
                        print(color2+" ",end="")                    # to delete the strike we add color2
                else:                                               # elif (self.adj_bg_msg_to_space_available == False):
                    for n in range(longest_line-number_letter_line_list[nl]):
                        print(color2+" ",end="")

                print(f"{reset_font()}",end="")

            else:  pass

            print()
            if last_one == nl: pass
            else:                print(start_line,end="")

        # end printing the message
        print_bg_lines(self.bottom_lines, bg_format_line_color)    # bg_line


    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Print Fancy Note                                                                                                                                 -
    #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def print_fancy_note(self, body_msg:str="")->None:
        '''
            It prints the fancy note with the attributes defined
        '''

        if body_msg == "":  body_msg = self.body_msg

        # save original values
        li_obj = self.left_indent

        # settings for the body_msg
        if self.note_msg == "":  len_note_msg = 0
        else:                      len_note_msg = len(self.note_msg)

        self.left_indent = self.note_left_space + len_note_msg + self.note_right_space
        n_lines, space_available, tncols = self.get_msg_attributes(body_msg, False)

        total_back_lines = self.top_lines + n_lines + self.bottom_lines
        if   self.note_position >= (total_back_lines): lines_back = 0
        elif self.note_position <= 0:                  lines_back = total_back_lines
        else:                                          lines_back = total_back_lines - self.note_position

        self.send_msg_terminal(body_msg)

        # settings for the note
        settings_note = set_font(bold=self.note_bold, bg=self.note_bg, fg=self.note_fg, italic=self.note_italic,\
                                 underline=self.note_underline, strike=self.note_strike, blinking=self.note_blinking,\
                                 dim=self.note_dim, hidden=self.note_hidden, inverse=self.note_inverse)

        if self.note_align == Align.LEFT or self.note_align == "l":
            print(f"{self.moveTo(qty=lines_back, direction=Move.UP)}{settings_note}{self.note_msg}",end="")

        elif self.note_align == Align.CENTER or self.note_align == "c":
            myq = int((self.note_left_space+self.note_right_space)/2)
            print(f"{self.moveTo(qty=lines_back, direction=Move.UP)}{self.moveTo(myq, Move.RIGHT)}{settings_note}{self.note_msg}",end="")

        elif self.note_align == Align.RIGHT or self.note_align == "r":
            myq = self.note_left_space + self.note_right_space
            print(f"{self.moveTo(lines_back, Move.UP)}{self.moveTo(myq, Move.RIGHT)}{settings_note}{self.note_msg}",end="")

        else:  # JUSTIFY
            print(f"{self.moveTo(lines_back, Move.UP)}{self.moveTo(self.note_left_space, Move.RIGHT)}{settings_note}{self.note_msg}")

        self.jumpTo(qty=lines_back-1, direction=Move.DOWN)
        print(f"{reset_font()}",end="")

        # putting back original values
        self.left_indent = li_obj
        # n_lines, space_available, tncols are variables for reference to calculate the message
        if self.help_lines == True:
            print(f"{ins_chr(self.left_indent)}Body_Lines:{n_lines}  Space_Available:{space_available}  N.Cols: {tncols}N.Lines:{total_back_lines}")


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Print Fancy Message                                                                                                                            -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def print_fancy_message(self, body_msg:str="")->None:

        '''  It prints the fancy message with the attributes defined  '''

        if body_msg == "":  body_msg = self.body_msg

        # save original values
        li_obj = self.left_indent;      bold_obj    = self.body_bold;            blinking_obj  = self.body_blinking
        tl_obj = self.top_lines;        italic_obj  = self.body_italic;          underline_ojb = self.body_underline
        bg_obj = self.body_bg;          strike_obj  = self.body_strike;          fnm_obj       = self.footnote_msg
        fg_obj = self.body_fg;          hidden_obj  = self.body_hidden;          dim_obj       = self.body_dim
        bl_obj = self.bottom_lines;     inverse_obj = self.body_inverse
        ti_obj = self.title_msg

        n_lines, space_available, tncols = self.get_msg_attributes(body_msg)  # settings for title

        #---------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------------------------------------------------------
        if not self.title_msg == "":
            # working with the font color
            self.body_bg     = self.title_bg;          self.body_underline = self.title_underline
            self.body_fg     = self.title_fg;          self.body_blinking  = self.title_blinking
            self.body_bold   = self.title_bold;        self.body_inverse   = self.title_inverse
            self.body_dim    = self.title_dim;         self.body_hidden    = self.title_hidden
            self.body_italic = self.title_italic;      self.body_strike    = self.title_strike

            if   self.title_align == Align.LEFT or self.title_align == "l":  pass

            elif self.title_align == Align.CENTER or self.title_align == "c":
                sp = int((space_available - len(self.title_msg))/2)
                self.title_msg = ins_chr(sp) + self.title_msg

            elif self.title_align == Align.RIGHT or self.title_align == "r":
                sp = space_available - len(self.title_msg) # 1 for not jumping line and finished
                self.title_msg = ins_chr(sp) + self.title_msg

            else:                                          # Align.JUSTIFY
                self.title_msg = ins_chr(self.title_indent) + self.title_msg

            self.bottom_lines = self.lines_title_body
            self.send_msg_terminal(self.title_msg)

            # This is necessary because when is right alignment, it jumps automatically to the next row
            if (self.title_align == Align.RIGHT and self.title_msg != ""):
                print("\033[1A",end="")
                print(f"{ins_chr(tncols)}")
                print("\033[1A",end="")

            # settings for body (we recovered left_indent, and change bottom_lines and change top_lines)
            if not self.footnote_msg == "":  self.bottom_lines = 0
            else:                            self.bottom_lines = bl_obj

            self.left_indent = li_obj
            self.body_bg     = bg_obj;          self.body_underline = underline_ojb
            self.body_fg     = fg_obj;          self.body_blinking  = blinking_obj
            self.body_bold   = bold_obj;        self.body_inverse   = inverse_obj
            self.body_dim    = dim_obj;         self.body_hidden    = hidden_obj
            self.body_italic = italic_obj;      self.body_strike    = strike_obj

            if not self.title_msg == "":  self.top_lines = 0
            else:                         self.top_lines = tl_obj

            self.body_fg = fg_obj  # returning the color for the body
            self.send_msg_terminal(body_msg)

        else:
            if not self.footnote_msg == "":   self.bottom_lines = self.footnote_lines_body
            else:                             self.bottom_lines = bl_obj

            self.send_msg_terminal(body_msg)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------------------------------------------------------
        if not self.footnote_msg == "":
            if   self.footnote_align == Align.LEFT or self.footnote_align == "l":  pass

            elif self.footnote_align == Align.CENTER or self.footnote_align == "c":
                sp = int((space_available - len(self.footnote_msg))/2)
                self.footnote_msg = ins_chr(sp) + self.footnote_msg

            elif self.footnote_align == Align.RIGHT or self.footnote_align == "r":
                sp = space_available - len(self.footnote_msg) # 1 for not jumping line and finished
                self.footnote_msg = ins_chr(sp) + self.footnote_msg

            else:
                self.footnote_msg = ins_chr(self.footnote_indent) + self.footnote_msg # JUSTIFY

            self.top_lines    = self.footnote_lines_body;    self.bottom_lines   = bl_obj
            self.body_bg      = self.footnote_bg;            self.body_underline = self.footnote_underline
            self.body_fg      = self.footnote_fg;            self.body_blinking  = self.footnote_blinking
            self.body_bold    = self.footnote_bold;          self.body_inverse   = self.footnote_inverse
            self.body_dim     = self.footnote_dim;           self.body_hidden    = self.footnote_hidden
            self.body_italic  = self.footnote_italic;        self.body_strike    = self.footnote_strike

            self.send_msg_terminal(self.footnote_msg)

            # This is necessary because when is right alignment, it jumps automatically to the next row
            if self.footnote_align == Align.RIGHT and self.footnote_msg != "":
                print("\033[1A",end="")
                print(f"{ins_chr(tncols)}")
                print("\033[1A",end="")

        else:  pass

        # putting back original values
        self.top_lines    = tl_obj;            self.left_indent    = li_obj            #  self.bottom_lines = bl_obj
        self.body_bg      = bg_obj;            self.body_underline = underline_ojb
        self.body_fg      = fg_obj;            self.body_blinking  = blinking_obj
        self.body_bold    = bold_obj;          self.body_inverse   = inverse_obj
        self.body_dim     = dim_obj;           self.body_hidden    = hidden_obj
        self.body_italic  = italic_obj;        self.body_strike    = strike_obj
        self.footnote_msg = fnm_obj;           self.title_msg      = ti_obj

        # n_lines, space_available, tncols are variables for reference to calculate the message
        if self.help_lines == True:
            total_lines = n_lines + self.top_lines + self.bottom_lines

            if self.title_msg != "":     total_lines += 1 + self.lines_title_body

            if self.footnote_msg != "":  total_lines += 1 + self.footnote_lines_body

            print(f"{ins_chr(self.left_indent)}Body_Lines:{n_lines}  Space_Available:{space_available}  N.Cols: {tncols}  N.Lines:{total_lines}")


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Get Message Attributes                                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def get_message_attributes(self, body_msg:str="", print_attributes=True)->list:
        '''
        It returns the attributes of the message
        '''
        tnrows, tncols, space_available, number_letter_line_list, adj_diff_space, new_msg_list, n_lines =\
                                                                                                FancyMessage.get_msg_attributes(self,body_msg,True)

        if body_msg == "":  body_msg = self.body_msg

        smallest_line = min(number_letter_line_list)
        longest_line  = max(number_letter_line_list)
        words = body_msg.split()
        counter_words = len(words)
        total_characters = sum(number_letter_line_list)
        screen_size_xy = [tncols,tnrows]

        result_lst  =  [["Attributes",                    "Values"],
                        ["Screen Size_xy",                screen_size_xy],
                        ["Left Indent",                   self.left_indent],
                        ["Right Indent",                  self.right_indent],
                        ["Space Available",               space_available],
                        ["Longest Line",                  longest_line],
                        ["Smallest Line",                 smallest_line],
                        ["List Line Lengths",             number_letter_line_list],
                        ["List Line Spaces",              adj_diff_space],
                        ["Words Into a List",             "\'words\'"],
                        ["Total Number of Lines",         n_lines],
                        ["Total Number of Words",         counter_words],
                        ["Total Number of Characters",    total_characters]]


        new_msg_list = [["Position","Word"]]
        cnt = 0
        for n in words:
            new_msg_list.append([cnt, n])
            cnt += 1

        if print_attributes == True:
            tbl = FancyFormat()
            # Title
            tbl.title_msg = "  get_message_attributes(message, True)  "
            tbl.title_align = Align.LEFT
            tbl.title_bold   = True;   tbl.title_bg = 231
            tbl.title_italic = True;   tbl.title_fg = 4
            # bg colors
            tbl.horizontal_line_bg = 4
            tbl.vertical_line_bg   = 4
            tbl.outer_corner_bg         = 4

            tbl.inner_corner_bg      = 4
            tbl.header_horizontal_line_bg = 4

            tbl.header_corner_bg = 4
            tbl.header_vertical_line_bg     = 4

            tbl.header_bg = 90
            tbl.header_fg = 231
            tbl.header_bold = True

            tbl.data_bg = 231
            tbl.data_fg = 0
            tbl.data_bold = True

            tbl.adj_top_margin = 2
            tbl.adj_indent = 4
            tbl.adj_space  = 4

            tbl.header_horizontal_line_on = True
            # tbl.horizontal_line_on = False
            tbl.middle_horizontal_line_on = False
            tbl.adj_bottom_margin = 1
            tbl.print_fancy_format(data=result_lst, style=Line_Style.SINGLE_SPACE)
            tbl.adj_top_margin = 1
            tbl.title_msg = "  Words of The Message Into a List  "
            tbl.print_fancy_format(new_msg_list)

        return result_lst, new_msg_list
