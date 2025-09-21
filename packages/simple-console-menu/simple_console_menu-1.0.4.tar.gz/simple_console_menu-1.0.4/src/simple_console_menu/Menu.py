from enum import Enum
import math


def _print_top_row(menu_name: str, menu_name_length: float, menu_size: int) -> None:
    """
    Generates the top row of the menu
    :param menu_name: The name of the menu
    :param menu_size: The size of the menu
    :return: The top row of the menu
    """
    if menu_name:
        if (menu_name_length % 2) == 0:
            # even
            print(int(menu_name_length) * "-", menu_name, int(menu_name_length) * "-")
        else:
            # uneven
            menu_name_length1 = math.ceil(menu_name_length)
            menu_name_length2 = int(math.floor(menu_name_length))
            print(int(menu_name_length1) * "-", menu_name, int(menu_name_length2) * "-")
    else:
        print(menu_size * "-")


def simple_console_menu(
    menu_name: str,
    menu_items: list[str],
    input_question: str = "What do you want to do:",
    menu_size: int = 76,
    auto_add_quit: bool = False,
    only_return_number: bool = True,
    allowed_characters: list[str] | str | None = None,
    accepted_quit_characters: str = "",
    return_menu_item: bool = False,
) -> int | str:
    """
    Makes a menu

    parameters:
        menu_name                - Required  : name of the menu (Str)
        menu_items               - Required  : menu items ["item 1","item 2"] (List)
        input_question           - Optional  : Question input (Str)
        menu_size                - Optional  : Size of the menu (Int)
        auto_add_quit            - Optional  : automatically add a quit option (Bool)
        only_return_number       - Optional  : only numbers are allowed to return (Bool)
        allowed_characters       - Optional  : specifier which character(s) are allowed if only_return_number is False (list or str separated with ';')
        accepted_quit_characters - Optional  : specifier which character is allowed if only_return_number is False for quit (str)
        return_menu_item         - Optional  : return the menu item instead of the number (Bool)

    """
    choose_loop = True
    menu_items_list = []
    allowed_characters_list = []
    choose = ""
    if isinstance(allowed_characters, str):
        allowed_characters_list = allowed_characters.split(";")
    elif isinstance(allowed_characters, list):
        allowed_characters_list = allowed_characters
    else:
        allowed_characters_list = []

    if isinstance(menu_items, str):
        menu_items_list = str(menu_items).split(";")
    else:
        menu_items_list = menu_items

    if auto_add_quit:
        menu_items_list.append("Quit")
    menu_number = 1
    choose_amount = 0

    menu_name_length = len(menu_name) + 2
    menu_name_length = menu_size - menu_name_length
    menu_name_length /= 2

    _print_top_row(menu_name, menu_name_length, menu_size)

    for x in menu_items_list:
        print(f"{menu_number}. {x}")
        menu_number += 1
    print(menu_size * "-")

    while choose_loop:
        choose = input(input_question)
        if return_menu_item:
            if choose.isdigit():
                choose_int = int(choose)
                if 0 < choose_int <= len(menu_items_list):
                    choose_loop = False
        elif only_return_number:
            if choose.isdigit():
                choose_loop = False
        else:
            if accepted_quit_characters != "":
                if (
                    (choose != "" and choose in allowed_characters_list)
                    or choose.isdigit()
                    or choose == accepted_quit_characters
                ):
                    choose_loop = False
            elif (
                choose != "" and choose in allowed_characters_list
            ) or choose.isdigit():
                choose_loop = False

        if choose_amount >= 20 and choose_loop:
            menu_number = 1

            _print_top_row(menu_name, menu_name_length, menu_size)

            for x in menu_items_list:
                print(f"{menu_number}. {x}")
                menu_number += 1
            print(menu_size * "-")
            choose_amount = 1
        choose_amount += 1

    if choose.isdigit():
        if int(choose) == menu_number - 1 and auto_add_quit:
            quit()
    elif choose == accepted_quit_characters:
        quit()

    if return_menu_item:
        if choose.isdigit():
            choose = int(choose)
            if 0 < choose <= len(menu_items_list):
                return menu_items_list[choose - 1]
            else:
                raise ValueError("Choice number out of range")
        else:
            if choose in menu_items_list:
                return choose
            else:
                raise ValueError("Choice not in menu items")

    if only_return_number:
        return int(choose)
    else:
        if choose.isdigit():
            return int(choose)
        else:
            return choose


