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

#--------------------------------------------------------------------------------------------------
# Fancy Separator                                                                                 -
#--------------------------------------------------------------------------------------------------
from custom_print.ref_names import Align
from custom_print.ref_names import Divider_Style

from custom_print.fancy_functions import ins_chr
from custom_print.fancy_functions import set_font
from custom_print.fancy_functions import reset_font
from custom_print.fancy_functions import dimensions


def get_final_top_bottom_corner_colors(self):
    '''
        it will get the final corner colors for top and bottom 
    '''
    #-----------------------------------------------------------------------------------------------------+
    #  Creating all the the CORNER colors                                                                 |
    #-----------------------------------------------------------------------------------------------------+
    if self.all_corner_bg <= -1 or self.all_corner_bg >= 256:
        bg_tlc = self.top_left_corner_bg
        bg_trc = self.top_right_corner_bg
        bg_blc = self.bottom_left_corner_bg
        bg_brc = self.bottom_right_corner_bg
    else:
        bg_tlc =self.all_corner_bg
        bg_trc =self.all_corner_bg
        bg_blc =self.all_corner_bg
        bg_brc =self.all_corner_bg

    if self.all_corner_fg <= -1 or self.all_corner_fg >= 256:
        fg_tlc = self.top_left_corner_fg
        fg_trc = self.top_right_corner_fg
        fg_blc = self.bottom_left_corner_fg
        fg_brc = self.bottom_right_corner_fg
    else:
        fg_tlc = self.all_corner_fg
        fg_trc = self.all_corner_fg
        fg_blc = self.all_corner_fg
        fg_brc = self.all_corner_fg


    bg_fg_ltc = set_font(self.all_corner_bold, bg_tlc, fg_tlc)
    bg_fg_rtc = set_font(self.all_corner_bold, bg_trc, fg_trc)

    bg_fg_lbc = set_font(self.all_corner_bold, bg_blc, fg_blc)
    bg_fg_rbc = set_font(self.all_corner_bold, bg_brc, fg_brc)

    return bg_fg_ltc, bg_fg_rtc, bg_fg_lbc, bg_fg_rbc



def get_final_line_colors(self):
    '''
        it will get the final color for the line
    '''
    #-----------------------------------------------------------------------------------------------------+
    #  Creating all the HORIZONTAL LINES colors                                                           |
    #-----------------------------------------------------------------------------------------------------+
    bg_fg_thl = set_font(self.horizontal_line_bold, self.top_horizontal_line_bg,    self.top_horizontal_line_fg)
    bg_fg_bhl = set_font(self.horizontal_line_bold, self.bottom_horizontal_line_bg, self.bottom_horizontal_line_fg)

    #-----------------------------------------------------------------------------------------------------+
    #  Creating all the VERTICAL LINES                                                                    |
    #-----------------------------------------------------------------------------------------------------+
    bg_fg_lvl  = set_font(self.vertical_line_bold, self.left_vertical_line_bg,   self.left_vertical_line_fg)
    bg_fg_rvl  = set_font(self.vertical_line_bold, self.right_vertical_line_bg,  self.right_vertical_line_fg)

    return bg_fg_thl, bg_fg_bhl, bg_fg_lvl, bg_fg_rvl



def get_fill_colors(self):
    '''
        it will get the final color for the fill
    '''
    #-----------------------------------------------------------------------------------------------------+
    #  Creating all the variables for the Fill color                                                      |
    #-----------------------------------------------------------------------------------------------------+
    if self.all_fill_bg <= -1 or self.all_fill_bg >= 256:
        bg_lf = self.left_fill_bg
        bg_rf = self.right_fill_bg
    else:
        bg_lf = self.all_fill_bg
        bg_rf = self.all_fill_bg

    f_bg_lf = set_font(False, bg_lf)
    f_bg_rf = set_font(False, bg_rf)

    return f_bg_lf, f_bg_rf



def get_all_corner_chr(self):
    '''
        it picks which variables are activated
    '''
    #-----------------------------------------------------------------------------------------------------+
    #  Creating all the variables for the CORNER CHR                                                      |
    #-----------------------------------------------------------------------------------------------------+

    if self.all_corner_chr == "":
        chr_tlc = self.top_left_corner_chr
        chr_trc = self.top_right_corner_chr
        chr_blc = self.bottom_left_corner_chr
        chr_brc = self.bottom_right_corner_chr
    else:
        chr_tlc = self.all_corner_chr
        chr_trc = self.all_corner_chr
        chr_blc = self.all_corner_chr
        chr_brc = self.all_corner_chr

    return chr_tlc, chr_trc, chr_blc, chr_brc



