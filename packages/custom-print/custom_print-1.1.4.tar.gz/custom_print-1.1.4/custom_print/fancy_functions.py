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
import os
from custom_print.ref_names import COLOR_NAMES

#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Screen Functions Windows and Linux                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Clean the Terminal (Windows)                                                                                                                       -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def clean():

    ''' It cleans the terminal and returns the cursor to home. '''
    # Ansi Code
    print("\033[2J",end="")  # clean the terminal
    print("\033[H",end="")   # return home the cursor


if os.name == 'nt' and (platform.release() == '10' or platform.release() == "11"):
    OS_Windows = True
    OS_Linux = False
    # Fix ANSI color in Windows 10 version 10.0.14393 (Windows Anniversary Update)
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Clear the Terminal (Windows)                                                                                                                   -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def clear():

        '''  It cleans the terminal and returns the cursor to home.  '''

        os.system("cls")

    # it may disable the scroll bar on the Command Prompt or the Windows PowerShell
    # to enable the scroll bar, got to Properties-> Layout-> Screen Buffer Size-> Set Height to 1000
    # use Command Prompt or Windows PowerShell
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Resize the Terminal (Windows)                                                                                                                  -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def resize(rows:int=25, cols:int=80)->None:

        '''  It resizes the terminal size.  '''

        #os.system(f"mode con:cols={cols} lines={rows}")
        os.system(f"mode {cols}, {rows}")


elif os.name == 'posix':
    OS_Windows = False
    OS_Linux = True
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Clear the Terminal (Linux)                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def clear():

        '''  It cleans the terminal and returns the cursor to home.  '''

        os.system("clear")

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Resize the Terminal (Linux)                                                                                                                    -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def resize(rows:int=25, cols:int=80)->None:

        '''  It resizes the terminal size.  '''

        os.system(f"resize -s {rows} {cols}")


