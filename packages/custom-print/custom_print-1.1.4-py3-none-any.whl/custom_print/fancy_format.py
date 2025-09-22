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
from custom_print.fancy_functions import set_font
from custom_print.fancy_functions import reset_font
from custom_print.fancy_functions import ins_newline
from custom_print.fancy_functions import move_cursor_right
from custom_print.fancy_functions import get_list_type
from custom_print.ref_names import Layout
from custom_print.ref_names import Line_Style


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Fancy Format (Class, Methods and Fucntions)                                                                                                        -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Bool to List Type                                                                                                                     -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def bool2list(my_bool):

    '''  It Converts a Bool to a String List  '''

    tempo_list = []
    tempo_list.append(my_bool)
    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Integer to List Type                                                                                                                  -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def int2list(my_int):

    '''  It Converts a Integer Number to a String List n  '''

    tempo_list = []
    tempo_list.append(my_int)
    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Float to List Type                                                                                                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def float2list(my_float):

    '''  It Converts a Float Number to a String List  '''

    tempo_list = []
    tempo_list.append(my_float)
    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Complex to List Type                                                                                                                  -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def complex2list(my_complex):

    '''  It Converts a Complex Number to a String List  '''

    tempo_list = []
    tempo_list.append(my_complex)
    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From String to List Type                                                                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def str2list(my_str):

    '''  It Converts a String to a String List  '''

    tempo_list = []
    tempo_list.append(my_str)
    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Dict to List Type                                                                                                                     -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def dict2list(my_dict, layout:Layout=Layout.HORIZONTAL):

    '''  It Converts a Dictionay to a String List  '''

    my_key_list = []; my_data_list = []

    my_key_list  = list(my_dict.keys())
    my_data_list = list(my_dict.values())
    complete_list = [];  tempo_list = []


    for d in range(len(my_dict)):
        tempo_list.append(my_key_list[d])
        tempo_list.append(my_data_list[d])
        complete_list.append(tempo_list)
        tempo_list = []

    if layout == Layout.VERTICAL: pass

    else:
        transpose_list = []
        for c in range(len(complete_list[0])):
            tempo_list = []
            for r in range(len(complete_list)):
                tempo_list.append(complete_list[r][c])
            transpose_list.append(tempo_list)
        complete_list = transpose_list


    return complete_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Set or Frozenset to List Type                                                                                                         -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def set2list(my_set:set, set_header = "none", layout:Layout=Layout.HORIZONTAL):

    '''  It Converts a Set or a Frozenset to a String List  '''

    # set and frozenset values are printed in aleatory order all the time
    tempo_list = []; cnt = 0; l = len(my_set)

    if layout.lower() == "v" or layout.lower() == Layout.VERTICAL:
        if "set" in set_header or "frozenset" in set_header:
            if len(my_set) > 1:
                tempo_list.append([set_header+" Values"])
            else:
                tempo_list.append([set_header+" Value"])

        elif set_header == "none":
            pass

        else:
            tempo_list.append([set_header])

        while l > 0:
            dato = list(my_set)[cnt]
            tempo_list.append([dato])
            cnt += 1
            l   -= 1

    if layout.lower() == "h" or layout.lower() == Layout.HORIZONTAL:
        if "set" in set_header or "frozenset" in set_header:
            if len(my_set) > 1:
                tempo_list.append("Set Values")
            else:
                tempo_list.append("Set Value")

        elif set_header == "none":
            pass

        else:
            tempo_list.append(set_header)

        while l > 0:
            dato = list(my_set)[cnt]
            tempo_list.append(dato)
            cnt += 1
            l   -= 1

    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Range to List Type                                                                                                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def range2list(my_range:range, range_header = "none", layout:Layout=Layout.HORIZONTAL):

    '''  It Converts a Range to a String List  '''

    tempo_list = []

    if layout.lower() == "v" or layout.lower() == Layout.VERTICAL:
        if range_header   == "range": tempo_list = [["Range"]]
        elif range_header == "none":  pass
        else:                         tempo_list = [[range_header]]

        for n in my_range:
            tempo_list.append([n])

    if layout.lower() == "h" or layout.lower() == Layout.HORIZONTAL:
        if range_header   == "range": tempo_list = ["Range"]
        elif range_header == "none":  pass
        else:                         tempo_list = [range_header]

        for n in my_range:
            tempo_list.append(n)

    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Convert From Tuple to List Type                                                                                                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def tuple2list(my_tuple):

    '''  It Converts a Tuple to a String List  '''

    tempo_list = []
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    if len(my_tuple) == 0:
        pass #return tempo_list

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    elif len(my_tuple) == 1:
                                                # string              ("")         -> Case 0   String
                                                # "empty_tuple"       ("",)        -> Case 1   Empty
        tempo_list.append(my_tuple[0])          # "one_item_no_row"   ("Apple",)   -> Case 2   Tuple
        #return tempo_list                      # "one_item_one_row"  (("Apple",)) -> Case 3   Tuple inside Tuple

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    #elif len(my_tuple) > 1:
    else:
        type_type = []; lengths = []
        l = len(my_tuple); tuple_tuple = 0; tuple_other = 0

        for n in range(len(my_tuple)):
            if isinstance(my_tuple[n], tuple):
                tuple_tuple = 1
                type_type.append("tuple")
                lengths.append(len(my_tuple[n]))

            else:
                tuple_other = 1
                type_type.append("other")
                lengths.append(1)

        # This is only for tuples inside the tuple ->
        # tupleData = (("hello","hello"),("hell",),("hi","bye","good"),([1,2],))        -> Case 4
        if (tuple_tuple == 1 and tuple_other == 0):
            tempo = []
            for col in my_tuple:
                for i in col:
                    tempo.append(i)
                tempo_list.append(tempo)
                tempo = []

        # This is only for other types inside a tuple
        # tupleData = ("hello","hell","hi",[1,2])                                       -> Case 5
        elif (tuple_tuple == 0 and tuple_other == 1):
            for n in my_tuple:
                tempo_list.append(n)     # for rows (Horizontal)
                #tempo_list.append([n])  # for cols (Vertical)

        # This is for combination tuple (tuple =1 and other = 1)                        -> Case 6
        # tupleData = (("hello","hello"),("hell",),("hi","bye","good"),[1,2], "hello")
        elif (tuple_tuple == 1 and tuple_other == 1):
            for n in range(l):
                if (lengths[n]) > 1:
                    tempo = []
                    for i in range(lengths[n]):
                        tempo.append(my_tuple[n][i])
                    tempo_list.append(tempo)

                else:
                    if type_type[n] == "other":
                        tempo_list.append([my_tuple[n]])
                    else:
                        tempo_list.append([my_tuple[n][0]])
        else:
            tempo_list = []

    return tempo_list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Get Data Type and Convert It to a List Type                                                                                                        -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def data2list(self,dato):

    '''  It Converts Any Type of Variable to a a String List Type  '''

    data_list = []
    # it is already a list type
    if isinstance(dato, list):
        return dato

    # bool type to list type
    elif isinstance(dato, bool):
        data_list = bool2list(dato)

    # int to list type
    elif isinstance(dato, int):
        data_list = int2list(dato)

    # float to list type
    elif isinstance(dato, float):
        data_list = float2list(dato)

    # string type
    elif isinstance(dato, str):
        data_list = str2list(dato)

    # complex type
    elif isinstance(dato, complex):
        if dato.imag < 0:
            data_list.append(str(dato.real)+"-"+str((dato.imag)*-1)+"j")
        else:
            data_list.append(str(dato.real)+"+"+str(dato.imag)+"j")

    # range type
    elif isinstance(dato, range):
        data_list = range2list(dato,"none", self.set_layout)

    # dictionary type
    elif isinstance(dato, dict):
        data_list = dict2list(dato, self.set_layout)

    # set type
    elif isinstance(dato, set):
        data_list = set2list(dato,"none", self.set_layout)

    # frozenset type
    elif isinstance(dato, frozenset):
        data_list = set2list(dato,"none", self.set_layout)

    # tuple
    elif isinstance(dato, tuple):
        data_list = tuple2list(dato)

    else:
        data_list = "none"

    # none: bytes, bytearray, memoryview(bytes(5))

    return data_list


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Get Total Length of the Columns                                                                                                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def get_total_length(self,my_list):
    '''
        getting the length of the table
    '''
    my_length = 0
    list_dimensions = get_list_type(my_list)
    if list_dimensions == "one_item_no_row":     # ["item"]
        # the *2 is because there are 2 adj_space one each size (left and right)
        # the +2 is because there are 2 vertical lines (left and right)
        my_length = len(my_list[0]) + (self.adj_space*2) + self.adj_indent + 2

    elif list_dimensions == "one_item_one_row":  # [[item]]
        # the *2 is because there are 2 adj_space one each size (left and right)
        # the adj_indent is because we have an indentation space at the begining
        # the +2 is because there are 2 vertical lines (left and right)
        my_length = len(my_list[0][0]) + (self.adj_space*2) + self.adj_indent + 2

    elif (list_dimensions == "multiple_items_one_row" or list_dimensions == "multiple_items_no_row"):
        # [1,2,3,4,5]  or [[1,2,3,4,5]]
        for item in my_list:
            my_length += len(item) + (self.adj_space*2) + 1  # this one is for the left vertical chr
        my_length += 1                                       # this one is for the right vertical chr, last one
        my_length += self.adj_indent                         # this is for the indentation space

    else:    # multiples rows
        one_item_per_row = True

        for row in my_list:             # checking if we a list like [[1],[2],[3]], only one column
            if  len(row) != 1:
                one_item_per_row = False
                break

        if one_item_per_row == True:    # finding the greatest column size in characters
            for row in my_list:
                for col in row:
                    if my_length < len(col):
                        my_length = len(col)

            # the adj_indent is because we have an indentation space at the begining
            # the *2 is because there are 2 adj_space one each size (left and right), self.adj_space
            # the +2 is because there are 2 vertical lines (left and right)
            my_length += self.adj_indent + (self.adj_space*2) + 2

        else:
            # we have a matrix list something like this [[10,20,30],[40,50,60],[70,80,90]]. awsome.
            max_rows, max_cols = get_number_rows_cols_list(my_list)
            tempo_cols = []
            n_cols = []

            # we create the transpose of the list but we save their lens in the transpose rather than the data
            for c in range(max_cols):
                for r in range(max_rows):
                    tempo_cols.append(len(my_list[r][c]))
                n_cols.append(tempo_cols)
                tempo_cols = []

            longest_cols = []
            for col in n_cols:
                longest_cols.append(max(col)) # longest_cols keeps the size list of the longest columns in chr
                # making the complete sum of the all the length
                # the adj_indent is because we have an indentation space at the begining
                # sum(longest_cols) is suming all the longest cols in the list
                # the self.adj_space is multiply by 2 because we have to side, left and right, on each column then
                # we multiply by the number of columns in the list
                # the +1  is because there are 1 vertical lines no consiered in the list
                # of longest_cols (left, middles, and right)

            my_length = self.adj_indent + sum(longest_cols) + ((self.adj_space*2)*len(longest_cols)) + len(longest_cols) + 1

    return my_length



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Title On Terminal with Its Attributes: Bold, Bg and Fg Color (title)                                                                         -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_title(self,my_list):
    '''
        printing the title of the table
    '''

    if self.title_msg == "":  return

    else:
        settings = set_font(self.title_bold,self.title_bg, self.title_fg,self.title_italic,self.title_underline,
                            self.title_strike,self.title_blinking,self.title_dim,self.title_hidden,self.title_inverse)

    total_length = get_total_length(self,my_list)  # check for the length of the message

    if (self.title_align.lower() == "left") or (self.title_align.lower() == "l"):
        print(move_cursor_right(self.adj_indent)+settings+self.title_msg+reset_font())

    elif (self.title_align.lower() == "center") or (self.title_align.lower() == "c"):
        difference = (int((total_length)/2)) - (int(((len(self.title_msg) + self.adj_indent))/2))
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.title_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+difference)+settings+self.title_msg+reset_font())

    elif (self.title_align.lower() == "right") or (self.title_align.lower() == "r"):
        # the 1 is for the vertical line
        difference = total_length - (len(self.title_msg) + (self.adj_space) + self.adj_indent + 1)
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.title_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+self.adj_space+1+difference)+settings+self.title_msg+reset_font())

    elif (self.title_align.lower() == "justify") or (self.title_align.lower() == "j"):
        difference = total_length - (len(self.title_msg) + (self.adj_space) + self.adj_indent + 1)
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.title_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+self.adj_space+1)+settings+self.title_msg+reset_font())

    else:
        print(move_cursor_right(self.adj_indent)+settings+self.title_msg+reset_font())   # left align

    ins_newline(self.adj_top_space)    # space between the the title and the top list



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Footnote On Terminal with Its Attributes: Bold, Bg and Fg Color (footnote)                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_notefoot(self,my_list):
    '''
        printing the notefoot of the table
    '''

    if self.footnote_msg == "": return

    else:
        settings = set_font(self.footnote_bold,self.footnote_bg, self.footnote_fg,self.footnote_italic,self.footnote_underline,\
                            self.footnote_strike,self.footnote_blinking,self.footnote_dim,self.footnote_hidden,self.footnote_inverse)

    total_length = get_total_length(self,my_list)  # check for the length of the message

    ins_newline(self.adj_bottom_space)

    if (self.footnote_align.lower() == "left") or (self.footnote_align.lower() == "l"):
        print(move_cursor_right(self.adj_indent)+settings+self.footnote_msg+reset_font())

    elif (self.footnote_align.lower() == "center") or (self.footnote_align.lower() == "c"):
        difference = (int((total_length)/2)) - (int(((len(self.footnote_msg) + self.adj_indent))/2))
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.footnote_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+difference)+settings+self.footnote_msg+reset_font())

    elif (self.footnote_align.lower() == "right") or (self.footnote_align.lower() == "r"):
        difference = total_length - (len(self.footnote_msg) + (self.adj_space) + self.adj_indent + 1) # 1 is for the vertical line
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.footnote_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+self.adj_space+1+difference)+settings+self.footnote_msg+reset_font())

    elif (self.footnote_align.lower() == "justify") or (self.footnote_align.lower() == "j"):
        difference = total_length - (len(self.footnote_msg) + (self.adj_space) + self.adj_indent + 1)
        if difference <= 0:
            print(move_cursor_right(self.adj_indent)+settings+self.footnote_msg+reset_font()) # left align
        else:
            print(move_cursor_right(self.adj_indent+self.adj_space+1)+settings+self.footnote_msg+reset_font())

    else:
        print(move_cursor_right(self.adj_indent)+settings+self.footnote_msg+reset_font())   # left align



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Horizontal Line                                                                                                                              -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_horizontal_segment(self,start_chr,end_chr,times,indent,option):
    '''
        print the horizontal line by segment
    '''

    set_v   = set_font(self.vertical_line_bold, self.vertical_line_bg, self.vertical_line_fg)
    set_h   = set_font(self.horizontal_line_bold, self.horizontal_line_bg, self.horizontal_line_fg)
    set_c   = set_font(self.outer_corner_bold, self.outer_corner_bg, self.outer_corner_fg)
    set_hd  = set_font(self.header_horizontal_line_bold, self.header_horizontal_line_bg,self.header_horizontal_line_fg)
    set_hdc = set_font(self.header_corner_bold, self.header_corner_bg,self.header_corner_fg)
    set_ic  = set_font(self.inner_corner_bold, self.inner_corner_bg,self.inner_corner_fg)

    # indentation adds the space is set up for the indentation
    # we want the indentation space at the begining but not at the end of the line.

    if indent == 1:
        print(move_cursor_right(self.adj_indent),end="")

    if option == "horizontal":
        print(set_v+start_chr+set_h,end="")

    elif option == "corner":
        print(set_c+start_chr+set_h,end="")

    elif option == "horizontal_header":
        print(set_hdc+start_chr+set_hd,end="")

    elif option == "inner_corner":
        print(set_ic+start_chr+set_h,end="")

    else:
        print(set_v+start_chr+set_h,end="")

    for n in range(times):
        print(end_chr,end="")

    print(reset_font(),end="")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Single Element                                                                                                                               -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_single_element(self,my_list):
    '''
        print the table when it is a single element
    '''

    if isinstance(my_list[0],list): item = my_list[0][0]
    else:                           item = my_list[0]

    ins_newline(self.adj_top_margin)
    # print title
    print_title(self,my_list)

    # get all the settings for the list
    set_d = set_font(self.data_bold, self.data_bg, self.data_fg, self.data_italic, self.data_underline, self.data_strike,\
                     self.data_blinking, self.data_dim, self.data_hidden, self.data_inverse)
    set_v = set_font(self.vertical_line_bold, self.vertical_line_bg, self.vertical_line_fg)

    # print the top horizontal line
    if  self.top_horizontal_line_on == True:
        indent = 1  # to add the space at the beginning ()
        print_horizontal_segment(self, self.top_left_corner_chr, self.top_horizontal_line_chr, ((len(item))+(2*self.adj_space)), indent, "corner")

        indent = 0  # to don't add this space at the end or the middle
        print_horizontal_segment(self, self.top_right_corner_chr, self.top_horizontal_line_chr, 0, indent, "corner")
        print()
    else:
        pass

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # print data with adjustments. We are missing vertical line color and horizontal line color and data color
    if (self.data_align.lower() == "left") or (self.data_align.lower() == "l"):
        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + item + move_cursor_right((self.adj_space*2),\
                          self.data_all_cell_bg) + set_v + self.right_vertical_line_chr + reset_font())

    elif (self.data_align.lower() == "right") or (self.data_align.lower() == "r"):
        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + move_cursor_right((self.adj_space*2),\
                          self.data_all_cell_bg) + item + set_v + self.right_vertical_line_chr + reset_font())

    elif (self.data_align.lower() == "center") or (self.data_align.lower() == "c"):
        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + move_cursor_right(self.adj_space, self.data_all_cell_bg) +\
                          item + move_cursor_right(self.adj_space, self.data_all_cell_bg) + set_v + self.right_vertical_line_chr + reset_font())

    elif (self.data_align.lower() == "justify") or (self.data_align.lower() == "j"):
        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + move_cursor_right(self.adj_space, self.data_all_cell_bg) +\
                          item + move_cursor_right(self.adj_space, self.data_all_cell_bg) + set_v + self.right_vertical_line_chr + reset_font())

    else:
        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + move_cursor_right(self.adj_space, self.data_all_cell_bg)+\
                          item + move_cursor_right(self.adj_space, self.data_all_cell_bg) + set_v + self.right_vertical_line_chr + reset_font())

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # print the bottom horizontal line
    if  self.bottom_horizontal_line_on == 1:
        indent = 1  # to add the space at the beginning (vertical line chr)
        print_horizontal_segment(self, self.bottom_left_corner_chr, self.bottom_horizontal_line_chr, ((len(item))+(2*self.adj_space)), indent, "corner")
        indent = 0  # to don't add this space at the end or the middle
        print_horizontal_segment(self, self.bottom_right_corner_chr, self.bottom_horizontal_line_chr, 0, indent, "corner")
        print()

    else:  pass

    print_notefoot(self,my_list)
    ins_newline(self.adj_bottom_margin)



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Multiple Horizontal Items (One Row OR No Row)                                                                                                -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_multiple_horizontal_items(self,my_list):
    '''
        print the table when is a horizontal items only
    '''
    ins_newline(self.adj_top_margin)
    # print title
    print_title(self,my_list)

    # get all the settings for the list
    set_d = set_font(self.data_bold, self.data_bg, self.data_fg, self.data_italic, self.data_underline, self.data_strike,\
                     self.data_blinking, self.data_dim, self.data_hidden, self.data_inverse)

    set_v = set_font(self.vertical_line_bold, self.vertical_line_bg, self.vertical_line_fg)

    # drawing the top horizontal line
    if  self.top_horizontal_line_on == True:
        indent = 1  # to add the space at the beginning (indentation space)
        for item in my_list:
            if indent == 1:          # first segment
                print_horizontal_segment(self, self.top_left_corner_chr, self.top_horizontal_line_chr, (len(item) +\
                                         (2*self.adj_space)), indent, "corner")
                indent = 0
            else:
                print_horizontal_segment(self, self.middle_top_corner_chr, self.top_horizontal_line_chr,(len(item) +\
                                         (2*self.adj_space)), indent, "inner_corner")

                # corner or horizontal depends on what color to get if the corner colors or the horizontal_line
                # last segment, which is only the corner that's why it's 0 on value

        print_horizontal_segment(self, self.top_right_corner_chr, self.top_horizontal_line_chr, 0, indent, "corner")
        print()  # done top line, jump to next line to print data

    else:  pass

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # print the data with their alignments
    indent = 1
    for item in my_list:
        if (self.data_align.lower() == "left") or (self.data_align.lower() == "l"):
            if indent == 1:
                print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + item +\
                     move_cursor_right((self.adj_space*2),self.data_all_cell_bg),end="")
                indent = 0
            else:
                print(set_v + self.middle_vertical_line_chr + set_d + item + move_cursor_right((self.adj_space*2),self.data_all_cell_bg),end="")

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif (self.data_align.lower() == "right") or (self.data_align.lower() == "r"):
            if indent == 1:
                print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d+\
                     move_cursor_right((self.adj_space*2),self.data_all_cell_bg) + item,end="")
                indent = 0
            else:
                print(set_v + self.middle_vertical_line_chr + set_d + move_cursor_right((self.adj_space*2),self.data_all_cell_bg) + item,end="")

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif (self.data_align.lower() == "justify") or (self.data_align.lower() == "j")\
              or (self.data_align.lower() == "center") or (self.data_align.lower() == "c"):
            if indent == 1:
                print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d +\
                      move_cursor_right(self.adj_space,self.data_all_cell_bg) + item + move_cursor_right(self.adj_space,self.data_all_cell_bg),end="")
                indent = 0
            else:
                print(set_v + self.middle_vertical_line_chr + set_d+move_cursor_right(self.adj_space,self.data_all_cell_bg) + item +\
                     move_cursor_right(self.adj_space,self.data_all_cell_bg),end="")

        #---------------------------------------------------------------------------------------------------------------------------------------------
        else: # justify default one
            print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + move_cursor_right(self.adj_space,self.data_all_cell_bg) +\
                  item + move_cursor_right(self.adj_space,self.data_all_cell_bg),end="")

    print(set_v + self.right_vertical_line_chr + reset_font())

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # print the bottom horizontal line
    if  self.bottom_horizontal_line_on == 1:
        indent = 1
        for item in my_list:
            if indent == 1:
                print_horizontal_segment(self, self.bottom_left_corner_chr, self.bottom_horizontal_line_chr, (len(item) + (2*self.adj_space)),\
                                  indent, "corner") # first segment
                indent = 0

            else:  # middle segments. "corner"
                print_horizontal_segment(self, self.middle_bottom_corner_chr, self.bottom_horizontal_line_chr, (len(item) + (2*self.adj_space)),\
                                    indent, "inner_corner")

                # corner or horizontal depends on what color to get if the corner colors or the horizontal_line
                # last segment, which is only the corner that's why it's 0 on value

        print_horizontal_segment(self, self.bottom_right_corner_chr, self.bottom_horizontal_line_chr, 0, indent, "corner")
        print()

    print_notefoot(self,my_list)
    ins_newline(self.adj_bottom_margin)



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Get Number of Rows and Cols of the List                                                                                                            -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def get_number_rows_cols_list(my_list):
    '''
        getting the number of rows and cols from the list
    '''
    n_rows = len(my_list)
    n_cols = 0

    for n in my_list:
        if len(n) > n_cols:
            n_cols = len(n)

    return n_rows, n_cols



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Complete Information in the List, if need it                                                                                                       -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def complete_info_list(self,my_list):
    '''
        complete the list
    '''
    n_rows, n_cols = get_number_rows_cols_list(my_list)
    row_tempo_list = []; matrix_update = []

    for row in range(n_rows):
        row_tempo_list = my_list[row]
        diff = n_cols - len(my_list[row])
        for col in range(diff):
            row_tempo_list.append(str(self.set_fill_chr))
        matrix_update.append(row_tempo_list)

    return matrix_update



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Get the Odd or Even Space Adjustment for the Word                                                                                                  -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def get_odd_even_space_adj(length,len_dato):
    '''
        calculting the space for the type of alignment chosen
    '''
    sp_start = 0; sp_end=0
    odd_l = length%2
    odd_len_dato = len_dato%2

    if odd_l == 1:
        sp_start = (int(length/2))-(int(len_dato/2))       # if length word is odd
        if odd_len_dato == 1:  sp_end = sp_start           # if len_dato is odd
        else:                  sp_end = sp_start + 1       # if len_dato is even

    else:
        sp_start = (int(length/2))-(int(len_dato/2))       # if the length word is even
        if odd_len_dato == 1:  sp_end = sp_start - 1       # if len_dato is odd
        else:                  sp_end = sp_start           # if len_dato is even

    return sp_start, sp_end



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Print Matrix List                                                                                                                                  -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def print_matrix_list(self,my_list):
    '''
        printing the table 
    '''
    # d  :data,   v: vertical,   hcl: left_corner_header,   mch:middle_corner_header, rch:right_corner_header,   t:title(header)
    # get all the settings for the list

    set_d = set_font(self.data_bold, self.data_bg, self.data_fg,self.data_italic, self.data_underline, self.data_strike,\
                     self.data_blinking, self.data_dim, self.data_hidden, self.data_inverse)

    set_v = set_font(self.vertical_line_bold, self.vertical_line_bg, self.vertical_line_fg)

    set_hchr_v = set_font(self.header_vertical_line_bold, self.header_vertical_line_bg,self.header_vertical_line_fg)

    set_t = set_font(self.header_bold, self.header_bg, self.header_fg,self.header_italic,self.header_underline,self.header_strike,\
                     self.header_blinking,self.header_dim,self.header_hidden,self.header_inverse)

    total_length = get_total_length(self,my_list)

    ins_newline(self.adj_top_margin)
    # print title
    print_title(self,my_list)
    # this is the last part and we need to start printing the matrix
    if len(my_list[0]) == 1:
        # we are dealing with only one column
        #---------------------------------------------------------------------------------------------------------------------------------------------
        #print_horizontal_segment(self,start_chr,end_chr,times,indent,option)
        # item is the longest column
        length = total_length - (self.adj_indent + (self.adj_space*2) + 2) # length is the longest column length

        # print the top horizontal line
        if  self.top_horizontal_line_on == True:
            indent = 1  # to add the space at the beginning ()
            print_horizontal_segment(self, self.top_left_corner_chr, self.top_horizontal_line_chr, length + (2*self.adj_space), indent, "corner")
            indent = 0  # to don't add this space at the end or the middle
            print_horizontal_segment(self, self.top_right_corner_chr, self.top_horizontal_line_chr, 0, indent, "corner")
            print()

        else:  pass
            #-----------------------------------------------------------------------------------------------------------------------------------------
            # print data here
        ctrl_header = 0
        for row in my_list:
            for dato in row:
                if ctrl_header == 0:        # printing Header
                    ctrl_header += 1
                    if (self.header_align.lower() == "left") or (self.header_align.lower() == "l"):
                        print(move_cursor_right(self.adj_indent) + set_hchr_v + self.header_left_vertical_line_chr + set_t + dato +\
                              move_cursor_right((self.adj_space*2)+(length-len(dato)),self.header_all_cell_bg) + set_hchr_v +\
                              self.header_right_vertical_line_chr + reset_font(),end="")

                    elif (self.header_align.lower() == "right") or (self.header_align.lower() == "r"):
                        print(move_cursor_right(self.adj_indent) + set_hchr_v + self.header_left_vertical_line_chr + set_t +\
                              move_cursor_right((self.adj_space*2)+(length-len(dato)),self.header_all_cell_bg) + dato + set_hchr_v +\
                              self.header_right_vertical_line_chr + reset_font(),end="")

                    elif (self.header_align.lower() == "center") or (self.header_align.lower() == "c"):
                        # add the extra space for the word odd or even space adjustment for start and the end
                        oe_sp_start, oe_sp_end = get_odd_even_space_adj(length,len(dato))
                        print(move_cursor_right(self.adj_indent) + set_hchr_v + self.header_left_vertical_line_chr + set_t +\
                              move_cursor_right(self.adj_space+oe_sp_start,self.header_all_cell_bg)+ dato +\
                              move_cursor_right(self.adj_space+oe_sp_end,self.header_all_cell_bg) +\
                              set_hchr_v+self.header_right_vertical_line_chr+reset_font(),end="")

                    elif (self.header_align.lower() == "justify") or (self.header_align.lower() == "j"):
                        print(move_cursor_right(self.adj_indent) + set_hchr_v + self.header_left_vertical_line_chr + set_t +\
                              move_cursor_right(self.adj_space,self.header_all_cell_bg) + dato +\
                           move_cursor_right(self.adj_space+(length-len(dato)),self.header_all_cell_bg) + set_hchr_v +\
                           self.header_right_vertical_line_chr+reset_font(),end="")
                    else:
                        print(move_cursor_right(self.adj_indent) + set_hchr_v + self.header_left_vertical_line_chr + set_t +\
                              move_cursor_right(self.adj_space,self.header_all_cell_bg) + dato +\
                              move_cursor_right(self.adj_space+(length-len(dato)),self.header_all_cell_bg) + set_hchr_v +\
                              self.header_right_vertical_line_chr + reset_font(),end="")
                    print()
                    # the horizontal line between the headers and the first data row, only for matrix list
                    # if self.header_horizontal_line_on == True or self.middle_horizontal_line_on == 1:
                    # the horizontal line between the headers and the first data row, only for matrix list
                    if self.header_horizontal_line_on == True :
                        indent = 1; print_horizontal_segment(self, self.header_left_corner_chr,\
                                 self.header_horizontal_line_chr, length + (2*self.adj_space), indent, "horizontal_header")
                        indent = 0; print_horizontal_segment(self, self.header_right_corner_chr,\
                                                     self.header_horizontal_line_chr, 0, indent, "horizontal_header")
                        print()

                else:                        # printing Data
                    if (self.data_align.lower() == "left") or (self.data_align.lower() == "l"):
                        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d + dato+\
                           move_cursor_right((self.adj_space*2)+(length-len(dato)),self.data_all_cell_bg) +\
                           set_v + self.right_vertical_line_chr + reset_font(),end="")

                    elif (self.data_align.lower() == "right") or (self.data_align.lower() == "r"):
                        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d +\
                              move_cursor_right((self.adj_space*2)+(length-len(dato)),self.data_all_cell_bg) +\
                                 dato + set_v + self.right_vertical_line_chr + reset_font(),end="")

                    elif (self.data_align.lower() == "center") or (self.data_align.lower() == "c"):
                        # add the extra space for the word odd or even space adjustment for start and the end
                        oe_sp_start, oe_sp_end = get_odd_even_space_adj(length,len(dato))
                        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d +\
                              move_cursor_right(self.adj_space+oe_sp_start,self.data_all_cell_bg)+ dato +\
                              move_cursor_right(self.adj_space+oe_sp_end,self.data_all_cell_bg) + set_v +\
                              self.right_vertical_line_chr + reset_font(),end="")

                    elif (self.data_align.lower() == "justify") or (self.data_align.lower() == "j"):
                        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d +\
                              move_cursor_right(self.adj_space,self.data_all_cell_bg)+ dato +\
                              move_cursor_right(self.adj_space+length-len(dato),self.data_all_cell_bg)+\
                              set_v + self.right_vertical_line_chr + reset_font(),end="")

                    else:
                        print(move_cursor_right(self.adj_indent) + set_v + self.left_vertical_line_chr + set_d +\
                              move_cursor_right(self.adj_space,self.data_all_cell_bg)+ dato +\
                              move_cursor_right(self.adj_space+length-len(dato),self.data_all_cell_bg) + set_v +\
                              self.right_vertical_line_chr + reset_font(),end="")

                    print()
                    # the horizontal line for all the rows, only for matrix list. 1 shows it and 0 hides it
                    if self.middle_horizontal_line_on == 1:
                        ctrl_header += 1
                        if ctrl_header == len(my_list):  pass

                        else:
                            indent = 1; print_horizontal_segment(self, self.left_lateral_corner_chr, self.middle_horizontal_line_chr,\
                                                                  length + (2*self.adj_space), indent, "inner_corner")

                            indent = 0; print_horizontal_segment(self, self.right_lateral_corner_chr, self.middle_horizontal_line_chr,\
                                                                  0, indent, "inner_corner")
                            print()
        #---------------------------------------------------------------------------------------------------------------------------------------------

        # print the bottom horizontal line
        if  self.bottom_horizontal_line_on == 1:
            indent = 1  # to add the space at the beginning (vertical line chr)
            print_horizontal_segment(self, self.bottom_left_corner_chr, self.bottom_horizontal_line_chr,\
                                      length + (2*self.adj_space), indent, "corner")
            indent = 0  # to don't add this space at the end or the middle
            print_horizontal_segment(self, self.bottom_right_corner_chr, self.bottom_horizontal_line_chr,\
                                      0, indent, "corner")
            print()

        else:  pass

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # we are dealing with a matrix list something like this [[10,20,30],[40,50,60],[70,80,90]]                                                       -
    # Awsome...!                                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    else:
        max_rows, max_cols = get_number_rows_cols_list(my_list)
        n_cols = []; tempo_cols = []

        # we create the transpose of the list but we save their lens in the transpose rather than the data
        for c in range(max_cols):
            for r in range(max_rows):
                tempo_cols.append(len(my_list[r][c]))
            n_cols.append(tempo_cols)
            tempo_cols = []

        longest_cols = []
        for col in n_cols:
            longest_cols.append(max(col)) # longest_cols keeps the size list of the longest columns in characters

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # drawing the top horizontal line
        if  self.top_horizontal_line_on == True:
            indent = 1  # to add the space at the beginning (indentation space)
            for item in longest_cols:
                if indent == 1:
                    print_horizontal_segment(self, self.top_left_corner_chr, self.top_horizontal_line_chr, (item+(2*self.adj_space)),\
                                              indent, "corner")
                    indent = 0
                else:   # corner or horizontal affect the color bg fg which variable will take into action
                    print_horizontal_segment(self, self.middle_top_corner_chr, self.top_horizontal_line_chr, (item+(2*self.adj_space)),\
                                              indent, "inner_corner")

            # last segment, which is only the corner that's why it's 0 on value
            print_horizontal_segment(self, self.top_right_corner_chr, self.top_horizontal_line_chr, 0, indent, "corner")
            print() # done top line, jump to next line to print data

        else:  pass
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # print header only
        ctrl_col = 0
        vertical = move_cursor_right(self.adj_indent)+set_hchr_v+self.header_left_vertical_line_chr
        for dato in my_list[0]:

            if (self.header_align.lower() == "left") or (self.header_align.lower() == "l"):
                print(vertical + set_t + dato + move_cursor_right((self.adj_space*2)+(longest_cols[ctrl_col]-len(dato)),self.header_all_cell_bg) +\
                      reset_font(),end="")

            elif (self.header_align.lower() == "right") or (self.header_align.lower() == "r"):
                print(vertical + set_t + move_cursor_right((self.adj_space*2)+(longest_cols[ctrl_col]-len(dato)),self.header_all_cell_bg) +\
                      dato + reset_font(),end="")

            elif (self.header_align.lower() == "center") or (self.header_align.lower() == "c"):
                # add the extra space for the word odd or even space adjustment for start and the end
                oe_sp_start, oe_sp_end = get_odd_even_space_adj(longest_cols[ctrl_col],len(dato))
                print(vertical + set_t + move_cursor_right(self.adj_space+oe_sp_start,self.header_all_cell_bg) + dato +\
                      move_cursor_right(self.adj_space+oe_sp_end,self.header_all_cell_bg) + reset_font(),end="")

            elif (self.header_align.lower() == "justify") or (self.header_align.lower() == "j"):
                print(vertical + set_t + move_cursor_right(self.adj_space,self.header_all_cell_bg) + dato +\
                      move_cursor_right(self.adj_space+(longest_cols[ctrl_col]-len(dato)),self.header_all_cell_bg) + reset_font(),end="")

            else:
                print(vertical + set_t + move_cursor_right(self.adj_space,self.header_all_cell_bg) + dato +\
                      move_cursor_right(self.adj_space+(longest_cols[ctrl_col]-len(dato)),self.header_all_cell_bg) + reset_font(),end="")

            vertical = set_hchr_v+self.header_middle_vertical_line_chr
            ctrl_col += 1
        print(set_hchr_v+self.header_right_vertical_line_chr+reset_font())

        #---------------------------------------------------------------------------------------------------------------------------------------------
        if self.header_horizontal_line_on == True :
            # the horizontal line between the headers and the firs data row, only for matrix list
            indent = 1  # to add the space at the beginning (indentation space)
            # drawing the bottom horizontal line
            for item in longest_cols:
                if indent == 1:
                    print_horizontal_segment(self, self.header_left_corner_chr,\
                       self.header_horizontal_line_chr, (item+(2*self.adj_space)), indent,"horizontal_header") # first segment
                    indent = 0
                else:
                    print_horizontal_segment(self, self.header_middle_corner_chr,\
                       self.header_horizontal_line_chr, (item+(2*self.adj_space)), indent,"horizontal_header") # middle segments

            # last segment, which is only the corner that's why it's 0 on value
            print_horizontal_segment(self, self.header_right_corner_chr,\
                  self.header_horizontal_line_chr, 0, indent, "horizontal_header")

            print() # done top line, jump to next line to print data

        ctrl_sep = 1
        for datos in my_list[1:]:  # This skip the first one
            ctrl_col = 0
            vertical = move_cursor_right(self.adj_indent)+set_v+self.left_vertical_line_chr
            for dato in datos:

                if (self.data_align.lower() == "left") or (self.data_align.lower() == "l"):
                    print(vertical + set_d + dato + move_cursor_right((self.adj_space*2)+(longest_cols[ctrl_col]-len(dato)),self.data_all_cell_bg) +\
                          reset_font(),end="")

                elif (self.data_align.lower() == "right") or (self.data_align.lower() == "r"):
                    print(vertical + set_d + move_cursor_right((self.adj_space*2)+(longest_cols[ctrl_col]-len(dato)),self.data_all_cell_bg) +\
                          dato + reset_font(),end="")

                elif (self.data_align.lower() == "center") or (self.data_align.lower() == "c"):
                    # add the extra space for the word odd or even space adjustment for start and the end
                    oe_sp_start, oe_sp_end = get_odd_even_space_adj(longest_cols[ctrl_col],len(dato))
                    print(vertical + set_d + move_cursor_right(self.adj_space+oe_sp_start,self.data_all_cell_bg) + dato +\
                          move_cursor_right(self.adj_space+oe_sp_end,self.data_all_cell_bg) + reset_font(),end="")

                elif (self.data_align.lower() == "justify") or (self.data_align.lower() == "j"):
                    print(vertical + set_d + move_cursor_right(self.adj_space,self.data_all_cell_bg) + dato +\
                          move_cursor_right(self.adj_space+(longest_cols[ctrl_col]-len(dato)),self.data_all_cell_bg) + reset_font(),end="")

                else:
                    print(vertical + set_d + move_cursor_right(self.adj_space,self.data_all_cell_bg) + dato +\
                          move_cursor_right(self.adj_space+(longest_cols[ctrl_col]-len(dato)),self.data_all_cell_bg) + reset_font(),end="")

                vertical = set_v+self.middle_vertical_line_chr
                ctrl_col += 1
            print(set_v+self.right_vertical_line_chr+reset_font())

            if self.middle_horizontal_line_on == 1:
                if ctrl_sep == len(my_list)-1:
                    # drawing the bottom horizontal line
                    if  self.bottom_horizontal_line_on == 1:
                        indent = 1  # to add the space at the beginning (indentation space)

                        for item in longest_cols:
                            if indent == 1:
                                # def print_horizontal_segment(self,start_chr,end_chr,times,indent,option):
                                print_horizontal_segment(self, self.bottom_left_corner_chr, self.bottom_horizontal_line_chr,\
                                   (item+(2*self.adj_space)), indent, "corner") # first segment
                                indent = 0

                            else:
                                # def print_horizontal_segment(self,start_chr,end_chr,times,indent,option):
                                print_horizontal_segment(self, self.middle_bottom_corner_chr, self.bottom_horizontal_line_chr,\
                                   (item+(2*self.adj_space)), indent, "inner_corner")
                                # last segment, which is only the corner that's why it's 0 on value
                        print_horizontal_segment(self, self.bottom_right_corner_chr,\
                           self.bottom_horizontal_line_chr, 0, indent, "corner")

                    else:
                        pass
                else:
                    indent = 1  # to add the space at the beginning (indentation space)
                                # drawing the bottom horizontal line
                    for item in longest_cols:
                        if indent == 1:
                            # def print_horizontal_segment(self,start_chr,end_chr,times,indent,option):
                            print_horizontal_segment(self, self.left_lateral_corner_chr, self.middle_horizontal_line_chr,\
                                                     (item+(2*self.adj_space)), indent,"inner_corner")
                            indent = 0

                        else:
                            print_horizontal_segment(self, self.middle_inner_corner_chr, self.middle_horizontal_line_chr,\
                                                     (item+(2*self.adj_space)), indent, "inner_corner")

                    print_horizontal_segment(self, self.right_lateral_corner_chr, self.middle_horizontal_line_chr,\
                                              0, indent, "inner_corner")
                print()
            ctrl_sep += 1

        if self.middle_horizontal_line_on == 0:
            if  self.bottom_horizontal_line_on == 1:
                indent = 1  # to add the space at the beginning (indentation space)
                            # drawing the bottom horizontal line
                for item in longest_cols:
                    if indent == 1:
                        # first segment
                        print_horizontal_segment(self, self.bottom_left_corner_chr, self.bottom_horizontal_line_chr,\
                                                 (item+(2*self.adj_space)), indent, "corner")
                        indent = 0
                    else:
                        #"horizontal")#"corner") # middle segments
                        print_horizontal_segment(self, self.middle_bottom_corner_chr, self.bottom_horizontal_line_chr,\
                                                 (item+(2*self.adj_space)), indent, "inner_corner")

                        # last segment, which is only the corner that's why it's 0 on value
                print_horizontal_segment(self, self.bottom_right_corner_chr, self.bottom_horizontal_line_chr,\
                                          0, indent, "corner")
                print() # done top line, jump to next line to print data

            else:  pass
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    print_notefoot(self,my_list)
    ins_newline(self.adj_bottom_margin)
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# End Printing Matrix                                                                                                                                -
#-----------------------------------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Making all the spaces in the table free of chars. This is for not spaces between the columns in the header and data                                          -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def make_double_empty_space_on_tbl(self):
    '''
        makes double space rather than print the character for the line
    '''
    # Horizontal Line Section
    self.top_horizontal_line_chr = " ";         self.bottom_horizontal_line_chr = " ";      self.middle_horizontal_line_chr = " "

    # Vertical Line Section
    self.left_vertical_line_chr  = "  ";         self.middle_vertical_line_chr = "  ";      self.right_vertical_line_chr = "  "

    # Outside Corner Section
    self.top_left_corner_chr     = "  ";         self.top_right_corner_chr   = "  "
    self.bottom_right_corner_chr = "  ";         self.bottom_left_corner_chr = "  "

    # Middle Corner Section
    self.middle_top_corner_chr   = "  ";         self.middle_bottom_corner_chr = "  ";      self.middle_inner_corner_chr = "  "
    self.left_lateral_corner_chr = "  ";         self.right_lateral_corner_chr = "  "

    # Header Section  Only for Matrix List
    self.header_left_vertical_line_chr   = "  "
    self.header_right_vertical_line_chr  = "  "
    self.header_middle_vertical_line_chr = "  "

    # Under Line Header Section  Only for Matrix List
    self.header_horizontal_line_chr   = " ";      self.header_left_corner_chr   = "  "
    self.header_right_corner_chr = "  ";     self.header_middle_corner_chr = "  "


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Setting all the color for the table between header and data                                                                                        -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def set_color_for_spaces_on_tbl(self, bg_color_line, bg_color_header, fg_color_header, bg_color_data, fg_color_data):
    '''
        setting the colors for the spaces
    '''
    self.horizontal_line_bg = bg_color_line
    self.outer_corner_bg    = bg_color_line
    self.inner_corner_bg    = bg_color_line
    self.header_corner_bg   = bg_color_line
    self.header_horizontal_line_bg = bg_color_line
    self.header_vertical_line_bg   = bg_color_line
    self.vertical_line_bg = bg_color_line

    self.header_bg = bg_color_header
    self.header_fg = fg_color_header
    self.data_bg   = bg_color_data
    self.data_fg   = fg_color_data

    self.top_horizontal_line_on    = True
    self.bottom_horizontal_line_on = True
    self.left_vertical_line_on     = True
    self.right_vertical_line_on    = True



