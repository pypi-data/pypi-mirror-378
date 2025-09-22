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
import enum
import platform        # fancy_functions
import csv             # PyLO class
import json            # PyLO class
import readline        # to use input and not cause problem with pylint
import os
#-----------------------------------------------------------------------------------------------------------------------------------------------------
# Layout is used for the Range, Set, Frozenset.                                                                                                      -
#-----------------------------------------------------------------------------------------------------------------------------------------------------
#class Move(str, enum.Enum): # python3.9.18
class Move(enum.StrEnum):    # python3.12.1
# class Move():
    '''
    Move reference class
    '''
    UP    = "up"
    RIGHT = "right"
    DOWN  = "down"
    LEFT  = "left"


class Align(enum.StrEnum):
# class Align():
    '''
    Align reference class
    '''
    LEFT     = "left"
    CENTER   = "center"
    RIGHT    = "right"
    JUSTIFY  = "justify"


class Layout(enum.StrEnum):
# class Layout():
    '''
    Layout reference class
    '''
    HORIZONTAL = "horizontal"
    VERTICAL =   "vertical"


class Length_bg(enum.Enum):
# class Length_bg():
    '''
    Length reference class
    '''
    ALL_ROW   = 1
    ONLY_WORD = 2

class Divider_Style(enum.Enum):
    '''
    Divider Styles
    '''
    CUSTOMIZED   = "customized"
    SINGLE_LINE  = "single_line"
    SINGLE_BOLD  = "single_bold"
    SINGLE_HEAVY = "single_heavy"
    DOUBLE_LINE  = "double_line"
    DASH_1       = "dash_1"
    DASH_2       = "dash_2"
    SQ_BRACKETS  = "sq_brackets"
    BLUE_WHITE_1 = "blue_white_1"
    BLUE_WHITE_2 = "blue_white_2"



class Line_Style(enum.StrEnum):
# class Line_Style():
    '''
    Line_Style reference class
    '''
    CUSTOMIZED   = "customized"
    DASH         = "dash"
    DOUBLE_LINE  = "double_line"
    SINGLE_LINE  = "single_line"
    SINGLE_BOLD  = "single_bold"
    SINGLE_HEAVY = "single_heavy"
    SQ_BRACKETS  = "sq_brackets"

    # This two option are for making their own custom color for the user
    SINGLE_SPACE  = "single_space"
    DOUBLE_SPACE  = "double_space"
    NONE          = "none"
    # Color Designs ( DEF -> Default )
    # set_color_for_spaces_on_tbl(self, bg_color_line, bg_color_header, fg_color_header, bg_color_data, fg_color_data)
    # Design 1
    WHITE_PURPLE        = "white_purple"
    WHITE_BLACK_PURPLE  = "white_black_purple"
    RED_WHITE           = "red_white"
    PURPLE_WHITE        = "purple_white"
    BLUE_WHITE          = "blue_white"
    TURQUOISE_WHITE     = "turquoise_white"


    TEAL_WHITE      = "teal_white"
    GRAY_TEAL_WHITE = "gray_teal_white"
    BLUE_PURPLE_WHITE_1 = "blue_purple_white_1"
    BLUE_PURPLE_WHITE_2 = "blue_purple_white_2"
    GREEN_GREEN_BLACK   = "green_green_black"

    # set_color_2_for_tbl(self,bg_h, fg_h, bg_l, bg_d, fg_d)
    # Design 2
    WHITE_BLACK_1   = "white_black"
    WHITE_BLACK_2   = "white_black_v2"
    TURQUOISE_BLACK = "turquoise_black"

    DESIGN_1  = "design_1"
    DESIGN_2  = "design_2"
    DESIGN_3  = "design_3"
    DESIGN_4  = "design_4"
    DESIGN_5  = "design_5"
    DESIGN_6  = "design_6"
    DESIGN_7  = "design_7"
    DESIGN_8  = "design_8"
    DESIGN_9  = "design_9"
    DESIGN_10 = "design_10"

#-----------------------------------------------------------------------------------------------------------------------------------------------------
class Unicode(enum.StrEnum):
# class Unicode():
    '''
    Unicode reference class
    '''
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Box Drawings                                                                                                                                   -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    BOX_DRAWINGS_LIGHT_HORIZONTAL          = "\N{BOX DRAWINGS LIGHT HORIZONTAL}"
    BOX_DRAWINGS_LIGHT_VERTICAL_AND_RIGHT  = "\N{BOX DRAWINGS LIGHT VERTICAL AND RIGHT}"
    BOX_DRAWINGS_LIGHT_VERTICAL_AND_LEFT   = "\N{BOX DRAWINGS LIGHT VERTICAL AND LEFT}"

    BOX_DRAWINGS_LIGHT_VERTICAL            = "\N{BOX DRAWINGS LIGHT VERTICAL}"
    BOX_DRAWINGS_LIGHT_DOWN_AND_HORIZONTAL = "\N{BOX DRAWINGS LIGHT DOWN AND HORIZONTAL}"
    BOX_DRAWINGS_LIGHT_UP_AND_HORIZONTAL   = "\N{BOX DRAWINGS LIGHT UP AND HORIZONTAL}"

    BOX_DRAWINGS_LIGHT_VERTICAL_AND_HORIZONTAL ="\N{BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL}"

    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Triangle                                                                                                                                       -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    BLACK_UP_POINTING_TRIANGLE   = "\N{BLACK UP-POINTING TRIANGLE}"      # \u25B2  up fill arrow
    WHITE_UP_POINTING_TRIANGLE   = "\N{WHITE UP-POINTING TRIANGLE}"      # \u25B3  up empty arrow

    BLAKC_RIGHT_POINTING_TRIANGLE = "\N{BLACK RIGHT-POINTING TRIANGLE}"  # \u25B6  right fill  arrow
    WHITE_RIGHT_POINTING_TRIANGLE = "\N{WHITE RIGHT-POINTING TRIANGLE}"  # \u25B7  right empty arrow

    BLACK_DOWN_POINTING_TRIANGLE = "\N{BLACK DOWN-POINTING TRIANGLE}"    # \u25BC  down fill  arrow
    WHITE_DOWN_POINTING_TRIANGLE = "\N{BLACK DOWN-POINTING TRIANGLE}"    # \u25BD  down empty arrow

    BLACK_LEFT_POINTING_TRIANGLE = "\N{BLACK LEFT-POINTING TRIANGLE}"    # \u25C0  left fill arrow
    WHITE_LEFT_POINTING_TRIANGLE = "\N{WHITE LEFT-POINTING TRIANGLE}"    # \u25C1  left empty arrow

    EM_DASH = "\N{EM DASH}"
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    # Miscellaneous                                                                                                                                  -
    #-------------------------------------------------------------------------------------------------------------------------------------------------
    BLACK_DIAMOND = "\N{BLACK DIAMOND}"
    WHITE_DIAMOND = "\N{WHITE DIAMOND}"

    BLACK_CIRCLE  = "\N{BLACK CIRCLE}"
    WHITE_CIRCLE  = "\N{WHITE CIRCLE}"

    FACE = "(" + chr(0x25D5) + chr(0x25E1) + chr(0x25D5) + ")"

