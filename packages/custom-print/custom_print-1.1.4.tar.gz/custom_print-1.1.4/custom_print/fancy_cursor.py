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
from custom_print.ref_names import Move

#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Cursor Class. Manipulate Cursor Around The Terminal                                                                                               --
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------------------
class Cursor:
    '''
    Cursor class helps to move the cursor around the terminal
    '''
    def jumpTo(self,qty=0, direction=Move.DOWN):

        '''  Moves the cursor n position to the Direction Specified  '''

        print(Cursor.moveTo(self, qty, direction),end="")


    def moveTo(self,qty=0, direction=Move.DOWN):

        '''  Moves the cursor n position to the Direction Specified  '''

        if direction.lower() == Move.UP or direction.lower() == "u":
            if qty == 0: movement = ""
            else:        movement = f"\033[{str(qty)}A"

        elif direction.lower() == Move.DOWN  or direction.lower() == "d":
            if qty == 0: movement = ""
            else:        movement = f"\033[{str(qty)}B"

        elif direction.lower() == Move.RIGHT or direction.lower() == "r":
            if qty == 0: movement = ""
            else:        movement = f"\033[{str(qty)}C"

        elif direction.lower() == Move.LEFT or direction.lower() == "l":
            if qty == 0: movement = ""
            else:        movement = f"\033[{str(qty)}D"

        else:  movement = ""
        return movement


    def jumpxy(self,x=0,y=0):

        '''  This function moves the cursor to specific position (x,y)  '''

        print(Cursor.movexy(self, y, x),end="")


    def movexy(self,x=0, y=0):

        '''  Moves the cursor to specific position (x, y)  '''

        if (y<=-1 or x<=-1):
            posi = ""
        else:
            posi = f"\033[{str(y)};{str(x)}H"

        return posi
