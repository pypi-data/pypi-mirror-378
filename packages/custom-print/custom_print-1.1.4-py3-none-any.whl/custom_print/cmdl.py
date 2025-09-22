def main():
    
    '''  Description of custom_print project  '''
    import custom_print as cp

    lst = [["Module Name",         "custom_print"                                   ],
           ["Version",             "1.1.4"                                          ],
           ["Author",              "Miguel Angel Aguilar Cuesta"                    ],
           ["Author Email",        "acma.mex@gmail.com"                             ],
           ["Description",         "Customized Print"                               ],
           ["Requirement",         "Python 3.12 or greater"                         ],
           ["Long Description",    "README.md"                                      ],
           ["Content Type",        "MarkDown"                                       ],
           ["Find README.md at",   "https://github.com/acma82/Custom_Print"         ],
           ["Dependencies",        "None"                                           ],
           ["License",             "Everyone Can Use It At Their Own Risk"          ]]

    tbl = cp.FancyFormat()
    FACE = " (" + "0" + chr(0x25E1) + "0" + ") "
    tbl.title_msg = FACE + "  Project Description "
    tbl.title_align = "center"
    tbl.title_bg = 231
    tbl.title_fg = 234
    tbl.title_bold = True


    tbl.footnote_msg = "Released on Friday, December 27, 2024"
    tbl.adj_top_space = 1
    tbl.adj_bottom_space = 1


    tbl.header_bg = 54;             tbl.data_bg = 231
    tbl.header_fg = 231;            tbl.data_fg = 234
    tbl.header_bold = True;         tbl.bold_data = True
    tbl.adj_top_margin = 2;         tbl.adj_indent = 4

    tbl.print_fancy_format(lst, "design_10")
    print()

if __name__ == "__main__":
    main()