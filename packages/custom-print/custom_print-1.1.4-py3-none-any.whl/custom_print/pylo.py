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
#from typing import Union
import os              # PyLO class
import csv             # PyLO class
import json            # PyLO class
import enum            # PyLO class
import typing          # To define in the function type of arguments that are accepted

from custom_print.ref_names import Move
from custom_print.ref_names import Layout
from custom_print.fancy_functions import get_list_type
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Python List Operation Functions (PyLO)                                                                                                             -
#-----------------------------------------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Class PyLO. Operation With List Personal                                                                                                          --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
class PyLO():
    '''
    PyLO class helps to make some quick operations with list in python
    '''
    class Str_List_Option(enum.StrEnum):

        '''  How the string is converted to list.  '''

        WORD_BY_WORD = "word_by_word"
        LINE_BY_LINE = "line_by_line"


    class Appending(enum.StrEnum):

        '''  How the two list will be merge. '''

        ROWS    = "rows"
        COLUMNS = "columns"


    class Order(enum.StrEnum):

        ''' how the order of the list will take priority  '''

        ASCENDING  = "ascending"
        DESCENDING = "descending"


    class Case(enum.StrEnum):

        '''  Defines what part of the list will be converted to a specific type of case.  '''

        UPPER = "upper"
        LOWER = "lower"
        CAPITALIZE = "capitalize"
        NONE = "none"


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Conversion to List                                                                                                                             -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def _bifc_to_list(self,data, convert_to_str=False):
        '''  It converts bool, int, float, and complex type to list type  '''
        tempo_list = []
        if convert_to_str == True:
            tempo_list.append(str(data))
        else:
            tempo_list.append(data)
        return tempo_list


    def bool_to_list(self,data:bool, convert_to_str=False):
        '''  It sets a bool variable into list as a bool or as string type  '''
        new_list = PyLO._bifc_to_list(self, data, convert_to_str)
        return new_list


    def int_to_list(self,data:int, convert_to_str=False):
        '''  It sets a int variable into list as an integer or as string type  '''
        new_list = PyLO._bifc_to_list(self, data, convert_to_str)
        return new_list


    def float_to_list(self,data:float, convert_to_str=False):
        '''  It sets a float variable into list as a float or as string type  '''
        new_list = PyLO._bifc_to_list(self, data, convert_to_str)
        return new_list


    def complex_to_list(self,data:complex, convert_to_str=False):
        '''  It sets a complex variable into a list as a complex or as string type   '''
        new_list = PyLO._bifc_to_list(self, data, convert_to_str)
        return new_list

    #---------------------------------------------------------------------------------------------------------------------------------------------
    def str_to_list(self,data:str, option:Str_List_Option=Str_List_Option.WORD_BY_WORD, counter=False):

        '''  It sets a string variable into a list as word by word or line by line  '''

        if option == "word_by_word" and counter == False:
            tempo_list = data.split()

        elif option == "word_by_word" and counter == True:
            cnt = 0
            tempo_list = []
            tempo = data.split()
            for w in tempo:
                tempo_list.append([cnt,w])
                cnt += 1

        elif option == "line_by_line":
            cnt = -1
            line_word = ""
            tempo_list = []
            for l in data:
                if l != "\n":
                    line_word += l
                else:
                    if cnt == -1:
                        cnt = 0
                    else:
                        if counter == True:
                            tempo_list.append([cnt,line_word])
                            cnt += 1
                            line_word = ""
                        else:
                            tempo_list.append(line_word)
                            cnt += 1
                            line_word = ""
        else:
            tempo_list = []

        return tempo_list


    #---------------------------------------------------------------------------------------------------------------------------------------------
    def dict_to_list(self,data:dict, key_title="key", value_title="value", convert_to_str=False):
        '''  It sets a dictionary variable into a list with its original values or as string values   '''

        my_key_list = []; my_data_list = []

        my_key_list  = list(data.keys())
        my_data_list = list(data.values())

        complete_list = [];  tempo_list = []
        if (key_title == "key") and (value_title == "value"):
            if (len(my_key_list)) > 1:   complete_list.append(["Keys","Values"])
            else:                        complete_list.append(["Key","Value"])

        elif (key_title == None or value_title == None or \
                key_title.lower() == "none" or value_title.lower() == "none"):
            pass

        else:
            complete_list.append([key_title,value_title])

        for d in range(len(data)):
            if convert_to_str == True:
                tempo_list.append(str(my_key_list[d]))
                tempo_list.append(str(my_data_list[d]))
                complete_list.append(tempo_list)
                tempo_list = []
            else:
                tempo_list.append(my_key_list[d])
                tempo_list.append(my_data_list[d])
                complete_list.append(tempo_list)
                tempo_list = []

        return complete_list


    #---------------------------------------------------------------------------------------------------------------------------------------------
    def range_to_list(self, data:range, header_title = "", layout:Layout=Layout.HORIZONTAL, convert_to_str=False):
        '''  It sets a range variable into a list with its original values or as string values   '''

        tempo_list = []

        def range_to_list_get_header(layout):
            header = "Range"
            if header_title == "":
                if len(data) > 1:
                    if layout == "vertical": tempo_list.append([header + " Values"])
                    else:                    tempo_list.append(header  + " Values")

                else:
                    if layout == "vertical": tempo_list.append([header + " Value"])
                    else:                    tempo_list.append(header  + " Value")

            elif (header_title == None or header_title.lower() == "none"):
                pass
            else:
                if layout == "vertical":  tempo_list.append([header_title])
                else:                     tempo_list.append(header_title)

        #for n in data:
        if (layout.lower() == "v" or layout == Layout.VERTICAL):
            range_to_list_get_header("vertical")
            for n in data:
                if convert_to_str == False:  tempo_list.append([n])
                else:                        tempo_list.append([str(n)])

        elif (layout.lower() == "h" or layout == Layout.HORIZONTAL):
            range_to_list_get_header("horizontal")
            for n in data:
                if convert_to_str == False:  tempo_list.append(n)
                else:                        tempo_list.append(str(n))

        else: pass

        return tempo_list


    #---------------------------------------------------------------------------------------------------------------------------------------------
    # set and frozenset values are printed in aleatory order all the time
    def set_to_list(self, data:set|frozenset, header_title:str="",layout:Layout=Layout.VERTICAL, convert_to_str=False):
        '''  It sets a set or a frozenset variable into a list with its original values or as string values   '''

        tempo_list = []

        #----------------------------------------------------------------------------------
        def _set_to_list_get_header(layout):
            if isinstance(data, set):       header = "Set"
            if isinstance(data, frozenset): header = "Frozenset"

            if header_title == "":
                if len(data) > 1:
                    if layout == "vertical": tempo_list.append([header + " Values"])
                    else:                    tempo_list.append(header  + " Values")

                else:
                    if layout == "vertical": tempo_list.append([header + " Value"])
                    else:                    tempo_list.append(header  + " Value")

            elif (header_title == None or header_title.lower() == "none"):
                pass
            else:
                if layout == "vertical":  tempo_list.append([header_title])
                else:                     tempo_list.append(header_title)

        #----------------------------------------------------------------------------------
        def _set_to_list_layout_vertical():
            _set_to_list_get_header("vertical")

            for d in data:
                if convert_to_str == False:  tempo_list.append([d])
                else:                        tempo_list.append([str(d)])


        def _set_to_list_layout_horizontal():
            _set_to_list_get_header("horizontal")

            for d in data:
                if convert_to_str == False:  tempo_list.append(d)
                else:                        tempo_list.append(str(d))

        #----------------------------------------------------------------------------------
        if (layout.lower() == "v"   or layout.lower() == Layout.VERTICAL):
            _set_to_list_layout_vertical()

        elif (layout.lower() == "h" or layout.lower() == Layout.HORIZONTAL):
            _set_to_list_layout_horizontal()

        else: pass

        return tempo_list



    #---------------------------------------------------------------------------------------------------------------------------------------------
    def tuple_to_list(self, data:tuple):
        '''  This function converts a tuple into a list keeping its original values '''
        tempo_list = []
        #-----------------------------------------------------------------------------------------------
        if len(data) == 0:
            return tempo_list

        #-----------------------------------------------------------------------------------------------
        elif len(data) == 1:
                                        # string              ("")         -> Case 0   String
                                        # "empty_tuple"       ("",)        -> Case 1   Empty
            tempo_list.append(data[0])  # "one_item_no_row"   ("Apple",)   -> Case 2   Tuple
            return tempo_list           # "one_item_one_row"  (("Apple",)) -> Case 3   Tuple inside Tuple

        #-----------------------------------------------------------------------------------------------
        #elif len(data) > 1:
        else:
            type_type = []; lengths = []
            l = len(data); tuple_tuple = 0; tuple_other = 0

            for n in range(len(data)):
                if isinstance(data[n], tuple):
                    tuple_tuple = 1
                    type_type.append("tuple")
                    lengths.append(len(data[n]))

                else:
                    tuple_other = 1
                    type_type.append("other")
                    lengths.append(1)

            # This is only for tuples inside the tuple ->
            # tupleData = (("hello","hello"),("hell",),("hi","bye","good"),([1,2],))        -> Case 4
            if (tuple_tuple == 1 and tuple_other == 0):
                tempo = []
                for col in data:
                    for i in col:
                        tempo.append(i)
                        tempo_list.append(tempo)
                        tempo = []

            # This is only for other types inside a tuple
            # tupleData = ("hello","hell","hi",[1,2])                                       -> Case 5
            elif (tuple_tuple == 0 and tuple_other == 1):
                for n in data:
                    tempo_list.append(n)     # for rows (Horizontal)
                    #tempo_list.append([n])  # for cols (Vertical)


            # This is for combination tuple (tuple =1 and other = 1)                        -> Case 6
            # tupleData = (("hello","hello"),("hell",),("hi","bye","good"),[1,2], "hello")
            elif (tuple_tuple == 1 and tuple_other == 1):
                for n in range(l):
                    if (lengths[n]) > 1:
                        tempo = []
                        for i in range(lengths[n]):
                            tempo.append(data[n][i])
                        tempo_list.append(tempo)

                    else:
                        if type_type[n] == "other":
                            tempo_list.append([data[n]])
                        else:
                            tempo_list.append([data[n][0]])
            else:
                tempo_list = []

        return tempo_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Shift An Element Inside A List, RIGHT or LEFT                                                                                                  -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def right_shift(self,my_list:list, qty:int=0, update:bool=False)->list:
        '''
        This function shift the elements in a list to the right.

        update is used to save the actual list with the shift elements.
        update is set to False is we wish to keep the original list and save
        the new list into another variable.
        '''
        list_type = get_list_type(my_list)

        # list_type = incorrect_variable_type: [Not a list type variable]
        if list_type == "incorrect_variable_type":
            return my_list
        # list_type = empty_list: []
        elif list_type == "empty_list":
            return my_list

        # list_type = one_item_no_row: ["one"]
        elif list_type == "one_item_no_row":
            return my_list

        # list_type = one_item_one_row: [["one"]]
        elif list_type == "one_item_one_row":
            return my_list

        # list_type == "multiple_items_no_row"          [1,2,3,4]
        # list_type == "multiple_items_multiple_rows"   [[7,6],[5,4],[1,2,3]] or [[2],[3],[5]]
        # list_type == "mix_items"                      [10,[50],[250],["H"],100]
        elif list_type == "multiple_items_no_row" or list_type == "mix_items"\
            or list_type == "multiple_items_multiple_rows":

            result = []; result = my_list; tempo = []

            length = len(result)-1
            for rot in range(qty):
                tempo.append(result[length])
                for n in range(length):
                    tempo.append(result[n])
                result = tempo
                tempo = []

            if update == True:
                my_list.clear()
                for n in result: my_list.append(n)
                return my_list
            else:
                return result

        # list_type = multiple_items_one_row: [[1,2,3,4]]
        elif list_type == "multiple_items_one_row":
            tempo = []; result = []; result = my_list[0]; length = len(result)-1

            for rot in range(qty):
                tempo.append(result[length])
                for n in range(length):
                    tempo.append(result[n])
                result = tempo
                tempo = []

            if update == True:
                my_list.clear()
                for n in result: tempo.append(n)
                my_list.append(tempo)
                return my_list

            else:
                return [result]

        # A different case will just return the same list
        else:
            return my_list

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def left_shift(self, my_list:list, qty=0, update:bool=False)->list:
        '''
        This function shift the elements in a list to the left.

        update is used to save the actual list with the shift elements.
        update is set to False is we wish to keep the original list and save
        the new list into another variable.'''

        list_type = get_list_type(my_list)

        # list_type = incorrect_variable_type: [Not a list type variable]
        if list_type == "incorrect_variable_type":
            return my_list

        # list_type = empty_list: []
        elif list_type == "empty_list":
            return my_list

        # list_type = one_item_no_row: ["one"]
        elif list_type == "one_item_no_row":
            return my_list

        # list_type = one_item_one_row: [["one"]]
        elif list_type == "one_item_one_row":
            return my_list

        # list_type == "multiple_items_no_row"          [1,2,3,4]
        # list_type == "multiple_items_multiple_rows"   [[7,6],[5,4],[1,2,3]] or [[2],[3],[5]]
        # list_type == "mix_items"                      [10,[50],[250],["H"],100]
        elif list_type == "multiple_items_no_row" or list_type == "mix_items"\
            or list_type == "multiple_items_multiple_rows":

            result = []; result = my_list; tempo = []; length = len(result)-2
            for rot in range(qty):
                tempo.append(result[1])
                for n in range(length):
                    idx = n + 2
                    tempo.append(result[idx])
                tempo.append(result[0])
                result = tempo
                tempo = []
            if update == 1:
                my_list.clear()
                for n in result: my_list.append(n)
                return my_list
            else:
                return result

        # list_type = multiple_items_one_row: [[1,2,3,4]]
        elif list_type == "multiple_items_one_row":
            tempo = []; result = []; result = my_list[0]; length = len(result)-2
            for rot in range(qty):
                tempo.append(result[1])
                for n in range(length):
                    idx = n + 2
                    tempo.append(result[idx])
                tempo.append(result[0])
                result = tempo
                tempo = []

            if update == 1:
                my_list.clear()
                for n in result: tempo.append(n)
                my_list.append(tempo)
                return my_list
            else:
                return [result]

        # A different case will just return the same list
        else:
            return my_list

    def shift(self, data:list, direction:str=Move.RIGHT, qty=0, update:bool=False)->list:
        '''
        This function shift the elements in a list to the left or right.

        update is used to save the actual list with the shift elements.
        If we set update to False, then we keep the original list and save
        the new list into another variable.'''

        if direction == "r" or direction == Move.RIGHT:
            tempo = PyLO.right_shift(self, my_list=data, qty=qty, update=update)
        elif direction == "l" or direction == Move.LEFT:
            tempo = PyLO.left_shift(self, my_list=data,  qty=qty, update=update)
        else:
            tempo = data
        return tempo


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Swap Two Items Into A List                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def swap(self, data:list, posi_1=0, posi_2=0, update:bool=False)->list:
        '''
        This function swap two elements in a list.

        update is used to save the actual list with the swap elements.

        If update is set to False, then we keep the original list and save
        the new list into another variable.

        posi_1 -> position 1 to be swap with position 2
        posi_2 -> position 2 to be swap with position 1

        Note: If one of the position provided is out of range, the function
              will return the list as original and it will print a message
              out of range.'''

        if posi_1 == posi_2:
            return data

        else:
            list_type = get_list_type(data)

            # list_type = incorrect_variable_type: [Not a list type variable]
            if list_type == "incorrect_variable_type":
                return data

            # list_type = empty_list: []
            elif list_type == "empty_list":
                return data

            # list_type = one_item_no_row: ["one"]
            elif list_type == "one_item_no_row":
                return data

            # list_type = one_item_one_row: [["one"]]
            elif list_type == "one_item_one_row":
                return data

            # list_type == "multiple_items_no_row"          [1,2,3,4]
            # list_type == "multiple_items_multiple_rows"   [[7,6],[5,4],[1,2,3]] or [[2],[3],[5]]
            # list_type == "mix_items"                      [10,[50],[250],["H"],100]
            elif list_type == "multiple_items_no_row" or list_type == "mix_items"\
                or list_type == "multiple_items_multiple_rows":
                result = []; length = len(data) - 1

                if length < posi_1:
                    print(f" posi_1 = {posi_1} is out of range...! ")
                    return data
                if length < posi_2:
                    print(f" posi_2 = {posi_2} is out of range...! ")
                    return data

                for n in range(len(data)):
                    if n == posi_1:
                        result.append(data[posi_2])
                    elif n == posi_2:
                        result.append(data[posi_1])
                    else:
                        result.append(data[n])

                if update == 1:
                    data.clear()
                    [data.append(n) for n in result]
                    return data
                else:
                    return result

            # list_type = multiple_items_one_row: [[1,2,3,4]]
            elif list_type == "multiple_items_one_row":
                result = []; length = len(data[0]) - 1
                if length < posi_1:
                    print(f" posi_1 = {posi_1} is out of range...! ")
                    return data
                if length < posi_2:
                    print(f" posi_2 = {posi_2} is out of range...! ")
                    return data

                for n in range(len(data[0])):
                    if n == posi_1:
                        result.append(data[0][posi_2])
                    elif n == posi_2:
                        result.append(data[0][posi_1])
                    else:
                        result.append(data[0][n])

                if update == 1:
                    data.clear()
                    [data.append(n) for n in result]
                    return [data]
                else:
                    return result

            else:
                return [data]

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Get Dimensions of a List                                                                                                                       -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def dimensions(self, data:list)->list[int]:
        '''
        dimensions(self, data:list)->list[int]

        This function return the number of rows and cols in a list.
        '''
        n_rows = 0
        n_cols = 0
        n_cols_max = 0
        n_cols_min = 0
        row_col_list = []

        list_type = get_list_type(data)

        if list_type == "incorrect_variable_type" or list_type == "empty_list":
            pass

        elif list_type == "one_item_no_row": # Done  ["dato"]
            n_rows = 0
            n_cols_max = 1
            n_cols_min = 1

        elif list_type == "one_item_one_row": # Done [["dato"]]
            n_rows = 1
            n_cols_max = 1
            n_cols_min = 1

        elif list_type == "multiple_items_no_row": # Done ["Hello","bye","good"]
            n_rows = 0
            for num in range(len(data)):
                n_cols += 1
            n_cols_max = n_cols
            n_cols_min = n_cols

        elif list_type == "multiple_items_one_row": # Done [["Hello","bye","good"]]
            n_rows = 1
            for n in data[0]:
                n_cols += 1
            n_cols_max = n_cols
            n_cols_min = n_cols

        # Done [["Hello"],["bye"],["good"]] or [["Hello","mio"],["bye"],["good","hh"]]
        elif list_type == "multiple_items_multiple_rows":
            n_rows = len(data); n_cols = 0; lengths = []

            for r in data:
                lengths.append(len(r))

            n_cols_max = max(lengths)
            n_cols_min = min(lengths)

        else:       # "mix_items"
            n_rows = 0
            n_cols_max = len(data)
            n_cols_min = len(data)

        row_col_list.append(["All_rows",n_rows])
        row_col_list.append(["max_cols",n_cols_max])
        row_col_list.append(["min_cols",n_cols_min])

        return row_col_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Autofill Data. It Completes Data List to Make   it Rectangular List (Rows, Cols)                                                               -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def autofill_data(self, data:list, fill_value:str="----", update:bool=False)->list:
        '''
        autofill_data(list, str/int/float, boolean)

        This function will fill all the empty columns from the list.
        fill_value is the chr to be used to fill those columns. It can be str,
        int, float, or bool. By default it's a str type (----). '''

        list_type = get_list_type(data)
        if list_type == "multiple_items_multiple_rows":

            n_rows_n_cols_list = PyLO.dimensions(self, data)
            n_rows = n_rows_n_cols_list[0][1]
            n_cols = n_rows_n_cols_list[1][1]

            tempo = []; matrix_update = []

            for row in range(n_rows):
                for col in range(n_cols):
                    try:
                        tempo.append(data[row][col])
                    except:
                        tempo.append(fill_value)

                matrix_update.append(tempo)
                tempo = []

            if update == True:
                data.clear()
                [data.append(n) for n in matrix_update]
            return matrix_update

        else:
            return data


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Transpose List (Converting The Rows Into Cols AND Cols Into Rows)                                                                              -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def transpose(self, data:list, autofill=True, fill_value="----", update:bool=False)->list:
        '''
        transpose(data:list, autofill:bool, fill_value:int|float|str, update:bool)

        update is used to replace original list with the transpose list.
        update is set to False to keep the original list and save
        the new list into another variable.

        When the list is not square or rectangular, the list will be filled using
        the fill_value. If the autofill is set to False, some data will be lost. '''

        transpose_list = []
        list_type = get_list_type(data)


        if list_type == "incorrect_variable_type":  # [Not a List]  Done...! Case 0
            pass #return "incorrect variable type"

        elif list_type == "empty_list":             # []  Done...! Case 1
            pass #return "empty list"

        elif list_type == "multiple_items_one_row": # input: [[10,20,30]] output: [10,20,30] Done...! Case 5
            for row in data:
                for col in row:
                    transpose_list.append(col)
            #return transpose_list

        elif list_type == "one_item_one_row":       # input: [[10]] output: [10] Done...! Case 4
            transpose_list.append(data[0][0])
            #return transpose_list

        elif list_type == "one_item_no_row":        # input :[10]  output: [[10]] Done...! Case 2
            transpose_list = [[data[0]]]
            #return transpose_list

        elif list_type == "multiple_items_no_row":  # input: [10,20,30] output: [[10],[20],[30]] Done...! Case 3
            for col in range(len(data)):
                transpose_list.append([data[col]])
            #return transpose_list

        elif list_type == "mix_items":
            for n in data:
                transpose_list.append([n])
                #return transpose_list                # input: [5,[50],45] or [5,[50,40],45] or [[5],6,40,[45]] Case 9

        else:   # input: [[1],[2],[3]] output: [[1,2,3]] Done...! Case 6
                # input: [[1,2,3],[4,5,6],[7,8,9]] output: [[1,4,7],[2,5,8],[3,6,9]] Done...!  Case 7
                # input: [[1,2,3],[4,5,6,6],[7,8,9,9]] output: [[1,4,7],[2,5,8],[3,6,9]] Done...! Case 8
                # input: [[1,2,3],[4,5],[7,8,9]] output: Error_data_dimension Done...! Case 9
                # note: the element 0 needs to be greater than the rest.

            #--------------------------------------------------------------
            if autofill == True:
                fill_list = PyLO.autofill_data(self, data=data, fill_value=fill_value)
            else:
                fill_list = data
            #--------------------------------------------------------------

            lengths = []
            for l in fill_list:           # finding the smallest
                lengths.append(len(l))

            smaller = min(lengths)

            for item in fill_list:
                if len(item) != smaller:
                    break

            for i in range(smaller):
                row =[]
                for item in fill_list:
                    # appending to new list with values and index positions
                    # i contains index position and item contains values
                    row.append(item[i])
                transpose_list.append(row)

        if update == False:
            pass
        else:
            data.clear()
            for n in transpose_list:
                data.append(n)

        return transpose_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Convert a List From Any Type to String                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def data_to_str(self, data:list, update=False)->list:

        '''  Converts all the elements of a list to string type  '''

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.data_to_str(self, value))
            else:
                new_list.append(str(value))


        if update == True:
            data.clear()
            for n in new_list: data.append(n)

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Convert a List From String to Number                                                                                                           -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def data_to_num(self, data:list, fill_value=0, update=False)->list:

        '''  Converts all items from a list to numbers where it is possible.
             If it is not possible then it will take the fill_value provided to switch
             the value was not possible to convert. If the fill value provided is not
             a number or it is not possible to convert it to a number then it will be
             sustitute for zero, 0.  '''

        def convert_to_number(value, alternative):
            new_value = 0
            if   isinstance(value, int):     new_value = value
            elif isinstance(value, float):   new_value = value
            elif isinstance(value, complex): new_value = value
            else:
                try:
                    new_value = int(value)                # the number is integer or a string integer
                except:
                    try:
                        new_value = float(value)          # the number is float or a string float
                    except:
                        try:
                            new_value = complex(value)    # the number is complex or a string complex
                        except:
                            new_value = alternative
            return new_value


        new_refill = convert_to_number(fill_value, 0)

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.data_to_num(self, value, new_refill))
            else:
                new_list.append(convert_to_number(value, new_refill))


        if update == True:
            data.clear()
            for n in new_list: data.append(n)

        return new_list



    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Write a CSV File                                                                                                                               -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def write_csv_file(self, data:list, file_path:str="CSV_List")->str:

        '''  It writes a list into a CSV file
             E.g: file_path -> /home/User_Name/Documents/My_First_Table.csv  '''

        current_path = os.getcwd()
        ext = ""
        for l in file_path[-4:]:
            ext += l

        if ext == ".csv": new_file_name = file_path
        else:             new_file_name = file_path + ".csv"

        list_type = get_list_type(data)

        #with open(file_path + ".csv", "w", newline="") as file:
        with open(new_file_name, "w", newline="") as file:
            writer = csv.writer(file)
            if (list_type == "one_item_one_row" or list_type == "multiple_items_one_row" or\
                list_type == "multiple_items_multiple_rows"):
                for row in range(len(data)):
                    writer.writerow([col for col in data[row]])
            else:
                writer.writerow([col for col in data])

        if "/" in new_file_name: file = new_file_name
        else:                  file = current_path+"/"+new_file_name

        return file



    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Read a CSV File                                                                                                                                -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def read_csv_file(self, file_path:str="CSV_List")->list:

        '''  It reads a CSV file and returns a list of the contains of the file
             E.g: file_path -> /home/User_Name/Documents/My_First_Table.csv '''

        rows = []; ext = ""
        for l in file_path[-4:]:
            ext += l

        if ext == ".csv": new_file_name = file_path
        else:             new_file_name = file_path + ".csv"

        #with open(file_path + ".csv", "r", newline="") as file:
        try:
            with open(new_file_name, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    rows.append(row)
        except:
            rows = ["No Data or Not File"]

        list_type = get_list_type(rows)
        csv_list = []
        if (list_type == "one_item_one_row" or list_type == "multiple_items_one_row"):
            for n in rows:
                for m in n:
                    csv_list.append(m)
        else:
            csv_list = rows
        return csv_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Write a List into JSON File                                                                                                                    -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def write_json_file(self, data:list, file_path:str="JSON_List")->str:

        '''  It writes a list into a json file
             E.g: file_path -> /home/User_Name/Documents/My_First_Table.json  '''

        current_path = os.getcwd()
        ext = ""
        for l in file_path[-5:]:
            ext += l

        if ext == ".json": new_file_name = file_path
        else:              new_file_name = file_path + ".json"

        with open(new_file_name, "w") as data_file:
            json.dump(data, data_file, indent=4)

        if "/" in new_file_name: file = new_file_name
        else:                  file = current_path+"/"+new_file_name

        return file


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Read a JSON File and Return it as a List                                                                                                       -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def read_json_file(self, file_path:str="JSON_List")->list:

        '''  It reads a json file and returns a list with the contains of the file
             E.g: file_path -> /home/User_Name/Documents/My_First_Table.json  '''

        ext = ""
        for l in file_path[-5:]:
            ext += l

        if ext == ".json": new_file_name = file_path
        else:              new_file_name = file_path + ".json"

        try:
            with open(new_file_name, "r") as data_file:
                data = json.load(data_file)
        except:
            data = ["No Data or Not File"]

        return data


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Delete a Column in a List                                                                                                                      -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def delete_col(self, data:list, index:int=0, update:bool=False)->list:

        '''  It deletes a specific column from the list  '''

        n_rows_n_cols_list = PyLO.dimensions(self, data)
        n_cmax = n_rows_n_cols_list[1][1];      new_list = [];      tempo_rows = []
        list_type = get_list_type(data)

        if list_type == "incorrect_variable_type"   or list_type == "empty_list":  pass


        else:
            if   index > n_cmax-1: index = n_cmax -1
            elif index < 0:        index = 0
            else:                  pass

            #                 Done  ["dato"]                    Done [["dato"]]
            if list_type == "one_item_no_row" or list_type == "one_item_one_row":
                if update == True: data.pop(0)


            # multiple_items_no_row -> ["Hello","bye","good"]          mix_items -> [10,[50],[250],["H"],100]
            elif list_type == "multiple_items_no_row" or list_type == "mix_items":
                value =  data.pop(index)
                for n in data: new_list.append(n)
                if update == False: data.insert(index,value)


            elif list_type == "multiple_items_one_row":       # Done [["Hello","bye","good"]]
                if index >= len(data[0]):
                    print("col_ref is out of range in one or more columns in the list")
                else:
                    tempo = []
                    value = data[0].pop(index)
                    for n in data[0]: tempo.append(n)
                    new_list.append(tempo)
                    if update == False: data[0].insert(index,value)


            # Done [["Hello"],["bye"],["good"]] or [["Hello","mio"],["bye"],["good","hh"]]
            elif list_type == "multiple_items_multiple_rows":
                new_list = []
                for row in data:
                    tempo = []
                    for col in range(len(row)):
                        if index == col:  pass
                        else:             tempo.append(row[col])

                    # if tempo != []: new_list.append(tempo)
                    if len(tempo)>0 : new_list.append(tempo)

                if update == True:
                    data.clear()
                    for row in new_list:
                        for col in row:
                            tempo_rows.append(col)
                        data.append(tempo_rows)
                        tempo_rows = []
            else:
                pass
        return new_list


#-------------------------------------------------------------------------------------------------------------------------------------------------
    # Table List To Vector List                                                                                                                      -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def make_to_vector(self, data:list)->list:

        '''  This function makes any list in a form as a vector. [1,2,3,4,5,etc.],
             up to 4 brackets.
        '''

        vector_lista = []
        for item in data:
            if isinstance(item, list):
                for i in item:
                    if isinstance(i, list):
                        for n in i:
                            if isinstance(n, list):
                                for m in n:
                                    vector_lista.append(m)
                            else:
                                vector_lista.append(n)
                    else:
                        vector_lista.append(i)
            else:
                vector_lista.append(item)
        return vector_lista


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Add a New Column in a List                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def add_col(self, data:list, col_data:list, posi:int=0)->list:

        '''  This method adds a column into the list in a specific postion.
             The original list has to be in the form of a matrix or table
             and the column to be added needs to be as a vector list.

             Ex.
                data = [["H1","H2"],["R1C1","R1C2"], ["R2C1","R2C2"]]
                new_col_data = ["New_Header",   "New_Row_Col",  "New_Row_Col"]
                result = add_col(data, new_col_data, 1)
            Notice that if you want to add more than one column at same time, use the merge method.
        '''
        tmp = []; new_list = []

        if col_data == [] or col_data == [[]] or col_data == [[[]]]:  pass
        else:
            if isinstance(data, list) and isinstance(col_data, list):
                list_type = get_list_type(data)
                if list_type == "multiple_items_one_row" or list_type == "multiple_items_multiple_rows"\
                                                         or list_type == "one_item_one_row":
                    for row in data:
                        for col in row:
                            tmp.append(col)
                        new_list.append(tmp)
                        tmp = []

                    col_info = PyLO.make_to_vector(self, col_data)

                    diff = len(col_info) - len(data)
                    if diff < 0:
                        miss_col = diff * -1
                        for n in range(miss_col):
                            col_info.append("----")
                    else: pass

                    cnt = 0
                    ctrl = 0
                    dimension_ld = PyLO.dimensions(self, data=data)
                    max_col = dimension_ld[1][1]

                    if posi <= 0:
                        for row in data:
                            new_list[ctrl].insert(0, col_info[ctrl])
                            ctrl += 1

                    elif posi >= max_col:
                        for row in data:
                            new_list[ctrl].append(col_info[ctrl])
                            ctrl += 1

                    else:
                        for row in data:
                            if posi >= len(row):
                                new_list[ctrl].append(col_info[ctrl])
                                cnt += 1

                            else:
                                for n in range(len(row)):
                                    if posi == n:
                                        new_list[ctrl].insert(n, col_info[cnt])
                                        cnt += 1
                                    else: pass
                            ctrl += 1
                else:
                    new_list = PyLO.join_as_vector(self, col_data, data, 0)
            else:
                new_list =[]

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Replace a Value in the List                                                                                                                    -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def replace_value(self, data:list, old:int|str, new:int|str, case_sensitive:bool=True, update:bool=False)->list:

        '''  It replaces an item value for another in a list
             The list can be a vector [1,2,3,4] or a matrix (table) [[1,2],[3,1]]
             or a combination of them [[1,2],[3,3,3],3,[5,6,7,8]]
        '''

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.replace_value(self, value, old, new, case_sensitive))

            else:
                if case_sensitive == True:
                    if value == old:    new_list.append(new)
                    else:               new_list.append(value)

                elif case_sensitive == False:
                    if isinstance(value, str) and isinstance(old, str):
                        if value.lower() == old.lower():
                            new_list.append(new)
                        else:
                            new_list.append(value)
                    else:
                        if value == old:
                            new_list.append(new)
                        else:
                            new_list.append(value)

                else: pass

        if update == True:
            data.clear()
            for n in new_list: data.append(n)

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Number a List                                                                                                                                  -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def number(self, data:list, start_number:int=0, id_txt:str="Id", renumber:bool=False, update:bool=False)->list:

        '''  This method set the number of rows by adding a column to the left side.  '''

        if renumber == True:
            original = PyLO.delete_col(self, data, 0, False)
        else:
            original = data

        list_type = get_list_type(original)
        if list_type == "multiple_items_multiple_rows":

            result = [];                    tempo = []
            header = original.pop(0);       header.insert(0,id_txt)

            for row in original:
                tempo = row
                tempo.insert(0,start_number)
                start_number += 1
                result.append(tempo)
                tempo = []
            result.insert(0,header)

        if update == True:
            tempo_rows = []
            data.clear()
            for row in result:
                for col in row:
                    tempo_rows.append(col)
                data.append(tempo_rows)
                tempo_rows = []
        else:
            tempo_rows = []
            data.clear()
            for row in result:
                for col in row[1:]:
                    tempo_rows.append(col)
                data.append(tempo_rows)
                tempo_rows = []
        return result


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Join Two List as a Vector                                                                                                                      -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def join_as_vector(self, data:list, list_to_join:list, col_posi:int=0)->list:

        '''  It joins two list as a vector, join_list = [1,2,3,4,5,etc.]  '''

        lista_1 = PyLO.make_to_vector(self, data=data)
        lista_2 = PyLO.make_to_vector(self, data=list_to_join)
        join_list = []

        if   col_posi >= len(lista_1):
            for n in lista_1: join_list.append(n)
            for n in lista_2: join_list.append(n)

        elif col_posi <= 0:
            for n in lista_2: join_list.append(n)
            for n in lista_1: join_list.append(n)
        else:
            ctrl = 0
            for l1 in lista_1:
                if ctrl == col_posi:
                    for l2 in lista_2:
                        join_list.append(l2)
                    join_list.append(l1)

                else:
                    join_list.append(l1)
                ctrl += 1

        return join_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Grep or Find a Value in a List.                                                                                                                -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def find_value(self, data:list, value:int|str, case_sensitive=False)->list:

        '''  This method finds a value into a list and returns the location of the value.
             Up to 4 brackets.
        '''

        my_type = get_list_type(data)
        new_data = []

        if case_sensitive == False:
            if isinstance(value, str): new_value = value.lower()
            else:                    new_value = value

            new_data = PyLO.lower_case(self, data)
        else:
            new_value = value
            new_data = data

        grep_list = []
        ctrl = 0

        if my_type == "multiple_items_multiple_rows":
            for row in range(len(data)):
                for col in range(len(data[row])):

                    if new_data[row][col] == new_value:
                        grep_list.append([row, col, data[row][col]])
            ctrl = 1
        else:
            tmp = PyLO.make_to_vector(self, data=new_data)
            for v in range(len(tmp)):
                if tmp[v] == new_value:
                    grep_list.append(v)

        if   ctrl == 1 and len(grep_list)>0: grep_list.insert(0, ["Row","Col","value"])
        elif ctrl == 2 and len(grep_list)>0:
            grep_list.insert(0, "Position(s)")
            PyLO.transpose(self, data=grep_list, update=True)

        else: pass

        return grep_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Lower Case                                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def lower_case(self, data:list)->list:

        '''  This method lower case all the items in a list.  '''

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.lower_case(self, value))
            else:
                if isinstance(value, str):
                    new_list.append(value.lower())
                else:
                    new_list.append(value)

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Upper Case                                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def upper_case(self, data:list)->list:

        '''  This method upper case all the items in a list.  '''

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.upper_case(self, value))
            else:
                if isinstance(value, str):
                    new_list.append(value.upper())
                else:
                    new_list.append(value)

        return new_list



    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Capitalize Case                                                                                                                                -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def capitalize_case(self, data:list)->list:

        '''  This method capitalize all the items in a list.  '''

        new_list = []
        for value in data:
            if isinstance(value, list):
                new_list.append(PyLO.capitalize_case(self, value))
            else:
                if isinstance(value, str):
                    new_list.append(value.capitalize())
                else:
                    new_list.append(value)

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Merge 2 List                                                                                                                                   -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def merge(self, list_1:list, list_2:list, posi=0, merge_by=Appending.ROWS):

        '''  This method merge two list with two option of merge.
             It can be merge by ROWS or by COLUMNS. It also,
             provide the option to pick the specific position
             where to start the merge on list_1.
        '''

        merge_list = []

        my_type_1 = get_list_type(list_1)
        my_type_2 = get_list_type(list_2)

        # Case 1 and Case 2 for list_1
        if my_type_1 == "incorrect_variable_type" or my_type_1 == "empty_list":
            if my_type_2 == "incorrect_variable_type" or my_type_2 == "empty_list":
                pass
            else:
                merge_list = list_2

        # Case 1 and Case 2 for list_2
        elif my_type_2 == "incorrect_variable_type" or my_type_2 == "empty_list":
            if  my_type_1 == "incorrect_variable_type" or my_type_1 == "empty_list":
                pass
            else:
                merge_list = list_1

        # Case 6 with Case 6
        elif my_type_1 == "multiple_items_multiple_rows" and my_type_2 == "multiple_items_multiple_rows":
            if merge_by == "rows":
                if posi <= 0:
                    for n in list_2: merge_list.append(n)
                    for n in list_1: merge_list.append(n)

                elif posi >= len(list_1[0]):
                    for n in list_1: merge_list.append(n)
                    for n in list_2: merge_list.append(n)

                else:
                    for row in range(len(list_1)):
                        if posi == row:
                            for n in list_2: merge_list.append(n)
                            merge_list.append(list_1[row])
                        else:
                            merge_list.append(list_1[row])

            elif merge_by == "columns":
                new_list_2 = PyLO.autofill_data(self, data=list_2)#, fill_value="!-py-12-@$^*-cp-?!")
                merge_list = PyLO.autofill_data(self, data=list_1)#, fill_value="!-py-12-@$^*-cp-?!")

                columnas = []
                for n in range(len(new_list_2[0])):  columnas.append([])

                for row in new_list_2:
                    for col in range(len(row)):
                        columnas[col].append(row[col])

                for row in range(len(columnas)):
                    merge_list = PyLO.add_col(self, data=merge_list, col_data=columnas[row], posi=posi)

                # for row in merge:
                #     tmp = []
                #     for col in row:
                #         if col == "!-py-12-@$^*-cp-?!": pass
                #         else: tmp.append(col)
                #     merge_list.append(tmp)

            else: pass


        # Case 6 with any other Case
        elif my_type_1 == "multiple_items_multiple_rows" and my_type_2 != "multiple_items_multiple_rows":
            tmp_2 = PyLO.make_to_vector(self, list_2)

            if merge_by == "rows":
                if posi <= 0:
                    merge_list.append(tmp_2)
                    for n in list_1: merge_list.append(n)

                elif posi >= len(list_1):
                    for n in list_1: merge_list.append(n)
                    merge_list.append(tmp_2)

                else:
                    for n in range(len(list_1)):
                        if posi == n:
                            merge_list.append(tmp_2)
                            merge_list.append(list_1[n])
                        else:
                            merge_list.append(list_1[n])

            elif merge_by == "columns":
                merge_list = PyLO.add_col(self, data=list_1, col_data=list_2, posi=posi)


        # Any Case with Case 6
        elif my_type_1 != "multiple_items_multiple_rows" and my_type_2 == "multiple_items_multiple_rows":
            tmp_1 = PyLO.make_to_vector(self, list_1)

            if merge_by == "rows":
                if posi <= 0:
                    merge_list.append(tmp_1)
                    for n in list_2: merge_list.append(n)

                elif posi >= len(list_2):
                    for n in list_2: merge_list.append(n)
                    merge_list.append(tmp_1)

                else:
                    for n in range(len(list_2)):
                        if posi == n:
                            merge_list.append(tmp_1)
                            merge_list.append(list_2[n])
                        else:
                            merge_list.append(list_2[n])

            elif merge_by == "columns":
                merge_list = PyLO.add_col(self, data=list_2, col_data=list_1, posi=posi)

        else:
            # Case 3,    Case 4,    Case 5,    Case 7,    Case 8
            tmp_1 = PyLO.make_to_vector(self, list_1)
            tmp_2 = PyLO.make_to_vector(self, list_2)

            if merge_by.lower() == "rows":
                if posi <= 0:
                    for n in tmp_2: merge_list.append(n)
                    for n in tmp_1: merge_list.append(n)


                elif posi >= len(tmp_1):
                    for n in tmp_1: merge_list.append(n)
                    for n in tmp_2: merge_list.append(n)

                else:
                    for m in range(len(tmp_1)):
                        if posi == m:
                            for n in range(len(tmp_2)):
                                merge_list.append(tmp_2[n])
                            merge_list.append(tmp_1[m])
                        else:
                            merge_list.append(tmp_1[m])

            elif merge_by.lower() == "columns":

                tmp = []
                if posi <= 0:
                    for n in tmp_2: tmp.append(n)
                    for n in tmp_1: tmp.append(n)

                elif posi >= len(tmp_1):
                    for n in tmp_1: tmp.append(n)
                    for n in tmp_2: tmp.append(n)

                else:
                    for r in range(len(tmp_1)):
                        if r == posi:
                            for c in range(len(tmp_2)):
                                tmp.append(tmp_2[c])
                            tmp.append(tmp_1[r])
                        else:
                            tmp.append(tmp_1[r])
                merge_list.append(tmp)
            else: pass
        return merge_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Delete an Item from a List                                                                                                                     -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def delete_value(self, data:list, value:str="", case_sensitive:bool=True, update:bool=False)->list:

        ''' This method delete an value from the list.
            This methods has the option of using the case sensitive.
        '''

        new_list = []
        for my_value in data:
            if isinstance(my_value, list):
                new_list.append(PyLO.delete_value(self, my_value, value, case_sensitive, False))

            else:
                if case_sensitive == True:
                    if my_value == value:    pass
                    else:               new_list.append(my_value)

                elif case_sensitive == False:
                    if isinstance(my_value, str) and isinstance(value, str):
                        if my_value.lower() == value.lower():
                            pass
                        else:
                            new_list.append(my_value)
                    else:
                        if my_value == value:
                            pass
                        else:
                            new_list.append(my_value)

                else: pass
        if update == True:
            data.clear()
            for d in new_list:
                data.append(d)

        return new_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Reverse Order in a List ROWS. Keeps the Headers Untouch                                                                                        -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def reversed_row_order(self, data:list, update:bool=False):

        '''  This methods reverse the order of the list keeping
             the headers in the same positon.
        '''

        headers = [];       body = [];      ctrl = 0
        reversed_list = []; tmp = []

        my_type = get_list_type(data)
        if my_type == "multiple_items_multiple_rows":

            for row in data:
                if ctrl == 0:
                    headers.append(row)
                    ctrl = 1
                else:
                    for col in row:
                        tmp.append(col)
                    body.append(tmp)
                    tmp = []

            for row in reversed(body):
                reversed_list.append(row)
            reversed_list.insert(0,headers[0])

            if update == True:
                data.clear()
                for r in reversed_list:
                    data.append(r)
        else: pass
        return reversed_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Sort Rows of a List by Column Reference. Keep The Headers, Untouch                                                                             -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def sort_rows_by_col(self, data:list, ref_col:int=0, reversed_order:bool=False, update:bool=False)->list:

        '''  sort_by_col won't sort the first row because it is considered the Header of the list.
             If a column is mixed with string type and another type, like integer or float, it will
             cause an error. This method is intended to be used with all cells filled with the same
             type per column except the header; any empty cells will be filled automatically.
             If you want to fill those spots with a specific type, then use the autofill_data method.
        '''

        def _get_order_only_horizontal(in_list):
            tempo_list = []
            [tempo_list.append(n) for n in in_list]
            sorted_list = sorted(tempo_list)
            if reversed_order == True: list.reverse(sorted_list)
            return sorted_list
            #-----------------------------------------------------------------------------------------------------------------------------------------

        sorted_list = []
        list_type = get_list_type(data)
        if list_type == "incorrect_variable_type": pass
        elif list_type == "empty_list":            pass
        elif list_type == "one_item_no_row":       sorted_list = data  # Done  ["dato"]
        elif list_type == "one_item_one_row":      sorted_list = data  # Done [["dato"]]
        elif list_type == "multiple_items_no_row": # multiple_items_no_row -> ["Hello","bye","good"]
            sorted_list = _get_order_only_horizontal(data)

        elif list_type == "multiple_items_one_row":# Done [["Hello","bye","good"]]
            tmp = []
            [tmp.append(n) for n in data[0]]
            tmp = _get_order_only_horizontal(tmp)
            sorted_list.append(tmp)

            # Done [["Hello"],["bye"],["good"]] or [["Hello","mio"],["bye"],["good","hh"]]
        elif list_type == "multiple_items_multiple_rows":
            complete_list = PyLO.autofill_data(self, data=data)
            n_rows_n_cols_list = PyLO.dimensions(self, complete_list)
            n_cols = n_rows_n_cols_list[1][1]

            if ref_col >= n_cols:  print("\n ref_col out of range...! \n")
            else:
                sorted_list = [complete_list[0]] + sorted(complete_list[1:], key=lambda x: x[ref_col])
                # sorted_list = [new_list[0]] + sorted(new_list[1:], key=lambda x: x[str(ref_col)])
                if reversed_order == True:
                    header_row = sorted_list.pop(0)
                    list.reverse(sorted_list)
                    sorted_list.insert(0,header_row)

        else: print(msg="\n Not supported between instances of types \n")

        if update == True:
            data.clear()
            [data.append(n) for n in sorted_list]

        return sorted_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Sort Columns of a List. Keep The Headers, Untouch                                                                                              -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def sort_cols(self, data:list, sort_type:str|list=Order.ASCENDING, update:bool=False)->list:
        ''' If the option provided is different than ascending or descending or a list, it will sort as ascending.
            If the list contains numbers not in the range of the data list, it will sort as ascending.
            If the list contains a length different than the length of the data, it will sort as ascending.
            If the list is NOT in the form of rXc it will return an empty list as a result.  '''

        my_type_list = get_list_type(data)
        if my_type_list == "multiple_items_multiple_rows":

            num_order = [];     order_list = []
            new_data  = PyLO.autofill_data(self, data=data)
            headers   = new_data.pop(0)

            if sort_type   == PyLO.Order.ASCENDING:  headers_sort = sorted(headers, reverse=False)
            elif sort_type == PyLO.Order.DESCENDING: headers_sort = sorted(headers, reverse=True)
            else:
                if isinstance(sort_type, list):
                    if len(headers) != len(sort_type):
                        headers_sort = sorted(headers, reverse=False)
                    else:
                        # checking all items are int
                        all_number = True
                        for n in sort_type:
                            if not isinstance(n, int): all_number = False
                            else:                      pass

                        if all_number == False: headers_sort = sorted(headers, reverse=False)
                        else:
                            num_max = max(sort_type)
                            num_min = min(sort_type)
                            if num_max > (len(headers)-1) or num_min < 0:
                                headers_sort = sorted(headers, reverse=False)
                            else:
                                headers_sort = []
                                for n in sort_type:
                                    headers_sort.append(headers[n])

                else: headers_sort = sorted(headers, reverse=False)

            for n in headers_sort:
                index = headers.index(n)
                num_order.append(index)

            order_list.append(headers_sort)

            for n in range(len(new_data)):
                tmp = []
                for d in num_order:
                    tmp.append(new_data[n][d])
                order_list.append(tmp)
        elif my_type_list == "multiple_items_no_row":

            if sort_type == PyLO.Order.ASCENDING:    order_list = sorted(data, reverse=False)

            elif sort_type == PyLO.Order.DESCENDING: order_list = sorted(data, reverse=True )

            else: order_list = data

        elif my_type_list == "multiple_items_one_row":
            new_type_list = get_list_type(data[0])
            if new_type_list == "multiple_items_no_row":
                print("inside")
                if sort_type == PyLO.Order.ASCENDING:  order_list = sorted(data[0], reverse=False)
                elif sort_type == PyLO.Order.DESCENDING: order_list = sorted(data[0], reverse=True )
                else: order_list = data
            else:
                order_list = data
        else: order_list = data

        if update == True:
            data.clear()
            [data.append(n) for n in order_list]

        return order_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Update Case in a List.                                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def update_case(self, data:list, header_case:str=Case.CAPITALIZE, data_case:str=Case.LOWER, update:bool=False):

        '''  This method updates the case to the headers and the data. '''

        my_type_list = get_list_type(data)
        if my_type_list != "multiple_items_multiple_rows":
            if   data_case == PyLO.Case.UPPER:      case_list = PyLO.upper_case(self, data=data)
            elif data_case == PyLO.Case.LOWER:      case_list = PyLO.lower_case(self, data=data)
            elif data_case == PyLO.Case.CAPITALIZE: case_list = PyLO.capitalize_case(self, data=data)
            else:                           case_list = []
        else:
            new_data  = PyLO.autofill_data(self, data=data)
            headers = new_data.pop(0)

            if   header_case == PyLO.Case.UPPER:      new_headers = PyLO.upper_case(self, data=headers)
            elif header_case == PyLO.Case.LOWER:      new_headers = PyLO.lower_case(self, data=headers)
            elif header_case == PyLO.Case.CAPITALIZE: new_headers = PyLO.capitalize_case(self, data=headers)
            else:                             new_headers = headers


            if   data_case == PyLO.Case.UPPER:        new_data = PyLO.upper_case(self, data=new_data)
            elif data_case == PyLO.Case.LOWER:        new_data = PyLO.lower_case(self, data=new_data)
            elif data_case == PyLO.Case.CAPITALIZE:   new_data = PyLO.capitalize_case(self, data=new_data)
            else:                             pass

            case_list = []
            case_list.append(new_headers)

            for n in new_data:
                case_list.append(n)

        if update == True:
            data.clear()
            [data.append(n) for n in case_list]

        return case_list


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Update Case in a Specific Column in a List.                                                                                                    -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def update_case_col(self, data:list, header_case:str=Case.CAPITALIZE, data_case:str=Case.LOWER, col_ref=0, update:bool=False):

        '''  This method updates the case for a specific column, header and data.  '''

        my_type_list = get_list_type(data)
        if my_type_list != "multiple_items_multiple_rows":

            if   data_case.lower() == PyLO.Case.UPPER:      case_list = PyLO.upper_case(self, data=data)
            elif data_case.lower() == PyLO.Case.LOWER:      case_list = PyLO.lower_case(self, data=data)
            elif data_case.lower() == PyLO.Case.CAPITALIZE: case_list = PyLO.capitalize_case(self, data=data)
            else:                           case_list = []

        else:
            new_data  = PyLO.autofill_data(self, data=data)
            if col_ref > len(new_data[0]): new_col_ref = len(new_data[0])
            elif col_ref < 0:              new_col_ref = 0
            else:                          new_col_ref = col_ref


            new_headers = new_data.pop(0)

            if isinstance(new_headers[new_col_ref], str):

                if   header_case.lower() == PyLO.Case.UPPER:      new_headers[new_col_ref] = new_headers[new_col_ref].upper()
                elif header_case.lower() == PyLO.Case.LOWER:      new_headers[new_col_ref] = new_headers[new_col_ref].lower()
                elif header_case.lower() == PyLO.Case.CAPITALIZE: new_headers[new_col_ref] = new_headers[new_col_ref].capitalize()
                else:                             pass
            else: pass

            for row in range(len(new_data)):
                if isinstance(new_data[row][new_col_ref], str):
                    if   data_case.lower() == PyLO.Case.UPPER:      new_data[row][new_col_ref] = new_data[row][new_col_ref].upper()
                    elif data_case.lower() == PyLO.Case.LOWER:      new_data[row][new_col_ref] = new_data[row][new_col_ref].lower()
                    elif data_case.lower() == PyLO.Case.CAPITALIZE: new_data[row][new_col_ref] = new_data[row][new_col_ref].capitalize()
                    else: pass
                else:
                    pass

            case_list = []
            case_list.append(new_headers)

            for n in new_data:
                case_list.append(n)

        if update == True:
            data.clear()
            [data.append(n) for n in case_list]

        return case_list


    def find_duplicate(self, data:list, case_sensitive:bool=True):

        '''  This method find all duplicate values into a list and returns
             all duplicate values into a list.
        '''

        new_data = PyLO.make_to_vector(self, data=data)
        duplicate_list = []

        for i in range(len(new_data)):
            for j in range(i + 1, len(new_data)):
                tmp = []
                if case_sensitive == True:
                    if new_data[i] == new_data[j]:
                        tmp.append(new_data[i])
                        tmp.append(i)
                        tmp.append(new_data[j])
                        tmp.append(j)
                        duplicate_list.append(tmp)
                else:
                    if isinstance(new_data[i], str) and isinstance(new_data[j], str):
                        if new_data[i].lower() == new_data[j].lower():
                            tmp.append(new_data[i])
                            tmp.append(i)
                            tmp.append(new_data[j])
                            tmp.append(j)
                            duplicate_list.append(tmp)
                    else:
                        if new_data[i] == new_data[j]:
                            tmp.append(new_data[i])
                            tmp.append(i)
                            tmp.append(new_data[j])
                            tmp.append(j)
                            duplicate_list.append(tmp)

        if len(duplicate_list)>0:
            p = ["Data 1", "Posi 1", "Data 2", "Posi 2"]
            duplicate_list.insert(0,p)

        return duplicate_list




    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Mathematic Matrix Operation with List.                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------

    def matrix(self, matrix_a:list, operation, matrix_b:list)->list:
        '''
            matrix operation
        '''

        return operation(matrix_a, matrix_b)


    def multiply_by(self,matrix_a:list, component_b:int):
        '''
            matrix multiplication
        '''
        result = []
        if isinstance(component_b, (int,float,complex)):
            for row in range(len(matrix_a)):
                tempo = []
                for col in range(len(matrix_a[row])):
                    tempo.append(matrix_a[row][col]*component_b)
                result.append(tempo)
            return result


        return result

    def matrix_multiply_by_scalar(self, matrix:list, scalar:typing.Union[int,float,complex])->list:
        '''
            multiply a matrix with an scalar
        '''

        result = []
        if isinstance(scalar, (int,float,complex)):
            for row in range(len(matrix)):
                tempo = []
                for col in range(len(matrix[row])):
                    tempo.append(matrix[row][col]*scalar)
                result.append(tempo)
            return result


    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Mathematic Vector Operation with List.                                                                                                         -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    def vector_multiply_by_scalar(self, vector:list, scalar:typing.Union[int,float,complex])->list:
        '''
            vector multiply by a scalar
        '''
        if isinstance(scalar, (int,float,complex)):
            resutl = []
            for row in vector:
                resutl.append(row*scalar)
            return resutl

    def vector_dot_product(self, vector_a:list, vector_b:list)->typing.Union[int, float, complex]:
        '''
            dot product for two vectors
        '''
        result = 0
        for row in range(len(vector_a)):
            result = vector_a[row]*vector_b[row] + result
        return result