def _print_top_row_block(
    menu_name: str, menu_name_length: float, menu_size: int
) -> None:
    """
    Generates the top row of the menu with a block
    :param menu_name: The name of the menu
    :param menu_size: The size of the menu
    :return: The top row of the menu
    """
    if menu_name:
        if (menu_name_length % 2) == 0:
            # even
            print(
                "╭" + int(menu_name_length - 1) * "─",
                menu_name,
                int(menu_name_length - 1) * "─" + "╮",
            )
        else:
            # uneven
            menu_name_length1 = math.ceil(menu_name_length)
            menu_name_length2 = int(math.floor(menu_name_length))
            print(
                "╭" + int(menu_name_length1 - 1) * "─",
                menu_name,
                int(menu_name_length2 - 1) * "─" + "╮",
            )
    else:
        print("╭" + (menu_size - 2) * "─" + "╮")


def simple_console_menu_block(
    menu_name: str,
    menu_items: list[str],
    input_question: str = "What do you want to do:",
    menu_size: int = 76,
    auto_add_quit: bool = False,
    only_return_number: bool = True,
    allowed_characters: list[str] | str | None = None,
    accepted_quit_characters: str = "",
    return_menu_item: bool = False,
) -> int | str:
    """
    Makes a menu with a box arround it

    parameters:
        menu_name                - Required  : name of the menu (Str)
        menu_items               - Required  : menu items ["item 1","item 2"] (List)
        input_question           - Optional  : Question input (Str)
        menu_size                - Optional  : Size of the menu (Int)
        auto_add_quit            - Optional  : automatically add a quit option (Bool)
        only_return_number       - Optional  : only numbers are allowed to return (Bool)
        allowed_characters       - Optional  : specifier which character(s) are allowed if only_return_number is False (list or str separated with ';')
        accepted_quit_characters - Optional  : specifier which character is allowed if only_return_number is False for quit (str)
        return_menu_item         - Optional  : return the menu item instead of the number (Bool)

    """
    choose_loop = True
    menu_items_list = []
    allowed_characters_list = []
    choose = ""

    if isinstance(allowed_characters, str):
        allowed_characters_list = allowed_characters.split(";")
    elif isinstance(allowed_characters, list):
        allowed_characters_list = allowed_characters
    else:
        allowed_characters_list = []

    if isinstance(menu_items, str):
        menu_items_list = str(menu_items).split(";")
    else:
        menu_items_list = menu_items

    if auto_add_quit:
        menu_items_list.append("Quit")

    menu_number = 1
    choose_amount = 0
    menu_name_length = len(menu_name) + 2
    menu_name_length = menu_size - menu_name_length
    menu_name_length /= 2

    _print_top_row_block(menu_name, menu_name_length, menu_size)

    for x in menu_items_list:
        menu_items_with_numbers = str(menu_number) + ". " + x
        print(
            f"│{menu_items_with_numbers}"
            + ((menu_size - 2) - len(menu_items_with_numbers)) * " "
            + "│"
        )
        menu_number += 1
    print("╰" + (menu_size - 2) * "─" + "╯")

    while choose_loop:
        choose = input(input_question)
        if return_menu_item:
            if choose.isdigit():
                choose_int = int(choose)
                if 0 < choose_int <= len(menu_items_list):
                    choose_loop = False
        elif only_return_number:
            if choose.isdigit():
                choose_loop = False
        else:
            if accepted_quit_characters != "":
                if (
                    (choose != "" and choose in allowed_characters_list)
                    or choose.isdigit()
                    or choose == accepted_quit_characters
                ):
                    choose_loop = False
            elif (
                choose != "" and choose in allowed_characters_list
            ) or choose.isdigit():
                choose_loop = False

        if choose_amount >= 20 and choose_loop:
            menu_number = 1

            _print_top_row_block(menu_name, menu_name_length, menu_size)

            for x in menu_items_list:
                menu_items_with_numbers = str(menu_number) + ". " + x
                print(
                    f"│{menu_items_with_numbers}"
                    + ((menu_size - 2) - len(menu_items_with_numbers)) * " "
                    + "│"
                )
                menu_number += 1
            print("╰" + (menu_size - 2) * "─" + "╯")
            choose_amount = 1
        choose_amount += 1

    if choose.isdigit():
        if int(choose) == menu_number - 1 and auto_add_quit:
            quit()
    elif choose == accepted_quit_characters:
        quit()

    if return_menu_item:
        if choose.isdigit():
            choose = int(choose)
            if 0 < choose <= len(menu_items_list):
                return menu_items_list[choose - 1]
            else:
                raise ValueError("Choice number out of range")
        else:
            if choose in menu_items_list:
                return choose
            else:
                raise ValueError("Choice not in menu items")

    if only_return_number:
        return int(choose)
    else:
        if choose.isdigit():
            return int(choose)
        else:
            return choose