else:
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Clean the Terminal (Other)                                                                                                                         -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
    def clear():

        '''  It cleans the terminal and returns the cursor to home.  '''

        print("\033[2J",end="")  # clean the terminal
        print("\033[H",end="")   # return home the cursor

    def resize(rows:int=25, cols:int=80)->None:

        '''  It resizes the terminal size.  '''

        os.system(f"resize -s {rows} {cols}")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Returns the Terminal) Dimensions                                                                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def dimensions():

    '''  It returns the dimensions of the terminal: cols, rows = dimensions()  '''

    cols, rows = os.get_terminal_size()
    return cols, rows



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Erase the Terminal                                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def erase():

    '''  It erases the terminal and leaves the cursor in the current position  '''

    print("\033[2J",end="")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Linux Background Color Option List                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def bg_ansi_colors(bold=False, fg=-1, n_line=0):

    '''  This function displays all background colors available with ansi code  '''

    reset = "\033[0m"
    space = "   "
    ctrl  = 0

    if fg < 0 or fg > 256: fg_color = "-1"
    else:                  fg_color = str(fg)

    if bold == True: b = "1"
    else:            b = "0"

    for color in range(257):
        if color <= 9:                    space = "   "
        elif color <= 99 and color >=10:  space = "  "
        else:                             space = " "

        if ctrl <= 1:
            ctrl += 1
            if fg_color == "-1":
                print(f"\033[{b};48;5;{color}m {COLOR_NAMES[color]} {reset}{color}",end=space)
            else:
                print(f"\033[{b};48;5;{color};38;5;{fg_color}m {COLOR_NAMES[color]} {reset}{color}",end=space)
        else:
            ctrl = 0
            if fg_color == "-1":
                if n_line > 0:
                    print(f"\033[{b};48;5;{color}m {COLOR_NAMES[color]} {reset}{color}")
                    ins_newline(n_line)
                else:
                    print(f"\033[{b};48;5;{color}m {COLOR_NAMES[color]} {reset}{color}")

            else:
                if n_line > 0:
                    print(f"\033[{b};48;5;{color};38;5;{fg_color}m {COLOR_NAMES[color]} {reset}{color}")
                    ins_newline(n_line)
                else:
                    print(f"\033[{b};48;5;{color};38;5;{fg_color}m {COLOR_NAMES[color]} {reset}{color}")

    print("\x1B[0m  bg default color  -1")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Linux Foreground Color Option List                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def fg_ansi_colors(bold=False, bg=-1, n_line=0):

    '''  This function displays all foreground colors available with ansi code  '''

    reset = "\033[0m"
    space = "   "
    ctrl  = 0

    if bg < 0 or bg > 256: bg_color = "-1"
    else:                  bg_color = str(bg)

    if bold == True: b = "1"
    else:            b = "0"

    for color in range(257):
        if color <= 9:
            space = "   "
        elif color <= 99 and color >=10:
            space = "  "
        else:
            space = " "

        if ctrl <= 1:
            ctrl += 1
            if bg_color == "-1":
                print(f"\033[{b};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}",end=space)
            else:
                print(f"\033[{b};48;5;{bg_color};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}",end=space)
        else:
            ctrl = 0
            if bg_color == "-1":
                if n_line > 0:
                    print(f"\033[{b};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}")
                    ins_newline(n_line)
                else:
                    print(f"\033[{b};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}")
            else:
                if n_line > 0:
                    print(f"\033[{b};48;5;{bg_color};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}")
                    ins_newline(n_line)
                else:
                    print(f"\033[{b};48;5;{bg_color};38;5;{color}m {COLOR_NAMES[color]} {reset}{color}")

    print("\x1B[0m  fg default color  -1")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Terminal Sounds                                                                                                                                    -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def terminal_bell():

    '''  This function makes sound of the terminal bell
         terminal_bell()
           '''

    print("\a")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Insert A Unicode Character n Times                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def ins_chr(n=1, unicode=" "):

    '''  This function inserts n times the unicode provided
         ins_chr(n=x, unicode=" ")  '''

    sp = str(unicode)

    space = ""
    while n > 0:
        space += sp
        n -= 1
    return space



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Insert n Newlines                                                                                                                                  -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def ins_newline(n=1):

    '''  This function inserts n new lines
         ins_newline(n=1)  '''

    while n > 0:
        n -= 1
        print("")



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Move Cursor to the Right. This function is used as the indentation for the print                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def move_cursor_right(n=0,option_space=False):

    '''  This function moves the cursor n spaces to the right.  '''

    if option_space == True:
        sp = ins_chr(n)
    else:
        if n == 0:
            sp = ""
        else:
            sp = f"\033[{str(n)}C"
    return sp



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Set Settings for the Font: Bold, Background, and Foreground                                                                                        -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def set_font(bold=False,bg=-1,fg=-1,italic=False,underline=False,strike=False,blinking=False,dim=False,hidden=False,inverse=False):

    '''  This function changes the attributes of the font (bold, bg, fg).

          set_font(bold=bool, bg=int, fg=int)

          Colors range from -1 to 256.
          To set the default color use -1 or 256.  '''

    # bg_color and fg_color, are int values but we convert then to str values
    reset = "\033[0m"

    if bg < 0 or bg > 255:  bgc = "reset"
    else:                   bgc = str(bg)

    if fg < 0 or fg > 255:  fgc = "reset"
    else:                   fgc = str(fg)


    if   bgc == "reset" and fgc == "reset":  settings = reset
    elif bgc == "reset" and fgc != "reset":  settings = reset+"\033[38;5;"+fgc+"m"
    elif bgc != "reset" and fgc == "reset":  settings = reset+"\033[48;5;"+bgc+"m"
    elif bgc != "reset" and fgc != "reset":  settings = reset+"\033[48;5;"+bgc+";38;5;"+fgc+"m"
    else:                                    settings = reset


    if   bold == True  and dim == False:  settings = settings + "\033[1m"
    elif bold == True  and dim == True:   settings = settings + "\033[1m"
    elif bold == False and dim == True:   settings = settings + "\033[2m"
    else:                                   pass  # (bold == False and dim == False):

    if italic == True:    settings = settings + "\033[3m"
    else:                 settings = settings + "\033[23m"

    if underline == True: settings = settings + "\033[4m"
    else:                 settings = settings + "\033[24m"

    if blinking == True:  settings = settings + "\033[5m"
    else:                 settings = settings + "\033[25m"

    if hidden == True:    settings = settings + "\033[8m"
    else:                 settings = settings + "\033[28m"

    if strike == True:    settings = settings + "\033[9m"
    else:                 settings = settings + "\033[29m"

    if inverse == True:   settings = settings + "\033[7m"
    else:                 settings = settings + "\033[27m"

    return settings



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Reset Settings for the Font: Bold, Background, and Foreground                                                                                      -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def reset_font():

    '''  This function resets the font attributes to the default ones.  '''

    return "\033[0m"



