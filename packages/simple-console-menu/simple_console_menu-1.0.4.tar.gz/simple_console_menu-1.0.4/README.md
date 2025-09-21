# Simple Consol Menu
this module allows you to create simple console menu. <br>
[![](https://img.shields.io/pypi/dm/simple-console-menu)](
https://pypi.org/project/simple-console-menu/)

## links
[Source](https://github.com/mikeee1/simple-console-menu) <br>
[Documentation](https://github.com/mikeee1/simple-console-menu/wiki) <br>
[Bug Report](https://github.com/mikeee1/simple-console-menu/issues) <br>
[PyPi](https://pypi.org/project/simple-console-menu/) 

## Installation
```
pip install simple-console-menu
```

## Usage
```python
from simple_console_menu import Menu
```

## Example
### SimpleConsoleMenu
---
The first menu is the `SimpleConsoleMenu`. <br>
You can use it by first importing the right file: 
```python
from simple_console_menu import Menu
```

And if you want to use it you can do this:
```python
menu = Menu.simple_console_menu(menu_name: str, menu_items: list[str], input_question: str, menu_size: int = 76, auto_add_quit: bool = False, only_return_number: bool = True, allowed_characters: list[str] | str | None = None, accepted_quit_characters: str = '', return_menu_item: bool = False)
```

With these parameters: <br>
    menu_name                - Required  : name of the menu (Str) <br>
    menu_items               - Required  : menu items ["item 1","item 2"] (List) <br>
    input_question           - Optional  : Question input (Str) <br>
    menu_size                - Optional  : Size of the menu (Int) <br>
    auto_add_quit            - Optional  : automatically add a quit option (Bool) <br>
    only_return_number       - Optional  : only numbers are allowed to return (Bool) <br>
    allowed_characters       - Optional  : specifier which character(s) are allowed if only_return_number is False, separated with ';' (str) <br>
    accepted_quit_characters - Optional  : specifier which character is allowed if only_return_number is False for quit (str) <br>
    return_menu_item         - Optional  : return the menu item instead of the number (Bool) <br>

full example:
```python
from simple_console_menu import Menu

menuNumber = Menu.SimpleConsoleMenu('menu', ["item1","item2","item3","item4","item5"], "Number:", 76, True)

if menuNumber == 1:
    print('item1')
elif menuNumber == 2:
    print('item2')
elif menuNumber == 3:
    print('item3')
elif menuNumber == 4:
    print('item4')
elif menuNumber == 5:
    print('item5')
```

And this wil display

```
----------------------------------- menu -----------------------------------
1. item1
2. item2
3. item3
4. item4
5. item5
6. Quit
----------------------------------------------------------------------------
Number:1
item1
```

There is also `SimpleConsoleMenuBlock` which works the same as `SimpleConsoleMenu` but looks like this:

```
╭────────────────────────────────── menu ──────────────────────────────────╮
│1. item1                                                            │
│2. item2                                                            │
│3. item3                                                            │
│4. item4                                                            │
│5. item5                                                            │
│6. Quit                                                             │
╰──────────────────────────────────────────────────────────────────────────╯
Number:
```

You can also use the `menu` class like this:

```python
from simple_console_menu import Menu

user_input = Menu.menu("Menu", ["item 1", "item 2", "item 3"]).display().get_user_input()
print(user_input)
```