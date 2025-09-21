from .Menu import simple_console_menu, simple_console_menu_block


def SimpleConsoleMenu(
    menuName: str,
    menuItems: list,
    inputQuestion: str = "What do you want to do:",
    menuSize: int = 76,
    autoAddQuit: bool = False,
    onlyReturnNumber: bool = True,
    allowedCharacters: str = "",
    acceptedQuitCharacters: str = "",
) -> int | str:
    """
    Makes a menu

    parameters:
        menuName               - Required  : name of the menu (Str)
        menuItems              - Required  : menu items ["item 1","item 2"] (List)
        inputQuestion          - Optional  : Question input (Str)
        menuSize               - Optional  : Size of the menu (Int)
        autoAddQuit            - Optional  : automatically add a quit option (Bool)
        onlyReturnNumber       - Optional  : only numbers are allowed to return (Bool)
        allowedCharacters      - Optional  : specifier which character(s) are allowed if onlyReturnNumber is False, separated with ';' (str)
        acceptedQuitCharacters - Optional  : specifier which character is allowed if onlyReturnNumber is False for quit (str)

    """
    return simple_console_menu(
        menuName,
        menuItems,
        input_question=inputQuestion,
        menu_size=menuSize,
        auto_add_quit=autoAddQuit,
        only_return_number=onlyReturnNumber,
        allowed_characters=allowedCharacters,
        accepted_quit_characters=acceptedQuitCharacters,
    )


def SimpleConsoleMenuBlock(
    menuName: str,
    menuItems: list,
    inputQuestion: str = "What do you want to do:",
    menuSize: int = 76,
    autoAddQuit: bool = False,
    onlyReturnNumber: bool = True,
    allowedCharacters: str = "",
    acceptedQuitCharacters: str = "",
) -> int | str:
    """
    Makes a menu with a box arround it

    parameters:
        menuName               - Required  : name of the menu (Str)
        menuItems              - Required  : menu items ["item 1","item 2"] (List)
        inputQuestion          - Optional  : Question input (Str)
        menuSize               - Optional  : Size of the menu (Int)
        autoAddQuit            - Optional  : automatically add a quit option (Bool)
        onlyReturnNumber       - Optional  : only numbers are allowed to return (Bool)
        allowedCharacters      - Optional  : specifier which character(s) are allowed if onlyReturnNumber is False, separated with ';' (str)
        acceptedQuitCharacters - Optional  : specifier which character is allowed if onlyReturnNumber is False for quit (str)

    """
    return simple_console_menu_block(
        menuName,
        menuItems,
        input_question=inputQuestion,
        menu_size=menuSize,
        auto_add_quit=autoAddQuit,
        only_return_number=onlyReturnNumber,
        allowed_characters=allowedCharacters,
        accepted_quit_characters=acceptedQuitCharacters,
    )