#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Get List Type                                                                                                                                      -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def get_list_type(my_list):
    '''
        getting the type of list
    '''
    if not isinstance(my_list, list):
        return "incorrect_variable_type"                # [Not a List] Case 0
    #-------------------------------------------------------------------------------------------------------------------------------------------------

    if len(my_list) == 0:
        return "empty_list"                             # []    Case 1

    #-------------------------------------------------------------------------------------------------------------------------------------------------

    if len(my_list) == 1:
        if isinstance(my_list[0], list):
            if len(my_list[0]) > 1:
                return "multiple_items_one_row"         # [[1,2,3]]   Case 5
            else:
                return "one_item_one_row"               # [[1]]  Case 4
        else:
            return "one_item_no_row"                    # [1]   Case 2

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    if len(my_list) > 1:
        items = 0; rows = 0
        for n in my_list:
            if not isinstance(n, list):
                items = 1
            else:
                rows = 1

        if (items ==  1 and rows == 0):
            return "multiple_items_no_row"              #  [1,2,3]                      Case 3
        elif (items == 0 and rows == 1):
            return  "multiple_items_multiple_rows"      # [[1],[4],[7]]                 Case 6
                                                        # [[1,2,3],[4,5,6],[7,8,9]]     Case 6
                                                        # [[1],[1,2,3],[5,4,7,8]]       Case 6
                                                        # any combination of this is    Case 6
                                                        # [[1,2,3],[[2],3,4],[5,[6,7]]] Case 6
        else:
            return "mix_items"                          # [5,6,[1,2,3],[1,0,3]]         Case 7
                                                        # [[1,2],[1,2,[1]],[1,2,3]]     Case 7
                                                        # any combination of this is    Case 7


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Subscript Letter                                                                                                                                   -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def subscript(number):
    '''
        subscript form
    '''
    subscript_map = {
        'a' : '\u2090',    'b' : '?',         'c' : '?',         'd' : '?',         'e' : '\u2091',
        'f' : '?',         'g' : '?',         'h' : '\u2095',    'i' : '\u1d62',    'j' : '\u2c7c',
        'k' : '\u2096',    'l' : '\u2097',    'm' : '\u2098',    'n' : '\u2099',    'o' : '\u2092',
        'p' : '\u209a',    'q' : '?',         'r' : '\u1d63',    's' : '\u209b',    't' : '\u209c',
        'u' : '\u1d64',    'v' : '\u1d65',    'w' : '?',         'x' : '\u2093',    'y' : '?',                        
        'z' : '?',

        'A' : '?',         'B' : '?',         'C' : '?',         'D' : '?',         'E' : '?',
        'F' : '?',         'G' : '?',         'H' : '?',         'I' : '?',         'J' : '?',
        'K' : '?',         'L' : '?',         'M' : '?',         'N' : '?',         'O' : '?',
        'P' : '?',         'Q' : '?',         'R' : '?',         'S' : '?',         'T' : '?',
        'U' : '?',         'V' : '?',         'W' : '?',         'X' : '?',         'Y' : '?',
        'Z' : '?',

        '0' : '\u2080',    '1' : '\u2081',    '2' : '\u2082',    '3' : '\u2083',    '4' : '\u2084',
        '5' : '\u2085',    '6' : '\u2086',    '7' : '\u2087',    '8' : '\u2088',    '9' : '\u2089',

        '+' : '\u208A',    '-' : '\u208B',    '=' : '\u208C',    '(' : '\u208D',    ')' : '\u208E',

        ':alpha'  : '?',
        ':beta'   : '\u1d66',
        ':gamma'  : '\u1d67', 
        'delta'   : '?'     , 
        'epsilon' : '?'     , 
        'theta'   : '?'     ,
        'iota'    : '?'     ,
        'pho'     : '\u1d68',
        'phi'     : '?'     ,
        'psi'     : '\u1d69',
        'chi'     : '\u1d6a',
    }


    subscript_string = ""
    for digit in str(number):
        if digit not in subscript_map:
            subscript_string += "?" # If symbols digit not in the map then set to ? by the default
        else:
            subscript_string += subscript_map.get(digit, digit) # Fallback for non-digits
    return subscript_string