class ValueToReturnEmptyError(Exception):
    """
    raised when the value to return is empty
    """

    def __init__(self, message: str = "Value to return is empty") -> None:
        super().__init__(message)


class menu:
    """
    allows you to create a menu
    """

    class menu_data_type(Enum):
        """
        data types for the menu
        possible values:
        STRING
        INT
        FLOAT
        """

        STRING = 1
        INT = 2
        FLOAT = 3

    class display_type(Enum):
        """
        display types for the menu
        possible values:
        BLOCK
        SIMPLE
        """

        BLOCK = 1
        SIMPLE = 2

    def __init__(
        self,
        menu_name: str,
        menu_items: list,
        input_question: str = "What do you want to do:",
        menu_size: int = 76,
        auto_add_quit: bool = False,
        return_type: menu_data_type = menu_data_type.INT,
    ) -> None:
        """
        allows you to create a menu
        :param menu_name: name of the menu (Str)
        :param menu_items: menu items ["item 1","item 2"] (List)
        :param input_question: question to ask the user (Str)
        :param menu_size: size of the menu (Int)
        :param auto_add_quit: automatically add a quit option (Bool)
        :return: None
        """
        self.menu_name = menu_name
        self.menu_items = menu_items
        self.input_question = input_question
        self.menu_size = menu_size
        self.auto_add_quit = auto_add_quit
        self.return_type = return_type

    def __str__(self) -> str:
        """
        returns the menu as a string
        :return: menu as a string
        """
        to_return = ""
        for k, v in self.__dict__.items():
            if not k.startswith("_menu__"):
                to_return += f"{k}: {v}, "
        return to_return[:-2]

    def set_menu_name(self, menu_name: str) -> "menu":
        """
        sets the menu name
        :param menu_name: name of the menu (Str)
        :return: None
        """
        self.menu_name = menu_name
        return self

    def set_menu_items(self, menu_items: list) -> "menu":
        """
        sets the menu items
        :param menu_items: menu items ["item 1","item 2"] (List)
        :return: None
        """
        self.menu_items = menu_items
        return self

    def add_menu_item(self, menu_item: str) -> "menu":
        """
        adds a menu item
        :param menu_item: menu item to add (Str)
        :return: None
        """
        self.menu_items.append(menu_item)
        return self

    def set_input_question(self, input_question: str) -> "menu":
        """
        sets the input question
        :param input_question: question to ask the user (Str)
        :return: None
        """
        self.input_question = input_question
        return self

    def set_menu_size(self, menu_size: int) -> "menu":
        """
        sets the menu size
        :param menu_size: size of the menu (Int)
        :return: None
        """
        self.menu_size = menu_size
        return self

    def set_auto_add_quit(self, auto_add_quit: bool) -> "menu":
        """
        sets the auto add quit option
        :param auto_add_quit: automatically add a quit option (Bool)
        :return: None
        """
        self.auto_add_quit = auto_add_quit
        return self

    def set_return_type(self, return_type: menu_data_type) -> "menu":
        """
        sets the return type
        :param return_type: return type (menu_data_type)
        :return: None
        """
        self.return_type = return_type
        return self

    def display(self, menu_display_type: display_type = display_type.BLOCK) -> "menu":
        """
        displays the menu
        :return: None
        """
        self.__menu_items_to_display = self.menu_items
        if self.auto_add_quit:
            self.__menu_items_to_display.append("Quit")
        if menu_display_type == self.display_type.BLOCK:
            self.__menu_number = 1
            self.__choose_amount = 0
            self.__menu_name_length = len(self.menu_name) + 2
            self.__menu_name_length = self.menu_size - self.__menu_name_length
            self.__menu_name_length /= 2
            if (self.__menu_name_length % 2) == 0:
                print(
                    "╭" + int(self.__menu_name_length - 1) * "─",
                    self.menu_name,
                    int(self.__menu_name_length - 1) * "─" + "╮",
                )
            else:
                self.__menu_name_length1 = math.ceil(self.__menu_name_length)
                self.__menu_name_length2 = math.floor(self.__menu_name_length)
                print(
                    "╭" + int(self.__menu_name_length1 - 1) * "─",
                    self.menu_name,
                    int(self.__menu_name_length2 - 1) * "─" + "╮",
                )
            for x in self.__menu_items_to_display:
                self.__menu_items_with_numbers = str(self.__menu_number) + ". " + x
                print(
                    f"│{self.__menu_items_with_numbers}"
                    + ((self.menu_size - 2) - len(self.__menu_items_with_numbers)) * " "
                    + "│"
                )
                self.__menu_number += 1
            print("╰" + (self.menu_size - 2) * "─" + "╯")

        elif menu_display_type == self.display_type.SIMPLE:
            self.__menu_number = 1
            self.__choose_amount = 0
            self.__menu_name_length = len(self.menu_name) + 2
            self.__menu_name_length = self.menu_size - self.__menu_name_length
            self.__menu_name_length /= 2
            if (self.__menu_name_length % 2) == 0:
                # even
                print(
                    int(self.__menu_name_length) * "-",
                    self.menu_name,
                    int(self.__menu_name_length) * "-",
                )
            else:
                # uneven
                menuNameLength1 = math.ceil(self.__menu_name_length)
                menuNameLength2 = int(math.floor(self.__menu_name_length))
                print(
                    int(menuNameLength1) * "-",
                    self.menu_name,
                    int(menuNameLength2) * "-",
                )
            for x in self.__menu_items_to_display:
                print(f"{self.__menu_number}. {x}")
                self.__menu_number += 1
            print(self.menu_size * "-")

        else:
            raise Exception("HOW DID YOU GET HERE?")

        while True:
            self.value_to_return = input(self.input_question)
            if self.return_type == self.menu_data_type.INT:
                try:
                    self.value_to_return = int(self.value_to_return)
                except ValueError:
                    print("You must enter a number")
                else:
                    break
            elif self.return_type == self.menu_data_type.FLOAT:
                try:
                    self.value_to_return = float(self.value_to_return)
                except ValueError:
                    print("You must enter a number")
                else:
                    break
            elif self.return_type == self.menu_data_type.STRING:
                break

        return self

    def get_user_input(self) -> str | int | float:
        """
        returns the user input
        :return: user input (Str | Int | Float)
        :raises ValueToReturnEmptyError: if the value to return is empty
        """
        try:
            return self.value_to_return
        except AttributeError:
            raise ValueToReturnEmptyError("Value to return is empty")


# compatibility layer for older version
def SimpleConsoleMenu(
    menuName: str,
    menuItems: list,
    inputQuestion="What do you want to do:",
    menuSize=76,
    autoAddQuit=False,
    onlyReturnNumber=True,
    allowedCharacters="",
    acceptedQuitCharacters="",
) -> int | str:
    """
    Deprecated, use simple_console_menu instead
    """
    return simple_console_menu(
        menuName,
        menuItems,
        inputQuestion,
        menuSize,
        autoAddQuit,
        onlyReturnNumber,
        allowedCharacters,
        acceptedQuitCharacters,
        False,
    )


def SimpleConsoleMenuBlock(
    menuName: str,
    menuItems: list,
    inputQuestion="What do you want to do:",
    menuSize=76,
    autoAddQuit=False,
    onlyReturnNumber=True,
    allowedCharacters="",
    acceptedQuitCharacters="",
) -> int | str:
    """
    Deprecated, use simple_console_menu instead
    """
    return simple_console_menu_block(
        menuName,
        menuItems,
        inputQuestion,
        menuSize,
        autoAddQuit,
        onlyReturnNumber,
        allowedCharacters,
        acceptedQuitCharacters,
        False,
    )