COLOR_NAMES = [\
"LIGHT BLACK           ",    "RED                   ",    "LIGHT OFFICE GREEN ",
"LIGHT BROWN           ",    "EARLY NIGHT BLUE      ",    "MID PURPLE         ",
"CYAN                  ",    "LIGHT GRAY            ",    "DARK GRAY          ",
"PASTEL RED            ",    "ELECTRIC LIGHT GREEN  ",    "DARKISH YELLOW     ",
"LIGHT BLUE            ",    "LIGHT PURPLE          ",    "VERY LIGHT BLUE    ",
"WHITE                 ",    "BLACK                 ",    "DARK BLUE          ",
"NAVY BLUE             ",    "MIDNIGHT BLUE         ",    "MEDDIUM BLUE       ",
"BLUE                  ",    "SUMMER GREEN          ",    "VERY DARK CYAN     ",
"SEA BLUE              ",    "ENDEAVOUR BLUE        ",    "SCIENCE BLUE       ",
"BLUE RIBBON           ",    "AO GREEN              ",    "DEEP SEA GREEN     ",
"TEAL                  ",    "DEEP CERULEAN BLUE    ",    "STRONG BLUE        ",
"AZURE BLUE            ",    "DARK LIME GREEN       ",    "GO GREEN           ",
"DARK CYAN             ",    "BONDI BLUE            ",    "CERULEAN BLUE      ",
"BLUE BOLT             ",    "STRONG LIME GREEN     ",    "MALACHITE GREEN    ",
"CARIBBEAN GREEN       ",    "STRONG CYAN           ",    "DARK TURQUOISE     ",
"VIVID SKY BLUE        ",    "ELECTRIC GREEN        ",    "SPRING GREEN       ",
"GUPPIE GREEN          ",    "MEDIUM SPRING GREEN   ",    "BRIGHT TURQUOISE   ",
"AQUA                  ",    "BLOOD RED             ",    "VERY DARK MAGENTA  ",
"INDIGO                ",    "DARK VIOLET           ",    "LIGHT_VIOLET       ",
"ELECTRIC INDIGO       ",    "VERDUN GREEN          ",    "SCORPION GRAY      ",
"UCLA BLUE             ",    "SCAMPI BLUE           ",    "SLATE BLUE         ",
"CORNFLOWER BLUE       ",    "AVOCADO GREEN         ",    "GLADE GREEN        ",
"STEEL TEAL CYAN       ",    "STEEL BLUE            ",    "HAVELOCK BLUE      ",
"BLUEBERRY             ",    "KELLY GREEN           ",    "FOREST GREEN       ",
"POLISHED PIN GREEN    ",    "CRYSTAL BLUE          ",    "AQUA PEARL         ",
"BLUE JEANS            ",    "HARLEQUIN GREEN       ",    "MODERATE LIME GREEN",
"CARIBBEAN GREEN PEARL ",    "EUCALYPTUS GREEN      ",    "MEDDIUM TURQUOISE  ",
"MAYA BLUE             ",    "BRIGHT GREEN          ",    "LIGHT LIME GREEN   ",
"LIGHT MALACHITE GREEN ",    "MEDDIUM AQUAMARINE    ",    "AQUAMARINE GREEN   ",
"AQUAMARINE CYAN       ",    "DEEP RED              ",    "FRENCH PLUM VIOLET ",
"FRESH EGGPLANT VIOLET ",    "VIOLET                ",    "STRONG VIOLET      ",
"ELECTRIC VIOLET       ",    "BROWN                 ",    "COPPER BROWN       ",
"MOSTLY VIOLET         ",    "ROYAL PURPLE          ",    "MEDDIUM PURPLE     ",
"BLUEBERRY PURPLE      ",    "DARK OLIVE GREEN      ",    "CLAY CREEK GREEN   ",
"TAUPE GRAY            ",    "COOL GRAY             ",    "CHETWODE BLUE      ",
"VIOLET BLUE           ",    "APPLE GREEN           ",    "ASPARAGUS GREEN    ",
"LEAF GREEN            ",    "GRAYISH CYAN          ",    "COBALT BLUE        ",
"SKY BLUE              ",    "PISTACHIO GREEN       ",    "MANTIS GREEN       ",
"PASTEL GREEN          ",    "PEARL AQUA            ",    "SLIGHTLY CYAN      ",
"PALE CYAN             ",    "GREEN                 ",    "LIGHT GREEN        ",
"VERY LIGHT LIME GREEN ",    "MINT GREEN            ",    "AQUA LIME GREEN    ",
"LIGHT CYAN            ",    "DARK RED              ",    "DARK PINK          ",
"DARK MAGENTA          ",    "HELIOTROPE MAGENTA    ",    "VIVID PURPLE       ",
"ELECTRIC PURPLE       ",    "DARK ORANGE BROWN     ",    "ELECTRIC BROWN     ",
"DARK MODERATE PINK    ",    "DARK MODERATE MAGENTA ",    "RICH LILAC VIOLET  ",
"LAVENDER INDIGO       ",    "PIRATE GOLD BROWN     ",    "BRONZE BROWN       ",
"DARK GRAYISH RED      ",    "DARK GRAYISH MAGENTA  ",    "LAVENDER           ",
"BRIGHT LAVENDER       ",    "LIGHT GOLD BROWN      ",    "LIGHT OLIVE GREEN  ",
"DARK GRAYISH YELLOW   ",    "SILVER FOIL           ",    "GRAYISH BLUE       ",
"BLUE PURPLE           ",    "VIVID LIME GREEN      ",    "MODERATE GREEN     ",
"YELLOW GREEN          ",    "GRAYISH LIME GREEN    ",    "CRYSTAL CYAN       ",
"PALE BLUE             ",    "LIME                  ",    "GREEN YELLOW       ",
"VERY LIGHT GREEN      ",    "MENTHOL GREEN         ",    "AEREO BLUE         ",
"CELESTE CYAN          ",    "STRONG RED            ",    "ROYAL RED          ",
"MEXICAN PINK          ",    "HOLLYWOOD PINK        ",    "STRONG MAGENTA     ",
"PHLOX VIOLET          ",    "STRONG ORANGE         ",    "INDIAN RED         ",
"BLUSH RED             ",    "SUPER PINK            ",    "ORCHID MAGENTA     ",
"LIGHT MAGENTA         ",    "CHOCOLATE BROWN       ",    "COPPERFIELD BROWN  ",
"SLIGHTLY RED          ",    "SLIGHTLY PINK         ",    "LIGHT ORCHID PINK  ",
"BRIGHT LILAC VIOLET   ",    "MUSTARD YELLOW        ",    "EARTH YELLOW       ",
"TAN BROWN             ",    "GRAYISH RED           ",    "GRAYISH MAGENTA    ",
"PALE VIOLET           ",    "STRONG YELLOW         ",    "MODERATE YELLOW    ",
"DECO YELLOW           ",    "PASTEL GRAY           ",    "LIGHT SILVER       ",
"PALE LAVENDER         ",    "NEON YELLOW           ",    "LIGHT GREEN YELLOW ",
"MINDARO YELLOW        ",    "PALE GREEN            ",    "VERY PALE GREEN    ",
"VERY LIGHT CYAN       ",    "LIGHT RED             ",    "RASPBERRY RED      ",
"BRIGHT PINK           ",    "PINK                  ",    "MAGENTA            ",
"FUCHSIA               ",    "BLAZE ORANGE          ",    "BITTERSWEET RED    ",
"STRAWBERRY RED        ",    "HOT PINK              ",    "LIGHT PINK         ",
"PINK FLAMINGO         ",    "DARK ORANGE           ",    "SALMON ORANGE      ",
"TANGERINE RED         ",    "PINK SALMON           ",    "LAVENDER ROSE      ",
"FUCHSIA PINK          ",    "ORANGE                ",    "LIGHT ORANGE       ",
"VERY LIGHT ORANGE     ",    "PALE RED              ",    "PALE PINK          ",
"PALE MAGENTA          ",    "GOLD                  ",    "DANDELION YELLOW   ",
"JASMINE BROWN         ",    "PALE ORANGE           ",    "MISTY ROSE PINK    ",
"PINK LACE             ",    "YELLOW                ",    "LEMON YELLOW       ",
"PASTEL YELLOW         ",    "PALE YELLOW           ",    "VERY PALE YELLOW   ",
"LIGHT WHITE           ",    "VAMPIRE BLACK         ",    "GRAY BLACK         ",
"EERIE BLACK           ",    "RAISIN BLACK          ",    "DARK CHARCOAL      ",
"BLACK OLIVE           ",    "OUTER SPACE GRAY      ",    "DARK LIVER GRAY    ",
"DAVYS GRAY            ",    "GRANITE GRAY          ",    "DIM GRAY           ",
"SONIC SILVER          ",    "GRAY                  ",    "PHILIPPINE GRAY    ",
"DUSTY GRAY            ",    "SPANISH GRAY          ",    "LIGHTISH GRAY      ",
"PHILIPPINE SILVER     ",    "SILVER                ",    "SILVER SAND.       ",
"AMERICAN SILVER       ",    "ALTO GRAY             ",    "MERCURY GRAY       ",
"DARK WHITE            ",    "DEFAULT               ",    "DEFAULT            "]