#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Superscript Letter                                                                                                                                 -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
def superscript(number):
    '''
        superscript form
    '''
    superscript_map = {

        'a' : '\u1d43',   'b' : '\u1d47',   'c' : '\u1d9c',   'd' : '\u1d48',   'e' : '\u1d49',
        'f' : '\u1da0',   'g' : '\u1d4d',   'h' : '\u02b0',   'i' : '\u2071',   'j' : '\u02b2',
        'k' : '\u1d4f',   'l' : '\u02e1',   'm' : '\u1d50',   'n' : '\u207f',   'o' : '\u1d52',
        'p' : '\u1d56',   'q' : '?',        'r' : '\u02b3',   's' : '\u02e2',   't' : '\u1d57',
        'u' : '\u1d58',   'v' : '\u1d5b',   'w' : '\u02b7',   'x' : '\u02e3',   'y' : '\u02b8',
        'z' : '?',

        'A' : '\u1d2c',    'B' : '\u1d2e',    'C' : '?',         'D' : '\u1d30',    'E' : '\u1d31',
        'F' : '?',         'G' : '\u1d33',    'H' : '\u1d34',    'I' : '\u1d35',    'J' : '\u1d36',
        'K' : '\u1d37',    'L' : '\u1d38',    'M' : '\u1d39',    'N' : '\u1d3a',    'O' : '\u1d3c',
        'P' : '\u1d3e',    'Q' : '?',         'R' : '\u1d3f',    'S' : '?',         'T' : '\u1d40',
        'U' : '\u1d41',    'V' : '\u2c7d',    'W' : '\u1d42',    'X' : '?',         'Y' : '?',     
        'Z' : '?',              

        '0' : '\u2070',    '1' : '\u00B9',    '2' : '\u00B2',    '3' : '\u00B3',    '4' : '\u2074',
        '5' : '\u2075',    '6' : '\u2076',    '7' : '\u2077',    '8' : '\u2078',    '9' : '\u2079',

        '+' : '\u207A',    '-' : '\u207B',    '=' : '\u207C',    '(' : '\u207D',    ')' : '\u207E',

        'alpha'   : '\u1d45',
        'beta'    : '\u1d5d', 
        'gamma'   : '\u1d5e', 
        'delta'   : '\u1d5f', 
        'epsilon' : '\u1d4b', 
        'theta'   : '\u1dbf',
        'iota'    : '\u1da5',
        'pho'     : '?',     
        'phi'     : '\u1db2',
        'psi'     : '\u1d60',
        'chi'     : '\u1d61',
        'coffee'  : '\u2615',
    }

    superscript_string = ""
    for digit in str(number):
        if digit not in superscript_map:
            superscript_string += "?"     # If symbols digit not in the map then set to ? by the default
        else:
            superscript_string += superscript_map.get(digit, digit) # Fallback for non-digits
    return superscript_string
