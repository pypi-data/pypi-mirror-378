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
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Class Draw Pictures Around The Terminal                                                                                                           --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
from custom_print.fancy_cursor import*
#from custom_print.ref_names import Move  # cursor already has Move
from custom_print.ref_names import Layout
from custom_print.ref_names import Line_Style
from custom_print.fancy_functions import ins_chr
from custom_print.fancy_functions import set_font
from custom_print.fancy_functions import reset_font
from custom_print.fancy_format import FancyFormat


class Pen(Cursor):                         # Inheritance the Cursor Class here.
    '''
    Pen class will draw lines nad squares
    '''
    def __init__(self):                    # Initializing Draw Class as self
        super().__init__()                 # Super Class to use all (vars and funs) from Cursor Class
                                           # with the Initialization Draw Class(self), ex. self.gotoxy(x,y)
        # General Section
        self.adj_indent = 0                # space from the terminal to the box
        self.draw_line_bold = False
        self.draw_line_bg = -1
        self.draw_line_fg = -1
        self.fill_color = False

        # Rectangle Section
        # Horizontal Line Section
        self.top_horizontal_line_chr = "-";      self.bottom_horizontal_line_chr = "-"
        # Vertical Line Section
        self.left_vertical_line_chr  = "|";      self.right_vertical_line_chr = "|"
        # Corner Section
        self.top_left_corner_chr     = "+";      self.top_right_corner_chr   = "+"
        self.bottom_right_corner_chr = "+";      self.bottom_left_corner_chr = "+"


    def draw_line(self, size=0, layout=Layout.HORIZONTAL, tail="\N{BLACK DIAMOND}", body="-", head="\N{BLACK DIAMOND}"):

        '''  It draws a line with the parameters specified

             draw_line(size=0, layout=Layout.HORIZONTAL,
             tail="\N{BLACK DIAMOND}", body="-", head="\N{BLACK DIAMOND}"  '''

        settings = set_font(self.draw_line_bold, self.draw_line_bg, self.draw_line_fg)

        if layout.lower() == "h" or layout.lower() == Layout.HORIZONTAL:
            self.jumpTo(qty = self.adj_indent, direction = Move.RIGHT)
            print(f"{settings}{tail}",end="")
            for n in range(size-2): print(body,end="")
            print(head,end="")
            reset_font()


        elif layout.lower() == "v" or layout.lower() == Layout.VERTICAL:
            self.jumpTo(qty = self.adj_indent, direction = Move.RIGHT)
            print(f"{settings}{tail}")
            for n in range(size-2): print(f"{self.moveTo(qty = self.adj_indent, direction = Move.RIGHT)}{body}")
            print(f"{self.moveTo(qty=self.adj_indent, direction=Move.RIGHT)}{head}")
            reset_font()

        else:  pass


    def draw_rectangle(self,length=3, width=3, style=Line_Style.DASH):

        '''  It draws a rectangle with the parameters specified
             draw_rectangle(self,length=3, width=3, style=Line_Style.DASH)  '''

        if length <= 2: length = 3   # length = largo, width = alto
        if width  <= 2: width  = 3

        #---------------------------------------------------------------------------------------------------------------
        # Refill bg Option For The Rectangle                                                                           -
        #---------------------------------------------------------------------------------------------------------------
        if self.fill_color == True:
            square = []

            sq_in = FancyFormat()
            # General
            sq_in.adj_indent = self.adj_indent
            sq_in.adj_space  = 0

            # Data section
            sq_in.data_bg = self.draw_line_bg
            sq_in.data_fg = self.draw_line_fg
            sq_in.data_all_cell_bg   = True

            # Horizontal Line Section
            sq_in.top_horizontal_line_chr    = self.top_horizontal_line_chr
            sq_in.bottom_horizontal_line_chr = self.bottom_horizontal_line_chr
            sq_in.top_horizontal_line_on     = True
            sq_in.bottom_horizontal_line_on  = True


            sq_in.horizontal_line_bold = self.draw_line_bold           # two values False and True (0 and 1)
            sq_in.horizontal_line_bg   = self.draw_line_bg             # values -1 to 255
            sq_in.horizontal_line_fg   = self.draw_line_fg             # values -1 to 255

            # Vertical Line Section
            sq_in.vertical_line_bold = self.draw_line_bold             # two values False and True (0 and 1)
            sq_in.vertical_line_bg   = self.draw_line_bg               # values -1 to 255
            sq_in.vertical_line_fg   = self.draw_line_fg               # values -1 to 255

            sq_in.left_vertical_line_chr  = self.left_vertical_line_chr
            sq_in.right_vertical_line_chr = self.right_vertical_line_chr

            # Corner Section
            sq_in.top_left_corner_chr     = self.top_left_corner_chr
            sq_in.top_right_corner_chr    = self.top_right_corner_chr
            sq_in.bottom_right_corner_chr = self.bottom_right_corner_chr
            sq_in.bottom_left_corner_chr  = self.bottom_left_corner_chr
            sq_in.all_corner_bold_chr = self.draw_line_bold       # two values False and True (0 and 1)
            sq_in.bg_corner_chr   = self.draw_line_bg         # values -1 to 255
            sq_in.fg_corner_chr   = self.draw_line_fg         # values -1 to 255

            # Line Under Header and Header Section
            sq_in.header_bg = self.draw_line_bg
            sq_in.header_fg = self.draw_line_fg

            sq_in.header_horizontal_line_on = False

            sq_in.header_all_cell_bg = True

            sq_in.header_vertical_line_bg_chr = self.draw_line_bg
            sq_in.header_vertical_line_fg_chr = self.draw_line_fg

            for n in range(width-2):
                square.append([ins_chr(length-2)])

            sq_in.print_fancy_format(square, style)

        #---------------------------------------------------------------------------------------------------------------
        # NO Refill bg Option For The Rectangle                                                                        -
        #---------------------------------------------------------------------------------------------------------------
        else:
            def print_horiz_sq_line(settings, indent, size, tail, body, head):
                self.jumpTo(qty = indent, direction = Move.RIGHT)
                print(f"{settings}{tail}",end="")
                for n in range(size-2): print(body,end="")
                print(head)
                reset_font()

            def print_vert_sq_line(settings, indent, size, tail, body, head):
                self.jumpTo(qty = indent, direction = Move.RIGHT)
                print(f"{settings}{tail}")
                for n in range(size-2): print(f"{self.moveTo(qty = indent, direction = Move.RIGHT)}{body}")
                print(f"{self.moveTo(qty=indent, direction=Move.RIGHT)}{head}")
                reset_font()


            if style.lower() == Line_Style.CUSTOMIZED: pass
            else:                                      # Backup all the default values
                # Horizontal Line Section
                thlc = self.top_horizontal_line_chr;    bhlc = self.bottom_horizontal_line_chr

                # Vertical Line Section
                lvlc = self.left_vertical_line_chr;     rvlc = self.right_vertical_line_chr

                # Corner Section
                tlcc = self.top_left_corner_chr;        trcc = self.top_right_corner_chr
                brcc = self.bottom_right_corner_chr;    blcc = self.bottom_left_corner_chr

                #---------------------------------------------------------------------------------------------------------------
                # start drwaing the rectangle                                                                                  -
                #---------------------------------------------------------------------------------------------------------------
                if style.lower() == Line_Style.SINGLE_LINE:

                    # Horizontal Line Section
                    self.top_horizontal_line_chr = "\u2500";      self.bottom_horizontal_line_chr="\u2500"

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u2502";      self.right_vertical_line_chr = "\u2502"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u250C";          self.top_right_corner_chr = "\u2510"
                    self.bottom_right_corner_chr="\u2518";        self.bottom_left_corner_chr="\u2514"


                elif style.lower() == Line_Style.SINGLE_BOLD:

                    # Horizontal Line Section
                    self.top_horizontal_line_chr = "\u2501";      self.bottom_horizontal_line_chr="\u2501"

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u2503";      self.right_vertical_line_chr = "\u2503"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u250F";          self.top_right_corner_chr = "\u2513"
                    self.bottom_right_corner_chr="\u251B";        self.bottom_left_corner_chr="\u2517"


                elif style.lower() == Line_Style.SINGLE_HEAVY:
                    # Horizontal Line Section
                    self.top_horizontal_line_chr = "\u2586";      self.bottom_horizontal_line_chr="\u2586"

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u2588";      self.right_vertical_line_chr = "\u2588"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u2586";          self.top_right_corner_chr = "\u2586"
                    self.bottom_right_corner_chr="\u2588";        self.bottom_left_corner_chr="\u2588"


                elif style.lower() == Line_Style.DOUBLE_LINE:
                    # Horizontal Line Section
                    self.top_horizontal_line_chr = "\u2550";      self.bottom_horizontal_line_chr="\u2550"

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u2551";      self.right_vertical_line_chr = "\u2551"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u2554";          self.top_right_corner_chr = "\u2557"
                    self.bottom_right_corner_chr="\u255D";        self.bottom_left_corner_chr="\u255A"


                elif style.lower() == Line_Style.SQ_BRACKETS:
                    # Horizontal Line Section
                    self.top_horizontal_line_chr = " ";           self.bottom_horizontal_line_chr=" "

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u2502";      self.right_vertical_line_chr = "\u2502"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u250C";          self.top_right_corner_chr = "\u2510"
                    self.bottom_right_corner_chr="\u2518";        self.bottom_left_corner_chr="\u2514"


                elif style.lower() == Line_Style.DASH:
                    # Horizontal Line Section
                    self.top_horizontal_line_chr = "\u002D";      self.bottom_horizontal_line_chr="\u002D"

                    # Vertical Line Section
                    self.left_vertical_line_chr  = "\u254E";      self.right_vertical_line_chr = "\u254E"

                    # Outside Corner Section
                    self.top_left_corner_chr = "\u002B";          self.top_right_corner_chr = "\u002B"
                    self.bottom_right_corner_chr="\u002B";        self.bottom_left_corner_chr="\u002B"


                elif style.lower() == Line_Style.NONE:
                    # Horizontal Line Section
                    self.top_horizontal_line_chr = " ";           self.bottom_horizontal_line_chr=" "

                    # Vertical Line Section
                    self.left_vertical_line_chr  = " ";           self.right_vertical_line_chr = " "

                    # Outside Corner Section
                    self.top_left_corner_chr = " ";               self.top_right_corner_chr = " "
                    self.bottom_right_corner_chr=" ";             self.bottom_left_corner_chr=" "

                else: pass
            #-------------------------------------------------------------------------------------------------------------------
            # def draw_rectangle(self,length=3, width=3, style=Line_Style.DASH):
            # def set_font(bold=False,bg=-1,fg=-1,italic=False,underline=False,strike=False,blinking=False,dim=False,hidden=False,inverse=False):
            settings = set_font(self.draw_line_bold, self.draw_line_bg, self.draw_line_fg)

            # top horizontal line
            tail = self.top_left_corner_chr
            body = self.top_horizontal_line_chr
            head = self.top_right_corner_chr
            print_horiz_sq_line(settings, self.adj_indent, length, tail, body, head)


            # left vertical line
            self.jumpTo(qty=1, direction=Move.UP)
            tail = self.top_left_corner_chr
            body = self.left_vertical_line_chr
            head = self.bottom_left_corner_chr
            print_vert_sq_line(settings, self.adj_indent, width, tail, body, head)


            # bottom horizontal line
            self.jumpTo(qty=1, direction=Move.UP)
            tail = self.bottom_left_corner_chr
            body = self.bottom_horizontal_line_chr
            head = self.bottom_right_corner_chr
            print_horiz_sq_line(settings, self.adj_indent, length, tail, body, head)


            # right vertical line
            self.jumpTo(qty=width,  direction=Move.UP)
            tail = self.top_right_corner_chr
            body = self.right_vertical_line_chr
            head = self.bottom_right_corner_chr
            print_vert_sq_line(settings, (length+self.adj_indent-1), width, tail, body, head)


            if style == Line_Style.CUSTOMIZED: pass
            else:
                # putting back all the default values
                # Horizontal Line Section
                self.top_horizontal_line_chr = thlc;    self.bottom_horizontal_line_chr = bhlc

                # Vertical Line Section
                self.left_vertical_line_chr = lvlc;     self.right_vertical_line_chr = rvlc

                # Corner Section
                self.top_left_corner_chr = tlcc;        self.top_right_corner_chr = trcc
                self.bottom_right_corner_chr = brcc;    self.bottom_left_corner_chr = blcc
            #-----------------------------------------------------------------------------------------------------------------------------------------