class No(enum.IntEnum):
    ''' Color class will help to select a specific color by name rather than using the number.
    The number can be known by using the methods bg_ansi_color or fg_ansi_color.

    Notice that Color class works with all the classes, methods, and functions from
    custom_print rather than itself.

    import custom_print as cp

    CORRECT -> print(f"{cp.set_font(True, cp.Color.SUMMER_GREEN, cp.Color.BLACK)} Hello There...! {cp.reset_font()}")

    WRONG ->print(f"{cp.Color.SUMMER_GREEN} Hello There...! {cp.reset_font}")
    For the lates option use the Bg and Fg and Style classes.
        '''

    LIGHT_BLACK           = 0;          RED                   = 1;          LIGHT_OFFICE_GREEN  = 2
    LIGHT_BROWN           = 3;          EARLY_NIGHT_BLUE      = 4;          MED_PURPLE          = 5
    CYAN                  = 6;          LIGHT_GRAY            = 7;          DARK_GRAY           = 8
    PASTEL_RED            = 9;          ELECTRIC_LIGHT_GREEN  = 10;         DARKISH_YELLOW      = 11
    LIGHT_BLUE            = 12;         LIGHT_PURPLE          = 13;         VERY_LIGHT_BLUE     = 14
    WHITE                 = 15;         BLACK                 = 16;         DARK_BLUE           = 17
    NAVY_BLUE             = 18;         MIDNIGHT_BLUE         = 19;         MEDDIUM_BLUE        = 20
    BLUE                  = 21;         SUMMER_GREEN          = 22;         VERY_DARK_CYAN      = 23
    SEA_BLUE              = 24;         ENDEAVOUR_BLUE        = 25;         SCIENCE_BLUE        = 26
    BLUE_RIBBON           = 27;         AO_GREEN              = 28;         DEEP_SEA_GREEN      = 29
    TEAL                  = 30;         DEEP_CERULEAN_BLUE    = 31;         STRONG_BLUE         = 32
    AZURE_BLUE            = 33;         DARK_LIME_GREEN       = 34;         GO_GREEN            = 35
    DARK_CYAN             = 36;         BONDI_BLUE            = 37;         CERULEAN_BLUE       = 38
    BLUE_BOLT             = 39;         STRONG_LIME_GREEN     = 40;         MALACHITE_GREEN     = 41
    CARIBBEAN_GREEN       = 42;         STRONG_CYAN           = 43;         DARK_TURQUOISE      = 44
    VIVID_SKY_BLUE        = 45;         ELECTRIC_GREEN        = 46;         SPRING_GREEN        = 47
    GUPPIE_GREEN          = 48;         MEDIUM_SPRING_GREEN   = 49;         BRIGHT_TURQUOISE    = 50
    AQUA                  = 51;         BLOOD_RED             = 52;         VERY_DARK_MAGENTA   = 53
    INDIGO                = 54;         DARK_VIOLET           = 55;         LIGHT_VIOLET        = 56
    ELECTRIC_INDIGO       = 57;         VERDUN_GREEN          = 58;         SCORPION_GRAY       = 59
    UCLA_BLUE             = 60;         SCAMPI_BLUE           = 61;         SLATE_BLUE          = 62
    CORNFLOWER_BLUE       = 63;         AVOCADO_GREEN         = 64;         GLADE_GREEN         = 65
    STEEL_TEAL_CYAN       = 66;         STEEL_BLUE            = 67;         HAVELOCK_BLUE       = 68
    BLUEBERRY             = 69;         KELLY_GREEN           = 70;         FOREST_GREEN        = 71
    POLISHED_PIN_GREEN    = 72;         CRYSTAL_BLUE          = 73;         AQUA_PEARL          = 74
    BLUE_JEANS            = 75;         HARLEQUIN_GREEN       = 76;         MODERATE_LIME_GREEN = 77
    CARIBBEAN_GREEN_PEARL = 78;         EUCALYPTUS_GREEN      = 79;         MEDDIUM_TURQUOISE   = 80
    MAYA_BLUE             = 81;         BRIGHT_GREEN          = 82;         LIGHT_LIME_GREEN    = 83
    LIGHT_MALACHITE_GREEN = 84;         MEDDIUM_AQUAMARINE    = 85;         AQUAMARINE_GREEN    = 86
    AQUAMARINE_CYAN       = 87;         DEEP_RED              = 88;         FRENCH_PLUM_VIOLET  = 89
    FRESH_EGGPLANT_VIOLET = 90;         VIOLET                = 91;         STRONG_VIOLET       = 92
    ELECTRIC_VIOLET       = 93;         BROWN                 = 94;         COPPER_BROWN        = 95
    MOSTLY_VIOLET         = 96;         ROYAL_PURPLE          = 97;         MEDDIUM_PURPLE      = 98
    BLUEBERRY_PURPLE      = 99;         DARK_OLIVE_GREEN      = 100;        CLAY_CREEK_GREEN    = 101
    TAUPE_GRAY            = 102;        COOL_GRAY             = 103;        CHETWODE_BLUE       = 104
    VIOLET_BLUE           = 105;        APPLE_GREEN           = 106;        ASPARAGUS_GREEN     = 107
    LEAF_GREEN            = 108;        GRAYISH_CYAN          = 109;        COBALT_BLUE         = 110
    SKY_BLUE              = 111;        PISTACHIO_GREEN       = 112;        MANTIS_GREEN        = 113
    PASTEL_GREEN          = 114;        PEARL_AQUA            = 115;        SLIGHTLY_CYAN       = 116
    PALE_CYAN             = 117;        GREEN                 = 118;        LIGHT_GREEN         = 119
    VERY_LIGHT_LIME_GREEN = 120;        MINT_GREEN            = 121;        AQUA_LIME_CYAN      = 122
    LIGHT_CYAN            = 123;        DARK_RED              = 124;        DARK_PINK           = 125
    DARK_MAGENTA          = 126;        HELIOTROPE_MAGENTA    = 127;        VIVID_PURPLE        = 128
    ELECTRIC_PURPLE       = 129;        DARK_ORANGE_BROWN     = 130;        ELECTRIC_BROWN      = 131
    DARK_MODERATE_PINK    = 132;        DARK_MODERATE_MAGENTA = 133;        RICH_LILAC_VIOLET   = 134
    LAVENDER_INDIGO       = 135;        PIRATE_GOLD_BROWN     = 136;        BRONZE_BROWN        = 137
    DARK_GRAYISH_RED      = 138;        DARK_GRAYISH_MAGENTA  = 139;        LAVENDER            = 140
    BRIGHT_LAVENDER       = 141;        LIGHT_GOLD_BROWN      = 142;        LIGHT_OLIVE_GREEN   = 143
    DARK_GRAYISH_YELLOW   = 144;        SILVER_FOIL           = 145;        GRAYISH_BLUE        = 146
    BLUE_PURPLE           = 147;        VIVID_LIME_GREEN      = 148;        MODERATE_GREEN      = 149
    YELLOW_GREEN          = 150;        GRAYISH_LIME_GREEN    = 151;        CRYSTAL_CYAN        = 152
    PALE_BLUE             = 153;        LIME                  = 154;        GREEN_YELLOW        = 155
    VERY_LIGHT_GREEN      = 156;        MENTHOL_GREEN         = 157;        AEREO_BLUE          = 158
    CELESTE_CYAN          = 159;        STRONG_RED            = 160;        ROYAL_RED           = 161
    MEXICAN_PINK          = 162;        HOLLYWOOD_PINK        = 163;        STRONG_MAGENTA      = 164
    PHLOX_VIOLET          = 165;        STRONG_ORANGE         = 166;        INDIAN_RED          = 167
    BLUSH_RED             = 168;        SUPER_PINK            = 169;        ORCHID_MAGENTA      = 170
    LIGHT_MAGENTA         = 171;        CHOCOLATE_BROWN       = 172;        COPPERFIELD_BROWN   = 173
    SLIGHTLY_RED          = 174;        SLIGHTLY_PINK         = 175;        LIGHT_ORCHID_PINK   = 176
    BRIGHT_LILAC_VIOLET   = 177;        MUSTARD_YELLOW        = 178;        EARTH_YELLOW        = 179
    TAN_BROWN             = 180;        GRAYISH_RED           = 181;        GRAYISH_MAGENTA     = 182
    PALE_VIOLET           = 183;        STRONG_YELLOW         = 184;        MODERATE_YELLOW     = 185
    DECO_YELLOW           = 186;        PASTEL_GRAY           = 187;        LIGHT_SILVER        = 188
    PALE_LAVENDER         = 189;        NEON_YELLOW           = 190;        LIGHT_GREEN_YELLOW  = 191
    MINDARO_YELLOW        = 192;        PALE_GREEN            = 193;        VERY_PALE_GREEN     = 194
    VERY_LIGHT_CYAN       = 195;        LIGHT_RED             = 196;        RASPBERRY_RED       = 197
    BRIGHT_PINK           = 198;        PINK                  = 199;        MAGENTA             = 200
    FUCHSIA               = 201;        BLAZE_ORANGE          = 202;        BITTERSWEET_RED     = 203
    STRAWBERRY_RED        = 204;        HOT_PINK              = 205;        LIGHT_PINK          = 206
    PINK_FLAMINGO         = 207;        DARK_ORANGE           = 208;        SALMON_ORANGE       = 209
    TANGERINE_RED         = 210;        PINK_SALMON           = 211;        LAVENDER_ROSE       = 212
    FUCHSIA_PINK          = 213;        ORANGE                = 214;        LIGHT_ORANGE        = 215
    VERY_LIGHT_ORANGE     = 216;        PALE_RED              = 217;        PALE_PINK           = 218
    PALE_MAGENTA          = 219;        GOLD                  = 220;        DANDELION_YELLOW    = 221
    JASMINE_BROWN         = 222;        PALE_ORANGE           = 223;        MISTY_ROSE_PINK     = 224
    PINK_LACE             = 225;        YELLOW                = 226;        LEMON_YELLOW        = 227
    PASTEL_YELLOW         = 228;        PALE_YELLOW           = 229;        VERY_PALE_YELLOW    = 230
    LIGHT_WHITE           = 231;        VAMPIRE_BLACK         = 232;        GRAY_BLACK          = 233
    EERIE_BLACK           = 234;        RAISIN_BLACK          = 235;        DARK_CHARCOAL       = 236
    BLACK_OLIVE           = 237;        OUTER_SPACE_GRAY      = 238;        DARK_LIVER_GRAY     = 239
    DAVYS_GRAY            = 240;        GRANITE_GRAY          = 241;        DIM_GRAY            = 242
    SONIC_SILVER          = 243;        GRAY                  = 244;        PHILIPPINE_GRAY     = 245
    DUSTY_GRAY            = 246;        SPANISH_GRAY          = 247;        LIGHTISH_GRAY       = 248
    PHILIPPINE_SILVER     = 249;        SILVER                = 250;        SILVER_SAND         = 251
    AMERICAN_SILVER       = 252;        ALTO_GRAY             = 253;        MERCURY_GRAY        = 254
    DARK_WHITE            = 255;        DEFAULT               = 256;        default             = -1