class Divider:
    '''
        It create a divider through the terminal screen.
    '''
    def __init__(self):
        '''
            defining the variables
        '''
        #-----------------------------------------------------------------------------------------------------+
        #  Defining all the variables                                                                         |
        #-----------------------------------------------------------------------------------------------------+
        #  Defining all the corner variables
        self.top_left_corner_chr     = " ";       self.top_left_corner_bg     = -1;       self.top_left_corner_fg     = -1
        self.top_right_corner_chr    = " ";       self.top_right_corner_bg    = -1;       self.top_right_corner_fg    = -1
        self.bottom_left_corner_chr  = " ";       self.bottom_left_corner_bg  = -1;       self.bottom_left_corner_fg  = -1
        self.bottom_right_corner_chr = " ";       self.bottom_right_corner_bg = -1;       self.bottom_right_corner_fg = -1

        self.all_corner_chr  = "";                self.all_corner_bg = -1;                self.all_corner_fg = -1
        self.all_corner_bold = False

        # Defining all the horizontal lines
        self.top_horizontal_line_chr    = " ";    self.top_horizontal_line_bg    = -1;    self.top_horizontal_line_fg    = -1
        self.bottom_horizontal_line_chr = " ";    self.bottom_horizontal_line_bg = -1;    self.bottom_horizontal_line_fg = -1
        self.top_horizontal_line_on     = True;   self.bottom_horizontal_line_on = True;  self.horizontal_line_bold      = False

        # Defining all the vertical lines
        self.left_vertical_line_chr  = " ";      self.left_vertical_line_bg  = -1;        self.left_vertical_line_fg  = -1
        self.right_vertical_line_chr = " ";      self.right_vertical_line_bg = -1;        self.right_vertical_line_fg = -1
        self.vertical_line_bold      = False

        # Data
        self.msg_bold = False;                   self.msg_bg = -1;                        self.msg_fg = -1
        self.adj_indent = 2;                     self.msg_align = Align.CENTER

        # Fill blank
        self.left_fill_bg = -1;                  self.right_fill_bg = -1;                  self.all_fill_bg = -1



    def print_fancy_divider(self, message=" Custom_Print_Divider ", style=Divider_Style.CUSTOMIZED):
        '''
            it prints the divider with all the attributes
        '''
        msg = str(message)
        cols, rows = dimensions()
        if style == Divider_Style.CUSTOMIZED or style == Divider_Style.BLUE_WHITE_1 or style == Divider_Style.BLUE_WHITE_2:
            sp = int((cols - len(msg))-len(self.left_vertical_line_chr)+1-len(self.right_vertical_line_chr)+1)
        else:
            sp = int((cols - len(msg)))

        data = set_font(self.msg_bold, self.msg_bg, self.msg_fg) + msg

        if sp % 2 == 0:
            # print("even ", sp)
            rsp = (sp)/2 - 1
            lsp = (sp)/2 - 1
        else:
            # print("odd ", sp)
            rsp = (int((sp)/2)) - 2
            lsp = (int((sp)/2)) + 1

        if cols <= (self.adj_indent + len(msg)):  self.adj_indent = 2


        #-----------------------------------------------------------------------------------------------------+
        #  Selecting the Design                                                                               |
        #-----------------------------------------------------------------------------------------------------+
        if style == Divider_Style.CUSTOMIZED:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)
            chr_tlc,     chr_trc,    chr_blc,  chr_brc  = get_all_corner_chr(self)

            #-------------------------------------------------------------------------------------------------+
            #  Making the Final chr for the divider Design                                                    |
            #-------------------------------------------------------------------------------------------------+
            if self.all_corner_chr != "":
                qty = cols-(2*(len(self.all_corner_chr)))

                division = int(qty/(len(self.top_horizontal_line_chr)))
                residuo = qty%(len(self.top_horizontal_line_chr))
                fill_chr = ""
                for n in range(residuo): fill_chr += self.top_horizontal_line_chr[n]
                final_chr_thl = bgfg_tlc + chr_tlc + bgfg_thl + ins_chr(division, self.top_horizontal_line_chr) + fill_chr + bgfg_trc + chr_trc


                division = int(qty/(len(self.bottom_horizontal_line_chr)))
                residuo = qty%(len(self.bottom_horizontal_line_chr))
                fill_chr = ""
                for n in range(residuo): fill_chr += self.bottom_horizontal_line_chr[n]
                final_chr_bhl = bgfg_blc + chr_blc + bgfg_bhl + ins_chr(division, self.bottom_horizontal_line_chr) + fill_chr + bgfg_brc + chr_brc

            else:
                qty = cols-len(self.top_left_corner_chr)-len(self.top_right_corner_chr)
                division = int(qty/(len(self.top_horizontal_line_chr)))
                residuo = qty%(len(self.top_horizontal_line_chr))
                fill_chr = ""
                for n in range(residuo): fill_chr += self.top_horizontal_line_chr[n]
                final_chr_thl = bgfg_tlc + chr_tlc + bgfg_thl +\
                                ins_chr(division, self.top_horizontal_line_chr) + fill_chr + bgfg_trc + chr_trc


                qty = cols-len(self.bottom_left_corner_chr)-len(self.bottom_right_corner_chr)
                division = int(qty/(len(self.bottom_horizontal_line_chr)))
                residuo = qty%(len(self.bottom_horizontal_line_chr))
                fill_chr = ""
                for n in range(residuo): fill_chr += self.top_horizontal_line_chr[n]
                final_chr_bhl = bgfg_blc + chr_blc + bgfg_bhl +\
                                ins_chr(division, self.bottom_horizontal_line_chr) + fill_chr + bgfg_brc + chr_brc


            final_chr_lvl = bgfg_lvl + self.left_vertical_line_chr
            final_chr_rvl = bgfg_rvl + self.right_vertical_line_chr




        elif style == Divider_Style.SINGLE_LINE:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "\u250C" + bgfg_thl + ins_chr(cols-2, "\u2500") +\
                            bgfg_trc + "\u2510"
            final_chr_bhl = bgfg_blc + "\u2514" + bgfg_bhl + ins_chr(cols-2, "\u2500") +\
                            bgfg_brc + "\u2518"

            final_chr_lvl = bgfg_lvl + "\u2502"
            final_chr_rvl = bgfg_rvl + "\u2502"

        elif style == Divider_Style.SINGLE_BOLD:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "\u250F" + bgfg_thl + ins_chr(cols-2, "\u2501") +\
                            bgfg_trc + "\u2513"
            final_chr_bhl = bgfg_blc + "\u2517" + bgfg_bhl + ins_chr(cols-2, "\u2501") +\
                            bgfg_brc + "\u251B"

            final_chr_lvl = bgfg_lvl + "\u2503"
            final_chr_rvl = bgfg_rvl + "\u2503"

        elif style == Divider_Style.SINGLE_HEAVY:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "\u2588" + bgfg_thl + ins_chr(cols-2, "\u2588") +\
                            bgfg_trc + "\u2588"
            final_chr_bhl = bgfg_blc + "\u2588" + bgfg_bhl + ins_chr(cols-2, "\u2588") +\
                            bgfg_brc + "\u2588"

            final_chr_lvl = bgfg_lvl + "\u2588"
            final_chr_rvl = bgfg_rvl + "\u2588"


        elif style == Divider_Style.DOUBLE_LINE:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "\u2554" + bgfg_thl + ins_chr(cols-2, "\u2550") +\
                            bgfg_trc + "\u2557"
            final_chr_bhl = bgfg_blc + "\u255A" + bgfg_bhl + ins_chr(cols-2, "\u2550") +\
                            bgfg_brc + "\u255D"

            final_chr_lvl = bgfg_lvl + "\u2551"
            final_chr_rvl = bgfg_rvl + "\u2551"


        elif style == Divider_Style.DASH_1:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "-" + bgfg_thl + ins_chr(cols-2, "-") +\
                            bgfg_trc + "-"
            final_chr_bhl = bgfg_blc + "-" + bgfg_bhl + ins_chr(cols-2, "-") +\
                            bgfg_brc + "-"

            final_chr_lvl = bgfg_lvl + "-"
            final_chr_rvl = bgfg_rvl + "-"


        elif style == Divider_Style.DASH_2:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "+" + bgfg_thl + ins_chr(cols-2, "-") +\
                            bgfg_trc + "+"
            final_chr_bhl = bgfg_blc + "+" + bgfg_bhl + ins_chr(cols-2, "-") +\
                            bgfg_brc + "+"

            final_chr_lvl = bgfg_lvl + "|"
            final_chr_rvl = bgfg_rvl + "|"


        elif style == Divider_Style.SQ_BRACKETS:
            bgfg_tlc,    bgfg_trc,   bgfg_blc, bgfg_brc = get_final_top_bottom_corner_colors(self)
            bgfg_thl,    bgfg_bhl,   bgfg_lvl, bgfg_rvl = get_final_line_colors(self)
            bg_lf,       bg_rf                          = get_fill_colors(self)

            final_chr_thl = bgfg_tlc + "\u259B" + bgfg_thl + ins_chr(cols-2, " ") +\
                            bgfg_trc + "\u259C"
            final_chr_bhl = bgfg_blc + "\u2599" + bgfg_bhl + ins_chr(cols-2, " ") +\
                            bgfg_brc + "\u259F"

            final_chr_lvl = bgfg_lvl + "\u258C"
            final_chr_rvl = bgfg_rvl + "\u2590"


        elif style == Divider_Style.BLUE_WHITE_2:
            # get_final_top_bottom_corner_colors
            frame_cololor = 4
            bgfg_tlc = set_font(True,frame_cololor);            bgfg_trc = set_font(True,frame_cololor)
            bgfg_blc = set_font(True,frame_cololor);            bgfg_brc = set_font(True,frame_cololor)

            # get_final_line_colors(self)
            bgfg_thl = set_font(True, frame_cololor);          bgfg_bhl = set_font(True, frame_cololor)
            bgfg_lvl = set_font(True, frame_cololor);          bgfg_rvl = set_font(True, frame_cololor)

            # get_fill_colors(self)
            bg_lf = set_font(True, 231)
            bg_rf = set_font(True, 231)

            data = set_font(self.msg_bold, frame_cololor, 231) + msg

            final_chr_thl = bgfg_tlc + " " + bgfg_thl + ins_chr(cols-2, " ") +\
                            bgfg_trc + " "
            final_chr_bhl = bgfg_blc + " " + bgfg_bhl + ins_chr(cols-2, " ") +\
                            bgfg_brc + " "

            final_chr_lvl = bgfg_lvl + self.left_vertical_line_chr
            final_chr_rvl = bgfg_rvl + self.right_vertical_line_chr

        elif style == Divider_Style.BLUE_WHITE_1:
            # get_final_top_bottom_corner_colors
            frame_cololor = 4
            bgfg_tlc = set_font(True,frame_cololor);            bgfg_trc = set_font(True,frame_cololor)
            bgfg_blc = set_font(True,frame_cololor);            bgfg_brc = set_font(True,frame_cololor)

            # get_final_line_colors(self)
            bgfg_thl = set_font(True, frame_cololor);          bgfg_bhl = set_font(True, frame_cololor)
            bgfg_lvl = set_font(True, frame_cololor);          bgfg_rvl = set_font(True, frame_cololor)

            # get_fill_colors(self)
            bg_lf = set_font(True, frame_cololor)
            bg_rf = set_font(True, frame_cololor)

            data = set_font(self.msg_bold, frame_cololor, 231) + msg

            final_chr_thl = bgfg_tlc + " " + bgfg_thl + ins_chr(cols-2, " ") +\
                            bgfg_trc + " "
            final_chr_bhl = bgfg_blc + " " + bgfg_bhl + ins_chr(cols-2, " ") +\
                            bgfg_brc + " "

            final_chr_lvl = bgfg_lvl + self.left_vertical_line_chr
            final_chr_rvl = bgfg_rvl + self.right_vertical_line_chr




        else:
            print(f"{set_font(True, 80, 234)} Style: \"{style}\" {set_font(True, 4,231)} Is NOT Recognized...!  {reset_font()}")
            print()
            return


        #-----------------------------------------------------------------------------------------------------+
        #  Printing the Top Horizontal Line                                                                   |
        #-----------------------------------------------------------------------------------------------------+
        if self.top_horizontal_line_on == True: print(f"{final_chr_thl}{reset_font()}")

        #-----------------------------------------------------------------------------------------------------+
        #  Printing the Message                                                                               |
        #-----------------------------------------------------------------------------------------------------+
        if (self.msg_align.lower() == Align.LEFT or self.msg_align.lower() == "l"):          # left    middle
            print(f"{final_chr_lvl}{data}{bg_rf}{ins_chr(lsp+rsp," ")}{final_chr_rvl}{reset_font()}")

        elif (self.msg_align.lower() == Align.CENTER or self.msg_align.lower() == "c"):      # center  middle
            print(f"{final_chr_lvl}{bg_lf}{ins_chr(lsp," ")}{data}{bg_rf}{ins_chr(rsp," ")}{final_chr_rvl}{reset_font()}")

        elif (self.msg_align.lower() == Align.RIGHT or self.msg_align.lower() == "r"):       # right   middle
            print(f"{final_chr_lvl}{bg_lf}{ins_chr(lsp+rsp," ")}{data}{final_chr_rvl}{reset_font()}")

        else:                                                                        # justify middle
            print(f"{final_chr_lvl}{bg_lf}{ins_chr(self.adj_indent," ")}{data}{bg_rf}{ins_chr(rsp+lsp-self.adj_indent," ")}{final_chr_rvl}{reset_font()}")
        #-----------------------------------------------------------------------------------------------------+
        #  Printing the Bottom Horizontal Line                                                                |
        #-----------------------------------------------------------------------------------------------------+
        if self.bottom_horizontal_line_on == True: print(f"{final_chr_bhl}{reset_font()}")