def set_color_2_for_tbl(self,bg_h, fg_h, bg_l, bg_d, fg_d):
    '''
        setting the colors for the designs
    '''
    self.header_corner_bg = bg_h
    self.header_horizontal_line_bg = bg_h
    self.header_vertical_line_bg   = bg_h
    self.header_bg = bg_h

    self.header_fg = fg_h

    self.outer_corner_bg    = bg_l
    self.horizontal_line_bg = bg_l
    self.inner_corner_bg    = bg_l
    self.vertical_line_bg   = bg_l

    self.data_bg = bg_d
    self.data_fg = fg_d

    self.header_bold = True
    self.middle_horizontal_line_on = False
    self.top_horizontal_line_on    = False
    self.bottom_horizontal_line_on = False
    self.header_horizontal_line_on = False

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Making all the spaces in the table free of chars. This is for spaces between the columns in the header and data                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def make_single_empty_space_on_tbl(self):
    '''
        makes single space rather than print the character for the line
    '''
    # Horizontal Line Section
    self.top_horizontal_line_chr = " ";         self.bottom_horizontal_line_chr = " ";      self.middle_horizontal_line_chr = " "

    # Vertical Line Section
    self.left_vertical_line_chr  = " ";         self.middle_vertical_line_chr = " ";        self.right_vertical_line_chr = " "

    # Outside Corner Section
    self.top_left_corner_chr     = " ";         self.top_right_corner_chr   = " "
    self.bottom_right_corner_chr = " ";         self.bottom_left_corner_chr = " "

    # Middle Corner Section
    self.middle_top_corner_chr   = " ";         self.middle_bottom_corner_chr = " ";         self.middle_inner_corner_chr = " "
    self.left_lateral_corner_chr = " ";         self.right_lateral_corner_chr = " "

    # Header Section  Only for Matrix List
    self.header_left_vertical_line_chr   = " "
    self.header_right_vertical_line_chr  = " "
    self.header_middle_vertical_line_chr = " "

    # Under Line Header Section  Only for Matrix List
    self.header_horizontal_line_chr = " ";      self.header_left_corner_chr   = " "
    self.header_right_corner_chr    = " ";      self.header_middle_corner_chr = " "

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Fancy Format Class, Defing the Class Without Initial Parameters                                                                                   --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
class FancyFormat:
    '''
    It create the format for the fancy_print_format method
    '''
    def __init__(self):
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # defining variable names                  # values to take                                                                                  -
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # General Use
        self.adj_top_margin    = 0                 # lines to be add between the terminal and the title
        self.adj_bottom_margin = 0                 # lines to be add between the end of list or footnote and terminal
        self.adj_top_space     = 0                 # lines to be added between title and top list
        self.adj_bottom_space  = 0                 # lines to be added between bottom list and footnote
        self.adj_indent        = 2                 # space from the terminal to the box
        self.adj_space         = 2                 # space from left to right inside inside the box
        self.set_fill_chr      = "----"            # to fill the empty spots when the list is not complete
        self.set_layout        = Layout.HORIZONTAL # This is only for Range, Set, Frozenset and dictionary type
        self.update_list       = False             # if we want to save the data as it's presented, but string each element in list

    #    +------------------------------------------------------------------------------+
    #    |    Color Design Template, Demos                                              |
    #    |    The following are some predesign (Design 1,2)                             |
    #    |                                                                              |
    #    |    design_color(self, 0_Desgin,  1_bg_lines,     2_fg_lines)                 |
    #    |                                                                              |
    #    +------------------------------------------------------------------------------+
        self.design_color   = 4   # This color is used for the designs (1 through 10)
        self.bg_line_colors = -1  # set all the bg_line colors, if it's set to default (-1, 256) then It'll be used the default variables
        self.fg_line_colors = -1  # set all the fg_line colors, if it's set to default (-1, 256) then It'll be used the default variables
        # bold_lines has 2 options:
        # True  -> will set up all the lines to bold
        # False -> will set all the lines to regular and it will respect every single variable assigned to the bold lines
        self.bold_lines = False


        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Title Section
        self.title_msg       = ""                  # string value
        self.title_bold      = False               # two values False and True (0 and 1)
        self.title_bg        = -1                  # values -1 to 255
        self.title_fg        = -1                  # values -1 to 255
        self.title_align     = "justify"           # 4 values: justify(j),left(l), center(c), and right(r)
        self.title_italic    = False               # two values False and True (0 and 1)
        self.title_underline = False               # two values False and True (0 and 1)
        self.title_strike    = False               # two values False and True (0 and 1)
        self.title_blinking  = False               # two values False and True (0 and 1)
        self.title_dim       = False               # two values False and True (0 and 1)
        self.title_hidden    = False               # two values False and True (0 and 1)
        self.title_inverse   = False               # two values False and True (0 and 1)

        # Footnote Section
        self.footnote_msg       = ""               # string value
        self.footnote_bold      = False            # two values False and True (0 and 1)
        self.footnote_bg        = -1               # values -1 to 255
        self.footnote_fg        = -1               # values -1 to 255
        self.footnote_align     = "justify"        # 4 values: justify(j),left(l), center(c), and right(r)
        self.footnote_italic    = False            # two values False and True (0 and 1)
        self.footnote_underline = False            # two values False and True (0 and 1)
        self.footnote_strike    = False            # two values False and True (0 and 1)
        self.footnote_blinking  = False            # two values False and True (0 and 1)
        self.footnote_dim       = False            # two values False and True (0 and 1)
        self.footnote_hidden    = False            # two values False and True (0 and 1)
        self.footnote_inverse   = False            # two values False and True (0 and 1)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Data Section
        self.data_bold        = False              # two values False and True (0 and 1)
        self.data_bg          = -1                 # values -1 to 255
        self.data_all_cell_bg = True               # how long will be the bg (all the cell or only the data)
        self.data_fg          = -1                 # values -1 to 255
        self.data_align       = "justify"          # 4 values: justify(j),left(l), center(c), and right(r)
        self.data_italic      = False              # two values False and True (0 and 1)
        self.data_underline   = False              # two values False and True (0 and 1)
        self.data_strike      = False              # two values False and True (0 and 1)
        self.data_blinking    = False              # two values False and True (0 and 1)
        self.data_dim         = False              # two values False and True (0 and 1)
        self.data_hidden      = False              # two values False and True (0 and 1)
        self.data_inverse     = False              # two values False and True (0 and 1)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Horizontal Line Section
        self.top_horizontal_line_chr    = " "      # chr used to print the horizontal segment for the top line
        self.bottom_horizontal_line_chr = " "      # chr used to print the horizontal segment for the bottom line
        self.middle_horizontal_line_chr = " "      # chr used to print the horizontal segment horizontal. Only matrix list

        #-----------------------------------------------------+---------------------------------------------+
        self.top_horizontal_line_on     = True     # |  to show or hide horizontal lines                    |
        self.middle_horizontal_line_on  = False    # |  for all the rows, only for matrix list.             |
        self.bottom_horizontal_line_on  = True     # |  two values False and True (0 and 1)                 |
        #-----------------------------------------------------+---------------------------------------------+

        self.horizontal_line_bold = False          # two values False and True (0 and 1)
        self.horizontal_line_bg   = -1             # values -1 to 255
        self.horizontal_line_fg   = -1             # values -1 to 255
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Vertical Line Section
        self.left_vertical_line_chr   = " "        # used for the left vertical line only
        self.middle_vertical_line_chr = " "        # all the vertical line in the middle between left and right. Only matrix
        self.right_vertical_line_chr  = " "        # used for the right vertical line only

        self.vertical_line_bold = False            # two values False and True (0 and 1)
        self.vertical_line_bg   = -1               # values -1 to 255
        self.vertical_line_fg   = -1               # values -1 to 255

        #-----------------------------------------------------+---------------------------------------------+
        self.right_vertical_line_on  = True        # | To show or hide vertical lines                       |
        self.left_vertical_line_on   = True        # | Testing this code (11_Template_4_Demo_1.py)          |
        self.middle_vertical_line_on = True        # | Testing this code (11_Template_4_Demo_1.py)          |
        #-----------------------------------------------------+---------------------------------------------+
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # External Corner Section
        self.top_left_corner_chr     = " "         # chr for the top left corner
        self.top_right_corner_chr    = " "         # chr for the top right corner
        self.bottom_right_corner_chr = " "         # chr for the bottom right corner
        self.bottom_left_corner_chr  = " "         # chr for the bottom left corner

        self.outer_corner_bold = False                  # two values False and True (0 and 1)
        self.outer_corner_bg   = -1                     # values -1 to 255
        self.outer_corner_fg   = -1                     # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Middle Corner Section
        self.middle_top_corner_chr    = " "        # all the middle corners between top_left_corner_chr and top_right_corner_chr. Only matrix list
        self.middle_bottom_corner_chr = " "        # all the middle corners between top_left_corner_chr and top_right_corner_chr. Only matrix list
        self.middle_inner_corner_chr  = " "        # corner inside the matrix and sides but not top(left,right), or bottom(left, right). Only matrix list
        self.left_lateral_corner_chr  = " "        # chr only for matrix list
        self.right_lateral_corner_chr = " "        # chr only for matrix list

        self.inner_corner_bold = False             # two values False and True (0 and 1)
        self.inner_corner_bg   = -1                # values -1 to 255
        self.inner_corner_fg   = -1                # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Header                                     Section  Only for Matrix List
        self.header_bold        = False            # two values False and True (0 and 1)
        self.header_bg          = -1               # values -1 to 255
        self.header_all_cell_bg = True             # how long will be the bg (all the cell or only the header)
        self.header_fg          = -1               # values -1 to 255
        self.header_align       = "justify"        # 4 values: justify(j),left(l), center(c), and right(r)
        self.header_italic      = False            # two values False and True (0 and 1)
        self.header_underline   = False            # two values False and True (0 and 1)
        self.header_strike      = False            # two values False and True (0 and 1)
        self.header_blinking    = False            # two values False and True (0 and 1)
        self.header_dim         = False            # two values False and True (0 and 1)
        self.header_hidden      = False            # two values False and True (0 and 1)
        self.header_inverse     = False            # two values False and True (0 and 1)

        # Attributes for the header lines
        self.header_left_vertical_line_chr   = " "       # small_bullet u'\u2022'
        self.header_right_vertical_line_chr  = " "       # circle_bullet u'\u2B24'
        self.header_middle_vertical_line_chr = " "       # matrix list only
        self.header_vertical_line_bold   = False         # two values False and True (0 and 1)
        self.header_vertical_line_bg     = -1            # values -1 to 255
        self.header_vertical_line_fg     = -1            # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Header horizontal line                           Section  Only for Matrix List
        self.header_horizontal_line_on  = False    # horizontal line between headers and the firs data row. 1 shows it and 0 hides it
        self.header_horizontal_line_chr = "-"      # chr to be printed for theheader line

        self.header_horizontal_line_bold = False              # values -1 to 255
        self.header_horizontal_line_bg   = -1                 # values -1 to 255
        self.header_horizontal_line_fg   = -1                 # values -1 to 255

        # attributes for the header corners (left, middles and right)
        self.header_left_corner_chr   = " "   # only for header line
        self.header_right_corner_chr  = " "   # only for header line
        self.header_middle_corner_chr = " "   # only for header line
        self.header_corner_bold       = False # two values False and True (0 and 1)
        self.header_corner_bg         = -1    # values -1 to 255
        self.header_corner_fg         = -1    # values -1 to 255


    def reset_fancy_format(self):

        '''  It resets all the attributes of the class  '''
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # defining variable names                  # values to take                                                                                  -
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # General Use
        self.adj_top_margin    = 0                 # lines to be add between the terminal and the title
        self.adj_bottom_margin = 0                 # lines to be add between the end of list or footnote and terminal
        self.adj_top_space     = 0                 # lines to be added between title and top list
        self.adj_bottom_space  = 0                 # lines to be added between bottom list and footnote
        self.adj_indent        = 2                 # space from the terminal to the box
        self.adj_space         = 2                 # space from left to right inside inside the box
        self.set_fill_chr      = "----"            # to fill the empty spots when the list is not complete
        self.set_layout        = Layout.HORIZONTAL # This is only for Range, Set, Frozenset and dictionary type
        self.update_list       = False             # if we want to save the data as it's presented, but string each element in list

    #    +------------------------------------------------------------------------------+
    #    |    Color Design Template, Demos                                              |
    #    |    The following are some predesign (Design 1,2)                             |
    #    |                                                                              |
    #    |    design_color(self, 0_Desgin,  1_bg_lines,     2_fg_lines)                 |
    #    |                                                                              |
    #    +------------------------------------------------------------------------------+
        self.design_color   = 4   # This color is used for the designs (1 through 10)
        self.bg_line_colors = -1  # set all the bg_line colors, if it's set to default (-1, 256) then It'll be used the default variables
        self.fg_line_colors = -1  # set all the fg_line colors, if it's set to default (-1, 256) then It'll be used the default variables
        # bold_lines has 2 options:
        # True  -> will set up all the lines to bold
        # False -> will set all the lines to regular and it will respect every single variable assigned to the bold lines
        self.bold_lines = False


        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Title Section
        self.title_msg       = ""                  # string value
        self.title_bold      = False               # two values False and True (0 and 1)
        self.title_bg        = -1                  # values -1 to 255
        self.title_fg        = -1                  # values -1 to 255
        self.title_align     = "justify"           # 4 values: justify(j),left(l), center(c), and right(r)
        self.title_italic    = False               # two values False and True (0 and 1)
        self.title_underline = False               # two values False and True (0 and 1)
        self.title_strike    = False               # two values False and True (0 and 1)
        self.title_blinking  = False               # two values False and True (0 and 1)
        self.title_dim       = False               # two values False and True (0 and 1)
        self.title_hidden    = False               # two values False and True (0 and 1)
        self.title_inverse   = False               # two values False and True (0 and 1)

        # Footnote Section
        self.footnote_msg       = ""               # string value
        self.footnote_bold      = False            # two values False and True (0 and 1)
        self.footnote_bg        = -1               # values -1 to 255
        self.footnote_fg        = -1               # values -1 to 255
        self.footnote_align     = "justify"        # 4 values: justify(j),left(l), center(c), and right(r)
        self.footnote_italic    = False            # two values False and True (0 and 1)
        self.footnote_underline = False            # two values False and True (0 and 1)
        self.footnote_strike    = False            # two values False and True (0 and 1)
        self.footnote_blinking  = False            # two values False and True (0 and 1)
        self.footnote_dim       = False            # two values False and True (0 and 1)
        self.footnote_hidden    = False            # two values False and True (0 and 1)
        self.footnote_inverse   = False            # two values False and True (0 and 1)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Data Section
        self.data_bold        = False              # two values False and True (0 and 1)
        self.data_bg          = -1                 # values -1 to 255
        self.data_all_cell_bg = True               # how long will be the bg (all the cell or only the data)
        self.data_fg          = -1                 # values -1 to 255
        self.data_align       = "justify"          # 4 values: justify(j),left(l), center(c), and right(r)
        self.data_italic      = False              # two values False and True (0 and 1)
        self.data_underline   = False              # two values False and True (0 and 1)
        self.data_strike      = False              # two values False and True (0 and 1)
        self.data_blinking    = False              # two values False and True (0 and 1)
        self.data_dim         = False              # two values False and True (0 and 1)
        self.data_hidden      = False              # two values False and True (0 and 1)
        self.data_inverse     = False              # two values False and True (0 and 1)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Horizontal Line Section
        self.top_horizontal_line_chr    = " "      # chr used to print the horizontal segment for the top line
        self.bottom_horizontal_line_chr = " "      # chr used to print the horizontal segment for the bottom line
        self.middle_horizontal_line_chr = " "      # chr used to print the horizontal segment horizontal. Only matrix list

        #-----------------------------------------------------+---------------------------------------------+
        self.top_horizontal_line_on     = True     # |  to show or hide horizontal lines                    |
        self.middle_horizontal_line_on  = False    # |  for all the rows, only for matrix list.             |
        self.bottom_horizontal_line_on  = True     # |  two values False and True (0 and 1)                 |
        #-----------------------------------------------------+---------------------------------------------+

        self.horizontal_line_bold = False          # two values False and True (0 and 1)
        self.horizontal_line_bg   = -1             # values -1 to 255
        self.horizontal_line_fg   = -1             # values -1 to 255
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Vertical Line Section
        self.left_vertical_line_chr   = " "        # used for the left vertical line only
        self.middle_vertical_line_chr = " "        # all the vertical line in the middle between left and right. Only matrix
        self.right_vertical_line_chr  = " "        # used for the right vertical line only

        self.vertical_line_bold = False            # two values False and True (0 and 1)
        self.vertical_line_bg   = -1               # values -1 to 255
        self.vertical_line_fg   = -1               # values -1 to 255

        #-----------------------------------------------------+---------------------------------------------+
        self.right_vertical_line_on  = True        # | To show or hide vertical lines                       |
        self.left_vertical_line_on   = True        # | Testing this code (11_Template_4_Demo_1.py)          |
        self.middle_vertical_line_on = True        # | Testing this code (11_Template_4_Demo_1.py)          |
        #-----------------------------------------------------+---------------------------------------------+
        #---------------------------------------------------------------------------------------------------------------------------------------------
        # External Corner Section
        self.top_left_corner_chr     = " "         # chr for the top left corner
        self.top_right_corner_chr    = " "         # chr for the top right corner
        self.bottom_right_corner_chr = " "         # chr for the bottom right corner
        self.bottom_left_corner_chr  = " "         # chr for the bottom left corner

        self.outer_corner_bold = False                  # two values False and True (0 and 1)
        self.outer_corner_bg   = -1                     # values -1 to 255
        self.outer_corner_fg   = -1                     # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Middle Corner Section
        self.middle_top_corner_chr    = " "        # all the middle corners between top_left_corner_chr and top_right_corner_chr. Only matrix list
        self.middle_bottom_corner_chr = " "        # all the middle corners between top_left_corner_chr and top_right_corner_chr. Only matrix list
        self.middle_inner_corner_chr  = " "        # corner inside the matrix and sides but not top(left,right), or bottom(left, right). Only matrix list
        self.left_lateral_corner_chr  = " "        # chr only for matrix list
        self.right_lateral_corner_chr = " "        # chr only for matrix list

        self.inner_corner_bold = False             # two values False and True (0 and 1)
        self.inner_corner_bg   = -1                # values -1 to 255
        self.inner_corner_fg   = -1                # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Header                                     Section  Only for Matrix List
        self.header_bold        = False            # two values False and True (0 and 1)
        self.header_bg          = -1               # values -1 to 255
        self.header_all_cell_bg = True             # how long will be the bg (all the cell or only the header)
        self.header_fg          = -1               # values -1 to 255
        self.header_align       = "justify"        # 4 values: justify(j),left(l), center(c), and right(r)
        self.header_italic      = False            # two values False and True (0 and 1)
        self.header_underline   = False            # two values False and True (0 and 1)
        self.header_strike      = False            # two values False and True (0 and 1)
        self.header_blinking    = False            # two values False and True (0 and 1)
        self.header_dim         = False            # two values False and True (0 and 1)
        self.header_hidden      = False            # two values False and True (0 and 1)
        self.header_inverse     = False            # two values False and True (0 and 1)

        # Attributes for the header lines
        self.header_left_vertical_line_chr   = " "       # small_bullet u'\u2022'
        self.header_right_vertical_line_chr  = " "       # circle_bullet u'\u2B24'
        self.header_middle_vertical_line_chr = " "       # matrix list only
        self.header_vertical_line_bold   = False         # two values False and True (0 and 1)
        self.header_vertical_line_bg     = -1            # values -1 to 255
        self.header_vertical_line_fg     = -1            # values -1 to 255

        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Header horizontal line                           Section  Only for Matrix List
        self.header_horizontal_line_on  = False    # horizontal line between headers and the firs data row. 1 shows it and 0 hides it
        self.header_horizontal_line_chr = "-"      # chr to be printed for theheader line

        self.header_horizontal_line_bold = False              # values -1 to 255
        self.header_horizontal_line_bg   = -1                 # values -1 to 255
        self.header_horizontal_line_fg   = -1                 # values -1 to 255

        # attributes for the header corners (left, middles and right)
        self.header_left_corner_chr   = " "   # only for header line
        self.header_right_corner_chr  = " "   # only for header line
        self.header_middle_corner_chr = " "   # only for header line
        self.header_corner_bold       = False # two values False and True (0 and 1)
        self.header_corner_bg         = -1    # values -1 to 255
        self.header_corner_fg         = -1    # values -1 to 255




    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Defing a the main function to control the print of the list                                                                                    -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def print_fancy_format(self,data="none",style=Line_Style.DASH):

        '''  It prints any type of data in a fancy format

             print_fancy_format(data, style)  '''

        data_list = data2list(self, data)
        my_list = []
        # convert all elements in the list to strigs only because the int type will cause problems with len command
        list_type = get_list_type(data_list)
        flag_row_col_insert = 0       # this control to add the row and cols for spaces for better visualization
        #--------------------------------------------------------------------------------------------------------------------------------------------+
        #                                                                                                                                            |
        #    Backup all the default values                                                                                                           |
        #                                                                                                                                            |
        #--------------------------------------------------------------------------------------------------------------------------------------------+
        # Horizontal Line Section                           Vertical Line Section
        thlc = self.top_horizontal_line_chr;                lvlc = self.left_vertical_line_chr
        bhlc = self.bottom_horizontal_line_chr;             mvlc = self.middle_vertical_line_chr
        hlc = self.middle_horizontal_line_chr;              rvlc = self.right_vertical_line_chr

        # Corner Section
        tlcc = self.top_left_corner_chr;                    trcc = self.top_right_corner_chr
        brcc = self.bottom_right_corner_chr;                blcc = self.bottom_left_corner_chr

        mtcc = self.middle_top_corner_chr;                  mbcc = self.middle_bottom_corner_chr;       micc = self.middle_inner_corner_chr
        llcc = self.left_lateral_corner_chr;                rlcc = self.right_lateral_corner_chr

        # Header Section  Only for Matrix List              # attributes for the header corners (left, middles and right)
        lvhlc = self.header_left_vertical_line_chr;         lculhc = self.header_left_corner_chr
        rvhlc = self.header_right_vertical_line_chr;        rculhc = self.header_right_corner_chr
        mvhlc = self.header_middle_vertical_line_chr;       mculhc = self.header_middle_corner_chr

        # Under Line Header Section  Only for Matrix List
        hluhc = self.header_horizontal_line_chr

        # Colors
        bg_H    = self.header_bg;                           fg_H    = self.header_fg
        bg_D    = self.data_bg;                             fg_D    = self.data_fg
        bg_hl   = self.horizontal_line_bg;                  fg_hl   = self.horizontal_line_fg
        bg_cc   = self.outer_corner_bg;                     fg_cc   = self.outer_corner_fg
        bg_ic   = self.inner_corner_bg;                     fg_vl   = self.vertical_line_fg
        bg_culh = self.header_corner_bg;                    fg_ic   = self.inner_corner_fg
        bg_ulh  = self.header_horizontal_line_bg;           fg_vhl  = self.header_vertical_line_fg
        bg_vhlc = self.header_vertical_line_bg;             fg_ulh  = self.header_horizontal_line_fg
        bg_vl   = self.vertical_line_bg;                    fg_culh = self.header_corner_fg

        # Lines ON
        thlo = self.top_horizontal_line_on
        mhl0 = self.middle_horizontal_line_on
        bhlo = self.bottom_horizontal_line_on
        rvlo = self.right_vertical_line_on
        lvlo = self.left_vertical_line_on
        mvlo = self.middle_vertical_line_on
        hluho = self.header_horizontal_line_on

        # Bold_lines
        bculh = self.header_corner_bold
        bulh  = self.header_horizontal_line_bold
        bvhl  = self.header_vertical_line_bold
        bic   = self.inner_corner_bold
        bc    = self.outer_corner_bold
        bvl   = self.vertical_line_bold
        bhl   = self.horizontal_line_bold

        # fill_chr
        fill_c = self.set_fill_chr


        # Assign Color to all the List for BG and FG
        if self.bg_line_colors <= -1 or self.bg_line_colors >= 256: pass
        else:
            self.horizontal_line_bg          = self.bg_line_colors
            self.outer_corner_bg             = self.bg_line_colors
            self.vertical_line_bg            = self.bg_line_colors
            self.inner_corner_bg             = self.bg_line_colors
            self.header_vertical_line_bg     = self.bg_line_colors
            self.header_horizontal_line_bg   = self.bg_line_colors
            self.header_corner_bg            = self.bg_line_colors

        if self.fg_line_colors <= -1 or self.fg_line_colors >= 256: pass
        else:
            self.horizontal_line_fg          = self.fg_line_colors
            self.outer_corner_fg             = self.fg_line_colors
            self.vertical_line_fg            = self.fg_line_colors
            self.inner_corner_fg             = self.fg_line_colors
            self.header_vertical_line_fg     = self.fg_line_colors
            self.header_horizontal_line_fg   = self.fg_line_colors
            self.header_corner_fg            = self.fg_line_colors

        if self.bold_lines == True:
            self.header_corner_bold          = True
            self.header_horizontal_line_bold = True
            self.header_vertical_line_bold   = True
            self.inner_corner_bold           = True
            self.outer_corner_bold           = True
            self.vertical_line_bold          = True
            self.horizontal_line_bold        = True
        else: pass



        if style.lower() == Line_Style.SINGLE_LINE:
            # Horizontal Line Section
            self.top_horizontal_line_chr = "\u2500";    self.bottom_horizontal_line_chr = "\u2500";  self.middle_horizontal_line_chr = "\u2500"

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u2502";    self.middle_vertical_line_chr = "\u2502";    self.right_vertical_line_chr = "\u2502"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u250C";    self.top_right_corner_chr   = "\u2510"
            self.bottom_right_corner_chr = "\u2518";    self.bottom_left_corner_chr = "\u2514"

            # Middle Corner Section
            self.middle_top_corner_chr   = "\u252C";    self.middle_bottom_corner_chr = "\u2534";    self.middle_inner_corner_chr = "\u253C"
            self.left_lateral_corner_chr = "\u251C";    self.right_lateral_corner_chr = "\u2524"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u2502"
            self.header_middle_vertical_line_chr = "\u2502"
            self.header_right_vertical_line_chr  = "\u2502"

            # Under Line Header Section  Only for Matrix List
            self.header_horizontal_line_chr = "\u2500"; self.header_left_corner_chr   = "\u251C"
            self.header_right_corner_chr    = "\u2524"; self.header_middle_corner_chr = "\u253C"


        elif style.lower() == Line_Style.SINGLE_BOLD:
            # Horizontal Line Section
            self.top_horizontal_line_chr = "\u2501";   self.bottom_horizontal_line_chr = "\u2501"; self.middle_horizontal_line_chr = "\u2501"

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u2503";   self.middle_vertical_line_chr = "\u2503";   self.right_vertical_line_chr = "\u2503"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u250F";   self.top_right_corner_chr   = "\u2513"
            self.bottom_right_corner_chr = "\u251B";   self.bottom_left_corner_chr = "\u2517"


            # Middle Corner Section
            self.middle_top_corner_chr   = "\u2533";   self.middle_bottom_corner_chr = "\u253B";   self.middle_inner_corner_chr = "\u254B"
            self.left_lateral_corner_chr = "\u2523";   self.right_lateral_corner_chr = "\u252B"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u2503"
            self.header_right_vertical_line_chr  = "\u2503"
            self.header_middle_vertical_line_chr = "\u2503"

            # Under Line Header Section  Only for Matrix List* <span style="color:blue"> <strong>print_separator </strong> </span>
            self.header_horizontal_line_chr = "\u2501"; self.header_left_corner_chr   = "\u2523"
            self.header_right_corner_chr    = "\u252B"; self.header_middle_corner_chr = "\u254B"


        elif style.lower() == Line_Style.SINGLE_HEAVY:
            # Horizontal Line Section
            self.top_horizontal_line_chr = "\u2586";    self.bottom_horizontal_line_chr="\u2586";   self.middle_horizontal_line_chr = "\u2586"

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u2588";    self.middle_vertical_line_chr = "\u2588";   self.right_vertical_line_chr = "\u2588"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u2586";    self.top_right_corner_chr   = "\u2586"
            self.bottom_right_corner_chr = "\u2588";    self.bottom_left_corner_chr = "\u2588"

            # Middle Corner Section
            self.middle_top_corner_chr   = "\u2586";    self.middle_bottom_corner_chr = "\u2588";   self.middle_inner_corner_chr = "\u2588"
            self.left_lateral_corner_chr = "\u2588";    self.right_lateral_corner_chr = "\u2588"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u2588"
            self.header_right_vertical_line_chr  = "\u2588"
            self.header_middle_vertical_line_chr = "\u2588"

            # Under Line Header Section  Only for Matrix List
            self.header_horizontal_line_chr = "\u2586"; self.header_left_corner_chr   = "\u2588"
            self.header_right_corner_chr    = "\u2588"; self.header_middle_corner_chr = "\u2588"


        elif style.lower() == Line_Style.DOUBLE_LINE:
            # Horizontal Line Section
            self.top_horizontal_line_chr = "\u2550";   self.bottom_horizontal_line_chr = "\u2550";   self.middle_horizontal_line_chr = "\u2550"

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u2551";   self.middle_vertical_line_chr = "\u2551";     self.right_vertical_line_chr = "\u2551"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u2554";   self.top_right_corner_chr   = "\u2557"
            self.bottom_right_corner_chr = "\u255D";   self.bottom_left_corner_chr = "\u255A"

            # Middle Corner Section
            self.middle_top_corner_chr   = "\u2566";   self.middle_bottom_corner_chr = "\u2569";     self.middle_inner_corner_chr = "\u256C"
            self.left_lateral_corner_chr = "\u2560";   self.right_lateral_corner_chr = "\u2563"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u2551"
            self.header_right_vertical_line_chr  = "\u2551"
            self.header_middle_vertical_line_chr = "\u2551"

            # Under Line Header Section  Only for Matrix List
            self.header_horizontal_line_chr = "\u2550"; self.header_left_corner_chr   = "\u2560"
            self.header_right_corner_chr    = "\u2563"; self.header_middle_corner_chr = "\u256C"


        elif style.lower() == Line_Style.SQ_BRACKETS:
            # Horizontal Line Section
            self.top_horizontal_line_chr = " ";           self.bottom_horizontal_line_chr = " ";        self.middle_horizontal_line_chr = " "

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u2502";      self.middle_vertical_line_chr = " ";          self.right_vertical_line_chr = "\u2502"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u250C";      self.top_right_corner_chr   = "\u2510"
            self.bottom_right_corner_chr = "\u2518";      self.bottom_left_corner_chr = "\u2514"

            # Middle Corner Section
            self.middle_top_corner_chr   =  " ";          self.middle_bottom_corner_chr = " ";          self.middle_inner_corner_chr = " "
            self.left_lateral_corner_chr =  "\u2502";     self.right_lateral_corner_chr = "\u2502"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u2502"
            self.header_right_vertical_line_chr  = "\u2502"
            self.header_middle_vertical_line_chr = " "

            # Under Line Header Section  Only for Matrix List
            self.header_horizontal_line_chr = " ";        self.header_left_corner_chr   = "\u2502"
            self.header_right_corner_chr    = "\u2502";   self.header_middle_corner_chr = " "


        elif style.lower() == Line_Style.DASH:
            # Horizontal Line Section
            self.top_horizontal_line_chr = "\u002D";    self.bottom_horizontal_line_chr = "\u002D";  self.middle_horizontal_line_chr = "\u002D"

            # Vertical Line Section
            self.left_vertical_line_chr  = "\u254E";    self.middle_vertical_line_chr = "\u254E";    self.right_vertical_line_chr = "\u254E"

            # Outside Corner Section
            self.top_left_corner_chr     = "\u002B";    self.top_right_corner_chr   = "+" #"\u002B"
            self.bottom_right_corner_chr = "\u002B";    self.bottom_left_corner_chr = "\u002B"

            # Middle Corner Section
            self.middle_top_corner_chr   =  "\u002B";   self.middle_bottom_corner_chr = "\u002B";    self.middle_inner_corner_chr = "\u002B"
            self.left_lateral_corner_chr =  "\u002B";   self.right_lateral_corner_chr = "\u002B"

            # Header Section  Only for Matrix List
            self.header_left_vertical_line_chr   = "\u254E"
            self.header_right_vertical_line_chr  = "\u254E"
            self.header_middle_vertical_line_chr = "\u254E"

            # Under Line Header Section  Only for Matrix List
            self.header_horizontal_line_chr = "\u002D"; self.header_left_corner_chr   = "\u002B"
            self.header_right_corner_chr    = "\u002B"; self.header_middle_corner_chr = "\u002B"

        #    +-------------------------------------------------------------------------+
        #    |    Color Design Template, Demos                                         |
        #    |    The following are some predesign (Design 2)                          |
        #    |                                                                         |
        #    |    set_color_2_for_tbl(self,bg_h, fg_h, bg_l, bg_d, fg_d)               |
        #    +-------------------------------------------------------------------------+
        elif style.lower() == Line_Style.WHITE_PURPLE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,231, 0, 90, 90, 231)

        elif style.lower() == Line_Style.WHITE_BLACK_PURPLE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,231, 234, 90, 234, 231)

        elif style.lower() == Line_Style.RED_WHITE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,1, 231, 231, 231, 21)

        elif style.lower() == Line_Style.PURPLE_WHITE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,90, 231, 22, 231, 234)

        elif style.lower() == Line_Style.BLUE_WHITE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,4, 231, 22, 231, 234)

        elif style.lower() == Line_Style.TURQUOISE_WHITE:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            set_color_2_for_tbl(self,44, 234, 234, 231, 234)


        #    +-------------------------------------------------------------------------+
        #    |    Color Design Template, Demos                                         |
        #    |    The following are some predesign (Design 1)                          |
        #    |                                                                         |
        #    |    set_color_for_spaces_on_tbl(self, bg_color_lines,  bg_color_header,  |
        #    |                                      fg_color_header, bg_color_data,    |
        #    |                                      fg_color_data)                     |
        #    +-------------------------------------------------------------------------+
        elif style.lower() == Line_Style.TEAL_WHITE:
            flag_row_col_insert = 1
            self.middle_horizontal_line_on       = False
            self.header_horizontal_line_on = False
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, -1, 23, 231, 231, 21)

        elif style.lower() == Line_Style.GRAY_TEAL_WHITE:
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 237, 23, 231, 231, 21)
            self.header_horizontal_line_chr = "-"
            self.header_horizontal_line_fg = 231

        elif style.lower() == Line_Style.WHITE_BLACK_1:
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 231, 231, 234, 231, 21)

        elif style.lower() == Line_Style.WHITE_BLACK_2:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 231, 231, 234, 234, 231)


        elif style.lower() == Line_Style.GREEN_GREEN_BLACK:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 121, 121, 0, 234, 231)

        elif style.lower() == Line_Style.BLUE_PURPLE_WHITE_1:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 4, 90, 15, 15, 21)

        elif style.lower() == Line_Style.BLUE_PURPLE_WHITE_2:
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 4, 90, 15, 4, 230)


        elif style.lower() == Line_Style.TURQUOISE_BLACK:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            set_color_for_spaces_on_tbl(self, 44, 44, 234, 234, 231)




        #    +-------------------------------------------------------------------------+
        #    |    This option is when we don't want any type of lines.                 |
        #    |    Only empty spaces as lines and colors                                |
        #    |-------------------------------------------------------------------------|
        #    |    This option is for the user to create its own customization          |
        #    |    The user needs to set the colors manually                            |
        #    |    Remember: set_bg_list_on = False                                     |
        #    +-------------------------------------------------------------------------+
        elif style.lower() == Line_Style.SINGLE_SPACE:
            make_single_empty_space_on_tbl(self)

        elif style.lower() == Line_Style.DOUBLE_SPACE:
            make_double_empty_space_on_tbl(self)

        elif style.lower() == Line_Style.CUSTOMIZED: pass

    #    +------------------------------------------------------------------------------+
    #    |    Color Design Template, Demos                                              |
    #    |    The following are some predesign (Design 1)                               |
    #    |                                                                              |
    #    |    design_color(self, 0_fg_lines,     1_bg_top     2_under,                  |
    #    |                       3_bg_bottom,    4_bg_vertical                          |
    #    |                                                                              |
    #    +------------------------------------------------------------------------------+
        elif style.lower() == Line_Style.DESIGN_1:
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = True
            self.middle_vertical_line_on   = True

            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.vertical_line_bg          = self.design_color
            self.inner_corner_bg           = self.design_color
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.design_color
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_2:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = True
            self.middle_vertical_line_on   = True
            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False

            self.horizontal_line_bg          = self.design_color
            self.outer_corner_bg             = self.design_color
            self.inner_corner_bg             = self.design_color
            self.vertical_line_bg            = self.header_bg
            self.header_vertical_line_bg     = self.header_bg
            self.header_horizontal_line_bg   = self.header_bg
            self.header_corner_bg            = self.header_bg

        elif style.lower() == Line_Style.DESIGN_3:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = False
            self.bottom_horizontal_line_on = False
            self.middle_vertical_line_on   = True
            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False

            self.vertical_line_bg            = self.design_color
            self.header_vertical_line_bg     = self.header_bg
            self.header_horizontal_line_bg   = self.header_bg
            self.header_corner_bg            = self.header_bg


        elif style.lower() == Line_Style.DESIGN_4:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = False
            self.left_vertical_line_on     = True
            self.middle_vertical_line_on   = True
            self.right_vertical_line_on    = True
            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = True

            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.header_bg
            self.header_vertical_line_bg   = self.header_bg
            self.header_horizontal_line_bg = self.design_color
            self.header_corner_bg          = self.header_bg


        elif style.lower() == Line_Style.DESIGN_5:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = False
            self.left_vertical_line_on     = True
            self.middle_vertical_line_on   = True
            self.right_vertical_line_on    = True
            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = True

            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.header_bg
            self.header_vertical_line_bg   = self.header_bg
            self.header_horizontal_line_bg = self.design_color
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_6:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = False
            self.left_vertical_line_on     = True
            self.middle_vertical_line_on   = True
            self.right_vertical_line_on    = True
            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = True

            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.data_bg
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.design_color
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_7:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = False
            self.left_vertical_line_on     = True
            self.middle_vertical_line_on   = True
            self.right_vertical_line_on    = False

            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False


            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.design_color
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.header_bg
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_8:
            flag_row_col_insert = 1
            make_single_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = False
            self.bottom_horizontal_line_on = True
            self.left_vertical_line_on     = False
            self.middle_vertical_line_on   = True
            self.right_vertical_line_on    = True

            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False


            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.design_color
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.header_bg
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_9:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = True
            self.bottom_horizontal_line_on = False
            self.left_vertical_line_on     = True
            self.middle_vertical_line_on   = False
            self.right_vertical_line_on    = False

            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False


            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.design_color
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.header_bg
            self.header_corner_bg          = self.design_color


        elif style.lower() == Line_Style.DESIGN_10:
            flag_row_col_insert = 1
            make_double_empty_space_on_tbl(self)
            self.top_horizontal_line_on    = False
            self.bottom_horizontal_line_on = True
            self.left_vertical_line_on     = False
            self.middle_vertical_line_on   = False
            self.right_vertical_line_on    = True

            self.middle_horizontal_line_on = False
            self.header_horizontal_line_on = False


            self.horizontal_line_bg        = self.design_color
            self.outer_corner_bg           = self.design_color
            self.inner_corner_bg           = self.design_color
            self.vertical_line_bg          = self.design_color
            self.header_vertical_line_bg   = self.design_color
            self.header_horizontal_line_bg = self.header_bg
            self.header_corner_bg          = self.design_color

        else:
            make_single_empty_space_on_tbl(self)
            self.horizontal_line_bg        = -1
            self.outer_corner_bg           = -1
            self.inner_corner_bg           = -1
            self.header_corner_bg          = -1
            self.header_horizontal_line_bg = -1
            self.header_vertical_line_bg   = -1
            self.vertical_line_bg          = -1

            self.horizontal_line_fg        = -1
            self.outer_corner_fg           = -1
            self.inner_corner_fg           = -1
            self.header_corner_fg          = -1
            self.header_horizontal_line_fg = -1
            self.header_vertical_line_fg   = -1
            self.vertical_line_fg          = -1

            self.horizontal_line_bold        = False
            self.outer_corner_bold           = False
            self.inner_corner_bold           = False
            self.header_corner_bold          = False
            self.header_horizontal_line_bold = False
            self.header_vertical_line_bold   = False
            self.vertical_line_bold          = False

            self.header_bg = -1
            self.header_fg = -1
            self.header_bold = -1
            self.data_bg = -1
            self.data_fg = -1
            self.data_bold = -1



        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Hiding Vertical Lines                                                                                                                      -
        #---------------------------------------------------------------------------------------------------------------------------------------------
        if  self.right_vertical_line_on == False:
            self.top_right_corner_chr = ""                 # 14
            self.header_right_vertical_line_chr = ""       # 23
            self.header_right_corner_chr  = ""             # 25
            self.right_vertical_line_chr  = ""             # 12
            self.right_lateral_corner_chr = ""             # 28
            self.bottom_right_corner_chr  = ""             # 15

        if  self.left_vertical_line_on == False:
            self.top_left_corner_chr = ""                  # 13
            self.header_left_vertical_line_chr = ""        # 22
            self.header_left_corner_chr  = ""              # 24
            self.left_vertical_line_chr  = ""              # 11
            self.left_lateral_corner_chr = ""              # 27
            self.bottom_left_corner_chr  = ""              # 16

        if self.middle_vertical_line_on == False:
            self.middle_top_corner_chr = ""                # 17
            self.header_middle_vertical_line_chr = ""      # 29
            self.header_middle_corner_chr = ""             # 30
            self.middle_vertical_line_chr = ""             # 18
            self.middle_inner_corner_chr  = ""             # 31
            self.middle_bottom_corner_chr = ""             # 19


        #---------------------------------------------------------------------------------------------------------------------------------------------
        # Checking the list_type                                                                                                                     -
        #---------------------------------------------------------------------------------------------------------------------------------------------
        if list_type == "empty_list":                   # []
            data_list.append(" ")
            print_single_element(self,data_list)


        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "one_item_no_row":              # ["one"]
            my_list = [str(data_list[0])]
            print_single_element(self,my_list)

            if self.update_list == True and (isinstance (data, list)):     #  updte the list
                data_list[0] = str(data_list[0][0])

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "one_item_one_row":             # [["one"]]
            my_list = [str(data_list[0][0])]
            print_single_element(self,my_list)

            if self.update_list == True and (isinstance (data, list)):     #  updte the list
                data_list[0] = str(data_list[0][0])

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "multiple_items_one_row":       # [[1,2,3,4]]
            # we need to convert from one row many cols to many cols and no row
            # also convert the elements in my_list to string. all of them
            for row in data_list:
                for n in row:
                    my_list.append(str(n))

            print_multiple_horizontal_items(self,my_list)

            # if we want to save the new list to into the old one as string
            if self.update_list == True and (isinstance (data, list)):
                data_list.clear()
                for n in my_list:
                    data_list.append(n)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "multiple_items_no_row":        # [1,2,3,4]
            # also convert the elements in my_list to string. all of them
            for n in (data_list):
                my_list.append(str(n))

            print_multiple_horizontal_items(self,my_list)

            # if we want to save the new list to into the old one as string
            if self.update_list == True and (isinstance (data, list)):
                data_list.clear()
                for n in my_list:
                    data_list.append(n)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "mix_items":                    # [10,[50],[250],["H"],100]
                                                          # "C",["H","K","P","o"]]
           # also convert the elements in my_list to string. all of them
            for n in (data_list):
                my_list.append(str(n))

            print_multiple_horizontal_items(self,my_list)

            # if we want to save the new list to into the old one as string
            if self.update_list == True and (isinstance (data, list)):
                data_list.clear()
                for n in my_list:
                    data_list.append(n)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        elif list_type == "multiple_items_multiple_rows":  # [[7,6],[5,4],[1,2,3]] or [[2],[3],[5]]
            # converting the data_list to string any single element into my_list
            # save the new matrix my_list and now we need to complete the matrix if necessary
            tempo_list1 = []; tempo_list2 = []
            for row in data_list:
                for col in row:
                    tempo_list1.append(str(col))
                tempo_list2.append(tempo_list1)
                tempo_list1 = []


            if flag_row_col_insert == 1:
                tempo_row = [" "];        self.set_fill_chr = " "
                tempo_list2.insert(1,tempo_row); tempo_list2.append(tempo_row)

                my_list = complete_info_list(self,tempo_list2)  # make the list complete
                print_matrix_list(self,my_list)                 # print list

                # putting back as original
                my_list.pop(1);    last = len(my_list) - 1;    my_list.pop(last)

            else:
                my_list = complete_info_list(self,tempo_list2)  # make the list complete
                print_matrix_list(self,my_list)



              # if we want to save the new list to into the old one as string
            if self.update_list == True and (isinstance (data, list)):
                data_list.clear()
                for n in my_list:
                    data_list.append(n)

        #---------------------------------------------------------------------------------------------------------------------------------------------
        else:
            print(list_type+": ",data_list)
        #--------------------------------------------------------------------------------------------------------------------------------------------+
        #                                                                                                                                            |
        #    Putting back all the default values                                                                                                     |
        #                                                                                                                                            |
        #--------------------------------------------------------------------------------------------------------------------------------------------+
        # Horizontal Line Section                       # Vertical Line Section
        self.top_horizontal_line_chr    = thlc;         self.left_vertical_line_chr   = lvlc
        self.bottom_horizontal_line_chr = bhlc;         self.middle_vertical_line_chr = mvlc
        self.middle_horizontal_line_chr = hlc;          self.right_vertical_line_chr  = rvlc

        # Corner Section
        self.top_left_corner_chr  = tlcc;               self.bottom_right_corner_chr = brcc
        self.top_right_corner_chr = trcc;               self.bottom_left_corner_chr  = blcc

        self.middle_top_corner_chr    = mtcc;           self.right_lateral_corner_chr = rlcc
        self.middle_bottom_corner_chr = mbcc;           self.left_lateral_corner_chr  = llcc
        self.middle_inner_corner_chr  = micc

        # Header Section  Only for Matrix List          attributes for the header corners (left, middles and right)
        self.header_left_vertical_line_chr   = lvhlc;   self.header_left_corner_chr   = lculhc
        self.header_right_vertical_line_chr  = rvhlc;   self.header_right_corner_chr  = rculhc
        self.header_middle_vertical_line_chr = mvhlc;   self.header_middle_corner_chr = mculhc

        # Under Line Header Section  Only for Matrix List
        self.header_horizontal_line_chr = hluhc

        # Colors
        self.header_bg = bg_H
        self.header_fg = fg_H

        self.data_bg = bg_D
        self.data_fg = fg_D

        self.horizontal_line_bg        = bg_hl
        self.outer_corner_bg           = bg_cc
        self.inner_corner_bg           = bg_ic
        self.header_horizontal_line_bg = bg_ulh
        self.vertical_line_bg          = bg_vl
        self.header_vertical_line_bg   = bg_vhlc
        self.header_corner_bg          = bg_culh

        self.horizontal_line_fg        = fg_hl
        self.outer_corner_fg           = fg_cc
        self.vertical_line_fg          = fg_vl
        self.inner_corner_fg           = fg_ic
        self.header_vertical_line_fg   = fg_vhl
        self.header_horizontal_line_fg = fg_ulh
        self.header_corner_fg          = fg_culh

        # Line ON
        self.top_horizontal_line_on    = thlo
        self.middle_horizontal_line_on = mhl0
        self.bottom_horizontal_line_on = bhlo
        self.right_vertical_line_on    = rvlo
        self.left_vertical_line_on     = lvlo
        self.middle_vertical_line_on   = mvlo
        self.header_horizontal_line_on = hluho

        # Bold_lines
        self.header_corner_bold          = bculh
        self.header_horizontal_line_bold = bulh
        self.header_vertical_line_bold   = bvhl
        self.inner_corner_bold           = bic
        self.outer_corner_bold           = bc
        self.vertical_line_bold          = bvl
        self.horizontal_line_bold        = bhl

        # fill chr
        self.set_fill_chr = fill_c