class Bg(enum.StrEnum):

    '''  This Class uses the name of the color for background.
         import custom_print as cp
         print(f"{cp.Bg.INDIGO} Hello {cp.Bg.OFF} Normal")
    '''

    LIGHT_BLACK           = "\033[48;5;0m";          RED                    = "\033[48;5;1m";         LIGHT_OFFICE_GREEN   = "\033[48;5;2m"
    LIGHT_BROWN           = "\033[48;5;3m";          EARLY_NIGHT_BLUE       = "\033[48;5;4m";         MED_PURPLE           = "\033[48;5;5m"
    CYAN                  = "\033[48;5;6m";          LIGHT_GRAY             = "\033[48;5;7m";         DARK_GRAY            = "\033[48;5;8m"
    PASTEL_RED            = "\033[48;5;9m";          ELECTRIC_LIGHT_GREEN   = "\033[48;5;10m";        DARKISH_YELLOW       = "\033[48;5;11m"
    LIGHT_BLUE            = "\033[48;5;12m";         LIGHT_PURPLE           = "\033[48;5;13m";         VERY_LIGHT_BLUE     = "\033[48;5;14m"
    WHITE                 = "\033[48;5;15m";         BLACK                  = "\033[48;5;16m";         DARK_BLUE           = "\033[48;5;17m"
    NAVY_BLUE             = "\033[48;5;18m";         MIDNIGHT_BLUE          = "\033[48;5;19m";         MEDDIUM_BLUE        = "\033[48;5;20m"
    BLUE                  = "\033[48;5;21m";         SUMMER_GREEN           = "\033[48;5;22m";         VERY_DARK_CYAN      = "\033[48;5;23m"
    SEA_BLUE              = "\033[48;5;24m";         ENDEAVOUR_BLUE         = "\033[48;5;25m";         SCIENCE_BLUE        = "\033[48;5;26m"
    BLUE_RIBBON           = "\033[48;5;27m";         AO_GREEN               = "\033[48;5;28m";         DEEP_SEA_GREEN      = "\033[48;5;29m"
    TEAL                  = "\033[48;5;30m";         DEEP_CERULEAN_BLUE     = "\033[48;5;31m";         STRONG_BLUE         = "\033[48;5;32m"
    AZURE_BLUE            = "\033[48;5;33m";         DARK_LIME_GREEN        = "\033[48;5;34m";         GO_GREEN            = "\033[48;5;35m"
    DARK_CYAN             = "\033[48;5;36m";         BONDI_BLUE             = "\033[48;5;37m";         CERULEAN_BLUE       = "\033[48;5;38m"
    BLUE_BOLT             = "\033[48;5;39m";         STRONG_LIME_GREEN      = "\033[48;5;40m";         MALACHITE_GREEN     = "\033[48;5;41m"
    CARIBBEAN_GREEN       = "\033[48;5;42m";         STRONG_CYAN            = "\033[48;5;43m";         DARK_TURQUOISE      = "\033[48;5;44m"
    VIVID_SKY_BLUE        = "\033[48;5;45m";         ELECTRIC_GREEN         = "\033[48;5;46m";         SPRING_GREEN        = "\033[48;5;47m"
    GUPPIE_GREEN          = "\033[48;5;48m";         MEDIUM_SPRING_GREEN    = "\033[48;5;49m";         BRIGHT_TURQUOISE    = "\033[48;5;50m"
    AQUA                  = "\033[48;5;51m";         BLOOD_RED              = "\033[48;5;52m";         VERY_DARK_MAGENTA   = "\033[48;5;53m"
    INDIGO                = "\033[48;5;54m";         DARK_VIOLET            = "\033[48;5;55m";         LIGHT_VIOLET        = "\033[48;5;56m"
    ELECTRIC_INDIGO       = "\033[48;5;57m";         VERDUN_GREEN           = "\033[48;5;58m";         SCORPION_GRAY       = "\033[48;5;59m"
    UCLA_BLUE             = "\033[48;5;60m";         SCAMPI_BLUE            = "\033[48;5;61m";         SLATE_BLUE          = "\033[48;5;62m"
    CORNFLOWER_BLUE       = "\033[48;5;63m";         AVOCADO_GREEN          = "\033[48;5;64m";         GLADE_GREEN         = "\033[48;5;65m"
    STEEL_TEAL_CYAN       = "\033[48;5;66m";         STEEL_BLUE             = "\033[48;5;67m";         HAVELOCK_BLUE       = "\033[48;5;68m"
    BLUEBERRY             = "\033[48;5;69m";         KELLY_GREEN            = "\033[48;5;70m";         FOREST_GREEN        = "\033[48;5;71m"
    POLISHED_PIN_GREEN    = "\033[48;5;72m";         CRYSTAL_BLUE           = "\033[48;5;73m";         AQUA_PEARL          = "\033[48;5;74m"
    BLUE_JEANS            = "\033[48;5;75m";         HARLEQUIN_GREEN        = "\033[48;5;76m";         MODERATE_LIME_GREEN = "\033[48;5;77m"
    CARIBBEAN_GREEN_PEARL = "\033[48;5;78m";         EUCALYPTUS_GREEN       = "\033[48;5;79m";         MEDDIUM_TURQUOISE   = "\033[48;5;80m"
    MAYA_BLUE             = "\033[48;5;81m";         BRIGHT_GREEN           = "\033[48;5;82m";         LIGHT_LIME_GREEN    = "\033[48;5;83m"
    LIGHT_MALACHITE_GREEN = "\033[48;5;84m";         MEDDIUM_AQUAMARINE     = "\033[48;5;85m";         AQUAMARINE_GREEN    = "\033[48;5;86m"
    AQUAMARINE_CYAN       = "\033[48;5;87m";         DEEP_RED               = "\033[48;5;88m";         FRENCH_PLUM_VIOLET  = "\033[48;5;89m"
    FRESH_EGGPLANT_VIOLET = "\033[48;5;90m";         VIOLET                 = "\033[48;5;91m";         STRONG_VIOLET       = "\033[48;5;92m"
    ELECTRIC_VIOLET       = "\033[48;5;93m";         BROWN                  = "\033[48;5;94m";         COPPER_BROWN        = "\033[48;5;95m"
    MOSTLY_VIOLET         = "\033[48;5;96m";         ROYAL_PURPLE           = "\033[48;5;97m";         MEDDIUM_PURPLE      = "\033[48;5;98m"
    BLUEBERRY_PURPLE      = "\033[48;5;99m";         DARK_OLIVE_GREEN       = "\033[48;5;100m";        CLAY_CREEK_GREEN    = "\033[48;5;101m"
    TAUPE_GRAY            = "\033[48;5;102m";        COOL_GRAY              = "\033[48;5;103m";        CHETWODE_BLUE       = "\033[48;5;104m"
    VIOLET_BLUE           = "\033[48;5;105m";        APPLE_GREEN            = "\033[48;5;106m";        ASPARAGUS_GREEN     = "\033[48;5;107m"
    LEAF_GREEN            = "\033[48;5;108m";        GRAYISH_CYAN           = "\033[48;5;109m";        COBALT_BLUE         = "\033[48;5;110m"
    SKY_BLUE              = "\033[48;5;111m";        PISTACHIO_GREEN        = "\033[48;5;112m";        MANTIS_GREEN        = "\033[48;5;113m"
    PASTEL_GREEN          = "\033[48;5;114m";        PEARL_AQUA             = "\033[48;5;115m";        SLIGHTLY_CYAN       = "\033[48;5;116m"
    PALE_CYAN             = "\033[48;5;117m";        GREEN                  = "\033[48;5;118m";        LIGHT_GREEN         = "\033[48;5;119m"
    VERY_LIGHT_LIME_GREEN = "\033[48;5;120m";        MINT_GREEN             = "\033[48;5;121m";        AQUA_LIME_CYAN      = "\033[48;5;122m"
    LIGHT_CYAN            = "\033[48;5;123m";        DARK_RED               = "\033[48;5;124m";        DARK_PINK           = "\033[48;5;125m"
    DARK_MAGENTA          = "\033[48;5;126m";        HELIOTROPE_MAGENTA     = "\033[48;5;127m";        VIVID_PURPLE        = "\033[48;5;128m"
    ELECTRIC_PURPLE       = "\033[48;5;129m";        DARK_ORANGE_BROWN      = "\033[48;5;130m";        ELECTRIC_BROWN      = "\033[48;5;131m"
    DARK_MODERATE_PINK    = "\033[48;5;132m";        DARK_MODERATE_MAGENTA  = "\033[48;5;133m";        RICH_LILAC_VIOLET   = "\033[48;5;134m"
    LAVENDER_INDIGO       = "\033[48;5;135m";        PIRATE_GOLD_BROWN      = "\033[48;5;136m";        BRONZE_BROWN        = "\033[48;5;137m"
    DARK_GRAYISH_RED      = "\033[48;5;138m";        DARK_GRAYISH_MAGENTA   = "\033[48;5;139m";        LAVENDER            = "\033[48;5;140m"
    BRIGHT_LAVENDER       = "\033[48;5;141m";        LIGHT_GOLD_BROWN       = "\033[48;5;142m";        LIGHT_OLIVE_GREEN   = "\033[48;5;143m"
    DARK_GRAYISH_YELLOW   = "\033[48;5;144m";        SILVER_FOIL            = "\033[48;5;145m";        GRAYISH_BLUE        = "\033[48;5;146m"
    BLUE_PURPLE           = "\033[48;5;147m";        VIVID_LIME_GREEN       = "\033[48;5;148m";        MODERATE_GREEN      = "\033[48;5;149m"
    YELLOW_GREEN          = "\033[48;5;150m";        GRAYISH_LIME_GREEN     = "\033[48;5;151m";        CRYSTAL_CYAN        = "\033[48;5;152m"
    PALE_BLUE             = "\033[48;5;153m";        LIME                   = "\033[48;5;154m";        GREEN_YELLOW        = "\033[48;5;155m"
    VERY_LIGHT_GREEN      = "\033[48;5;156m";        MENTHOL_GREEN          = "\033[48;5;157m";        AEREO_BLUE          = "\033[48;5;158m"
    CELESTE_CYAN          = "\033[48;5;159m";        STRONG_RED             = "\033[48;5;160m";        ROYAL_RED           = "\033[48;5;161m"
    MEXICAN_PINK          = "\033[48;5;162m";        HOLLYWOOD_PINK         = "\033[48;5;163m";        STRONG_MAGENTA      = "\033[48;5;164m"
    PHLOX_VIOLET          = "\033[48;5;165m";        STRONG_ORANGE          = "\033[48;5;166m";        INDIAN_RED          = "\033[48;5;167m"
    BLUSH_RED             = "\033[48;5;168m";        SUPER_PINK             = "\033[48;5;169m";        ORCHID_MAGENTA      = "\033[48;5;170m"
    LIGHT_MAGENTA         = "\033[48;5;171m";        CHOCOLATE_BROWN        = "\033[48;5;172m";        COPPERFIELD_BROWN   = "\033[48;5;173m"
    SLIGHTLY_RED          = "\033[48;5;174m";        SLIGHTLY_PINK          = "\033[48;5;175m";        LIGHT_ORCHID_PINK   = "\033[48;5;176m"
    BRIGHT_LILAC_VIOLET   = "\033[48;5;177m";        MUSTARD_YELLOW         = "\033[48;5;178m";        EARTH_YELLOW        = "\033[48;5;179m"
    TAN_BROWN             = "\033[48;5;180m";        GRAYISH_RED            = "\033[48;5;181m";        GRAYISH_MAGENTA     = "\033[48;5;182m"
    PALE_VIOLET           = "\033[48;5;183m";        STRONG_YELLOW          = "\033[48;5;184m";        MODERATE_YELLOW     = "\033[48;5;185m"
    DECO_YELLOW           = "\033[48;5;186m";        PASTEL_GRAY            = "\033[48;5;187m";        LIGHT_SILVER        = "\033[48;5;188m"
    PALE_LAVENDER         = "\033[48;5;189m";        NEON_YELLOW            = "\033[48;5;190m";        LIGHT_GREEN_YELLOW  = "\033[48;5;191m"
    MINDARO_YELLOW        = "\033[48;5;192m";        PALE_GREEN             = "\033[48;5;193m";        VERY_PALE_GREEN     = "\033[48;5;194m"
    VERY_LIGHT_CYAN       = "\033[48;5;195m";        LIGHT_RED              = "\033[48;5;196m";        RASPBERRY_RED       = "\033[48;5;197m"
    BRIGHT_PINK           = "\033[48;5;198m";        PINK                   = "\033[48;5;199m";        MAGENTA             = "\033[48;5;200m"
    FUCHSIA               = "\033[48;5;201m";        BLAZE_ORANGE           = "\033[48;5;202m";        BITTERSWEET_RED     = "\033[48;5;203m"
    STRAWBERRY_RED        = "\033[48;5;204m";        HOT_PINK               = "\033[48;5;205m";        LIGHT_PINK          = "\033[48;5;206m"
    PINK_FLAMINGO         = "\033[48;5;207m";        DARK_ORANGE            = "\033[48;5;208m";        SALMON_ORANGE       = "\033[48;5;209m"
    TANGERINE_RED         = "\033[48;5;210m";        PINK_SALMON            = "\033[48;5;211m";        LAVENDER_ROSE       = "\033[48;5;212m"
    FUCHSIA_PINK          = "\033[48;5;213m";        ORANGE                 = "\033[48;5;214m";        LIGHT_ORANGE        = "\033[48;5;215m"
    VERY_LIGHT_ORANGE     = "\033[48;5;216m";        PALE_RED               = "\033[48;5;217m";        PALE_PINK           = "\033[48;5;218m"
    PALE_MAGENTA          = "\033[48;5;219m";        GOLD                   = "\033[48;5;220m";        DANDELION_YELLOW    = "\033[48;5;221m"
    JASMINE_BROWN         = "\033[48;5;222m";        PALE_ORANGE            = "\033[48;5;223m";        MISTY_ROSE_PINK     = "\033[48;5;224m"
    PINK_LACE             = "\033[48;5;225m";        YELLOW                 = "\033[48;5;226m";        LEMON_YELLOW        = "\033[48;5;227m"
    PASTEL_YELLOW         = "\033[48;5;228m";        PALE_YELLOW            = "\033[48;5;229m";        VERY_PALE_YELLOW    = "\033[48;5;230m"
    LIGHT_WHITE           = "\033[48;5;231m";        VAMPIRE_BLACK          = "\033[48;5;232m";        GRAY_BLACK          = "\033[48;5;233m"
    EERIE_BLACK           = "\033[48;5;234m";        RAISIN_BLACK           = "\033[48;5;235m";        DARK_CHARCOAL       = "\033[48;5;236m"
    BLACK_OLIVE           = "\033[48;5;237m";        OUTER_SPACE_GRAY       = "\033[48;5;238m";        DARK_LIVER_GRAY     = "\033[48;5;239m"
    DAVYS_GRAY            = "\033[48;5;240m";        GRANITE_GRAY           = "\033[48;5;241m";        DIM_GRAY            = "\033[48;5;242m"
    SONIC_SILVER          = "\033[48;5;243m";        GRAY                   = "\033[48;5;244m";        PHILIPPINE_GRAY     = "\033[48;5;245m"
    DUSTY_GRAY            = "\033[48;5;246m";        SPANISH_GRAY           = "\033[48;5;247m";        LIGHTISH_GRAY       = "\033[48;5;248m"
    PHILIPPINE_SILVER     = "\033[48;5;249m";        SILVER                 = "\033[48;5;250m";        SILVER_SAND         = "\033[48;5;251m"
    AMERICAN_SILVER       = "\033[48;5;252m";        ALTO_GRAY              = "\033[48;5;253m";        MERCURY_GRAY        = "\033[48;5;254m"
    DARK_WHITE            = "\033[48;5;255m";        DEFAULT                = "\033[49m";              OFF                 = "\033[49m"





class Fg(enum.StrEnum):

    '''  This Class uses the name of the color for the foreground.
         import custom_print as cp
         print(f"{cp.Fg.YELLOW} Hello {cp.Fg.OFF} Normal")
    '''

    LIGHT_BLACK           = "\033[38;5;0m";          RED                    = "\033[38;5;1m";         LIGHT_OFFICE_GREEN   = "\033[38;5;2m"
    LIGHT_BROWN           = "\033[38;5;3m";          EARLY_NIGHT_BLUE       = "\033[38;5;4m";         MED_PURPLE           = "\033[38;5;5m"
    CYAN                  = "\033[38;5;6m";          LIGHT_GRAY             = "\033[38;5;7m";         DARK_GRAY            = "\033[38;5;8m"
    PASTEL_RED            = "\033[38;5;9m";          ELECTRIC_LIGHT_GREEN   = "\033[38;5;10m";        DARKISH_YELLOW       = "\033[38;5;11m"
    LIGHT_BLUE            = "\033[38;5;12m";         LIGHT_PURPLE           = "\033[38;5;13m";         VERY_LIGHT_BLUE     = "\033[38;5;14m"
    WHITE                 = "\033[38;5;15m";         BLACK                  = "\033[38;5;16m";         DARK_BLUE           = "\033[38;5;17m"
    NAVY_BLUE             = "\033[38;5;18m";         MIDNIGHT_BLUE          = "\033[38;5;19m";         MEDDIUM_BLUE        = "\033[38;5;20m"
    BLUE                  = "\033[38;5;21m";         SUMMER_GREEN           = "\033[38;5;22m";         VERY_DARK_CYAN      = "\033[38;5;23m"
    SEA_BLUE              = "\033[38;5;24m";         ENDEAVOUR_BLUE         = "\033[38;5;25m";         SCIENCE_BLUE        = "\033[38;5;26m"
    BLUE_RIBBON           = "\033[38;5;27m";         AO_GREEN               = "\033[38;5;28m";         DEEP_SEA_GREEN      = "\033[38;5;29m"
    TEAL                  = "\033[38;5;30m";         DEEP_CERULEAN_BLUE     = "\033[38;5;31m";         STRONG_BLUE         = "\033[38;5;32m"
    AZURE_BLUE            = "\033[38;5;33m";         DARK_LIME_GREEN        = "\033[38;5;34m";         GO_GREEN            = "\033[38;5;35m"
    DARK_CYAN             = "\033[38;5;36m";         BONDI_BLUE             = "\033[38;5;37m";         CERULEAN_BLUE       = "\033[38;5;38m"
    BLUE_BOLT             = "\033[38;5;39m";         STRONG_LIME_GREEN      = "\033[38;5;40m";         MALACHITE_GREEN     = "\033[38;5;41m"
    CARIBBEAN_GREEN       = "\033[38;5;42m";         STRONG_CYAN            = "\033[38;5;43m";         DARK_TURQUOISE      = "\033[38;5;44m"
    VIVID_SKY_BLUE        = "\033[38;5;45m";         ELECTRIC_GREEN         = "\033[38;5;46m";         SPRING_GREEN        = "\033[38;5;47m"
    GUPPIE_GREEN          = "\033[38;5;48m";         MEDIUM_SPRING_GREEN    = "\033[38;5;49m";         BRIGHT_TURQUOISE    = "\033[38;5;50m"
    AQUA                  = "\033[38;5;51m";         BLOOD_RED              = "\033[38;5;52m";         VERY_DARK_MAGENTA   = "\033[38;5;53m"
    INDIGO                = "\033[38;5;54m";         DARK_VIOLET            = "\033[38;5;55m";         LIGHT_VIOLET        = "\033[38;5;56m"
    ELECTRIC_INDIGO       = "\033[38;5;57m";         VERDUN_GREEN           = "\033[38;5;58m";         SCORPION_GRAY       = "\033[38;5;59m"
    UCLA_BLUE             = "\033[38;5;60m";         SCAMPI_BLUE            = "\033[38;5;61m";         SLATE_BLUE          = "\033[38;5;62m"
    CORNFLOWER_BLUE       = "\033[38;5;63m";         AVOCADO_GREEN          = "\033[38;5;64m";         GLADE_GREEN         = "\033[38;5;65m"
    STEEL_TEAL_CYAN       = "\033[38;5;66m";         STEEL_BLUE             = "\033[38;5;67m";         HAVELOCK_BLUE       = "\033[38;5;68m"
    BLUEBERRY             = "\033[38;5;69m";         KELLY_GREEN            = "\033[38;5;70m";         FOREST_GREEN        = "\033[38;5;71m"
    POLISHED_PIN_GREEN    = "\033[38;5;72m";         CRYSTAL_BLUE           = "\033[38;5;73m";         AQUA_PEARL          = "\033[38;5;74m"
    BLUE_JEANS            = "\033[38;5;75m";         HARLEQUIN_GREEN        = "\033[38;5;76m";         MODERATE_LIME_GREEN = "\033[38;5;77m"
    CARIBBEAN_GREEN_PEARL = "\033[38;5;78m";         EUCALYPTUS_GREEN       = "\033[38;5;79m";         MEDDIUM_TURQUOISE   = "\033[38;5;80m"
    MAYA_BLUE             = "\033[38;5;81m";         BRIGHT_GREEN           = "\033[38;5;82m";         LIGHT_LIME_GREEN    = "\033[38;5;83m"
    LIGHT_MALACHITE_GREEN = "\033[38;5;84m";         MEDDIUM_AQUAMARINE     = "\033[38;5;85m";         AQUAMARINE_GREEN    = "\033[38;5;86m"
    AQUAMARINE_CYAN       = "\033[38;5;87m";         DEEP_RED               = "\033[38;5;88m";         FRENCH_PLUM_VIOLET  = "\033[38;5;89m"
    FRESH_EGGPLANT_VIOLET = "\033[38;5;90m";         VIOLET                 = "\033[38;5;91m";         STRONG_VIOLET       = "\033[38;5;92m"
    ELECTRIC_VIOLET       = "\033[38;5;93m";         BROWN                  = "\033[38;5;94m";         COPPER_BROWN        = "\033[38;5;95m"
    MOSTLY_VIOLET         = "\033[38;5;96m";         ROYAL_PURPLE           = "\033[38;5;97m";         MEDDIUM_PURPLE      = "\033[38;5;98m"
    BLUEBERRY_PURPLE      = "\033[38;5;99m";         DARK_OLIVE_GREEN       = "\033[38;5;100m";        CLAY_CREEK_GREEN    = "\033[38;5;101m"
    TAUPE_GRAY            = "\033[38;5;102m";        COOL_GRAY              = "\033[38;5;103m";        CHETWODE_BLUE       = "\033[38;5;104m"
    VIOLET_BLUE           = "\033[38;5;105m";        APPLE_GREEN            = "\033[38;5;106m";        ASPARAGUS_GREEN     = "\033[38;5;107m"
    LEAF_GREEN            = "\033[38;5;108m";        GRAYISH_CYAN           = "\033[38;5;109m";        COBALT_BLUE         = "\033[38;5;110m"
    SKY_BLUE              = "\033[38;5;111m";        PISTACHIO_GREEN        = "\033[38;5;112m";        MANTIS_GREEN        = "\033[38;5;113m"
    PASTEL_GREEN          = "\033[38;5;114m";        PEARL_AQUA             = "\033[38;5;115m";        SLIGHTLY_CYAN       = "\033[38;5;116m"
    PALE_CYAN             = "\033[38;5;117m";        GREEN                  = "\033[38;5;118m";        LIGHT_GREEN         = "\033[38;5;119m"
    VERY_LIGHT_LIME_GREEN = "\033[38;5;120m";        MINT_GREEN             = "\033[38;5;121m";        AQUA_LIME_CYAN      = "\033[38;5;122m"
    LIGHT_CYAN            = "\033[38;5;123m";        DARK_RED               = "\033[38;5;124m";        DARK_PINK           = "\033[38;5;125m"
    DARK_MAGENTA          = "\033[38;5;126m";        HELIOTROPE_MAGENTA     = "\033[38;5;127m";        VIVID_PURPLE        = "\033[38;5;128m"
    ELECTRIC_PURPLE       = "\033[38;5;129m";        DARK_ORANGE_BROWN      = "\033[38;5;130m";        ELECTRIC_BROWN      = "\033[38;5;131m"
    DARK_MODERATE_PINK    = "\033[38;5;132m";        DARK_MODERATE_MAGENTA  = "\033[38;5;133m";        RICH_LILAC_VIOLET   = "\033[38;5;134m"
    LAVENDER_INDIGO       = "\033[38;5;135m";        PIRATE_GOLD_BROWN      = "\033[38;5;136m";        BRONZE_BROWN        = "\033[38;5;137m"
    DARK_GRAYISH_RED      = "\033[38;5;138m";        DARK_GRAYISH_MAGENTA   = "\033[38;5;139m";        LAVENDER            = "\033[38;5;140m"
    BRIGHT_LAVENDER       = "\033[38;5;141m";        LIGHT_GOLD_BROWN       = "\033[38;5;142m";        LIGHT_OLIVE_GREEN   = "\033[38;5;143m"
    DARK_GRAYISH_YELLOW   = "\033[38;5;144m";        SILVER_FOIL            = "\033[38;5;145m";        GRAYISH_BLUE        = "\033[38;5;146m"
    BLUE_PURPLE           = "\033[38;5;147m";        VIVID_LIME_GREEN       = "\033[38;5;148m";        MODERATE_GREEN      = "\033[38;5;149m"
    YELLOW_GREEN          = "\033[38;5;150m";        GRAYISH_LIME_GREEN     = "\033[38;5;151m";        CRYSTAL_CYAN        = "\033[38;5;152m"
    PALE_BLUE             = "\033[38;5;153m";        LIME                   = "\033[38;5;154m";        GREEN_YELLOW        = "\033[38;5;155m"
    VERY_LIGHT_GREEN      = "\033[38;5;156m";        MENTHOL_GREEN          = "\033[38;5;157m";        AEREO_BLUE          = "\033[38;5;158m"
    CELESTE_CYAN          = "\033[38;5;159m";        STRONG_RED             = "\033[38;5;160m";        ROYAL_RED           = "\033[38;5;161m"
    MEXICAN_PINK          = "\033[38;5;162m";        HOLLYWOOD_PINK         = "\033[38;5;163m";        STRONG_MAGENTA      = "\033[38;5;164m"
    PHLOX_VIOLET          = "\033[38;5;165m";        STRONG_ORANGE          = "\033[38;5;166m";        INDIAN_RED          = "\033[38;5;167m"
    BLUSH_RED             = "\033[38;5;168m";        SUPER_PINK             = "\033[38;5;169m";        ORCHID_MAGENTA      = "\033[38;5;170m"
    LIGHT_MAGENTA         = "\033[38;5;171m";        CHOCOLATE_BROWN        = "\033[38;5;172m";        COPPERFIELD_BROWN   = "\033[38;5;173m"
    SLIGHTLY_RED          = "\033[38;5;174m";        SLIGHTLY_PINK          = "\033[38;5;175m";        LIGHT_ORCHID_PINK   = "\033[38;5;176m"
    BRIGHT_LILAC_VIOLET   = "\033[38;5;177m";        MUSTARD_YELLOW         = "\033[38;5;178m";        EARTH_YELLOW        = "\033[38;5;179m"
    TAN_BROWN             = "\033[38;5;180m";        GRAYISH_RED            = "\033[38;5;181m";        GRAYISH_MAGENTA     = "\033[38;5;182m"
    PALE_VIOLET           = "\033[38;5;183m";        STRONG_YELLOW          = "\033[38;5;184m";        MODERATE_YELLOW     = "\033[38;5;185m"
    DECO_YELLOW           = "\033[38;5;186m";        PASTEL_GRAY            = "\033[38;5;187m";        LIGHT_SILVER        = "\033[38;5;188m"
    PALE_LAVENDER         = "\033[38;5;189m";        NEON_YELLOW            = "\033[38;5;190m";        LIGHT_GREEN_YELLOW  = "\033[38;5;191m"
    MINDARO_YELLOW        = "\033[38;5;192m";        PALE_GREEN             = "\033[38;5;193m";        VERY_PALE_GREEN     = "\033[38;5;194m"
    VERY_LIGHT_CYAN       = "\033[38;5;195m";        LIGHT_RED              = "\033[38;5;196m";        RASPBERRY_RED       = "\033[38;5;197m"
    BRIGHT_PINK           = "\033[38;5;198m";        PINK                   = "\033[38;5;199m";        MAGENTA             = "\033[38;5;200m"
    FUCHSIA               = "\033[38;5;201m";        BLAZE_ORANGE           = "\033[38;5;202m";        BITTERSWEET_RED     = "\033[38;5;203m"
    STRAWBERRY_RED        = "\033[38;5;204m";        HOT_PINK               = "\033[38;5;205m";        LIGHT_PINK          = "\033[38;5;206m"
    PINK_FLAMINGO         = "\033[38;5;207m";        DARK_ORANGE            = "\033[38;5;208m";        SALMON_ORANGE       = "\033[38;5;209m"
    TANGERINE_RED         = "\033[38;5;210m";        PINK_SALMON            = "\033[38;5;211m";        LAVENDER_ROSE       = "\033[38;5;212m"
    FUCHSIA_PINK          = "\033[38;5;213m";        ORANGE                 = "\033[38;5;214m";        LIGHT_ORANGE        = "\033[38;5;215m"
    VERY_LIGHT_ORANGE     = "\033[38;5;216m";        PALE_RED               = "\033[38;5;217m";        PALE_PINK           = "\033[38;5;218m"
    PALE_MAGENTA          = "\033[38;5;219m";        GOLD                   = "\033[38;5;220m";        DANDELION_YELLOW    = "\033[38;5;221m"
    JASMINE_BROWN         = "\033[38;5;222m";        PALE_ORANGE            = "\033[38;5;223m";        MISTY_ROSE_PINK     = "\033[38;5;224m"
    PINK_LACE             = "\033[38;5;225m";        YELLOW                 = "\033[38;5;226m";        LEMON_YELLOW        = "\033[38;5;227m"
    PASTEL_YELLOW         = "\033[38;5;228m";        PALE_YELLOW            = "\033[38;5;229m";        VERY_PALE_YELLOW    = "\033[38;5;230m"
    LIGHT_WHITE           = "\033[38;5;231m";        VAMPIRE_BLACK          = "\033[38;5;232m";        GRAY_BLACK          = "\033[38;5;233m"
    EERIE_BLACK           = "\033[38;5;234m";        RAISIN_BLACK           = "\033[38;5;235m";        DARK_CHARCOAL       = "\033[38;5;236m"
    BLACK_OLIVE           = "\033[38;5;237m";        OUTER_SPACE_GRAY       = "\033[38;5;238m";        DARK_LIVER_GRAY     = "\033[38;5;239m"
    DAVYS_GRAY            = "\033[38;5;240m";        GRANITE_GRAY           = "\033[38;5;241m";        DIM_GRAY            = "\033[38;5;242m"
    SONIC_SILVER          = "\033[38;5;243m";        GRAY                   = "\033[38;5;244m";        PHILIPPINE_GRAY     = "\033[38;5;245m"
    DUSTY_GRAY            = "\033[38;5;246m";        SPANISH_GRAY           = "\033[38;5;247m";        LIGHTISH_GRAY       = "\033[38;5;248m"
    PHILIPPINE_SILVER     = "\033[38;5;249m";        SILVER                 = "\033[38;5;250m";        SILVER_SAND         = "\033[38;5;251m"
    AMERICAN_SILVER       = "\033[38;5;252m";        ALTO_GRAY              = "\033[38;5;253m";        MERCURY_GRAY        = "\033[38;5;254m"
    DARK_WHITE            = "\033[38;5;255m";        DEFAULT                = "\033[39m";              OFF                 = "\033[39m"



class Style(enum.StrEnum):

    '''  This class uses the style name rather than the bool value.
         import custom_print as cp
         print(f"{cp.Fg.YELLOW} Hello {cp.Fg.OFF} Normal")
    '''

    BOLD_ON      = "\033[1m";       BOLD_OFF      = "\033[22m"
    DIM_ON       = "\033[2m";       DIM_OFF       = "\033[22m"
    ITALIC_ON    = "\033[3m";       ITALIC_OFF    = "\033[23m"
    UNDERLINE_ON = "\033[4m";       UNDERLINE_OFF = "\033[24m"
    BLINKING_ON  = "\033[5m";       BLINKING_OFF  = "\033[25m"
    INVERSE_ON   = "\033[7m";       INVERSE_OFF   = "\033[27m"
    HIDDEN_ON    = "\033[8m";       HIDDEN_OFF    = "\033[28m"
    STRIKE_ON    = "\033[9m";       STRIKE_OFF    = "\033[29m"
    RESET_ALL    = "\033[0m"
    OFF = "\033[22m"+"\033[23m"+"\033[24m"+"\033[25m"+"\033[27m"+"\033[28m"+"\033[29m"
