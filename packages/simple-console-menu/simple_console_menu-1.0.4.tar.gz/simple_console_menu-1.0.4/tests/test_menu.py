import pytest
from unittest.mock import patch, call
import sys
from io import StringIO

from simple_console_menu.Menu import simple_console_menu, simple_console_menu_block


class TestSimpleConsoleMenu:
    """Test cases for simple_console_menu function"""

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_basic_menu_numeric_input(self, mock_print, mock_input):
        """Test basic menu with numeric input"""
        result = simple_console_menu("Test Menu", ["Option 1", "Option 2"])
        
        assert result == 1
        assert mock_input.called
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        menu_output = " ".join(print_calls)
        assert "Test Menu" in menu_output
        assert "1. Option 1" in menu_output
        assert "2. Option 2" in menu_output

    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_menu_with_multiple_options(self, mock_print, mock_input):
        """Test menu with multiple options"""
        items = ["First", "Second", "Third"]
        result = simple_console_menu("Multi Menu", items)
        
        assert result == 2

    @patch('builtins.input', return_value='3')
    @patch('builtins.print')
    def test_menu_with_auto_quit(self, mock_print, mock_input):
        """Test menu with auto quit option"""
        with pytest.raises(SystemExit):
            simple_console_menu("Test Menu", ["Option 1", "Option 2"], auto_add_quit=True)

    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('builtins.print')
    def test_invalid_then_valid_input(self, mock_print, mock_input):
        """Test handling of invalid input followed by valid input"""
        result = simple_console_menu("Test Menu", ["Option 1"])
        
        assert result == 1
        assert mock_input.call_count == 2

    @patch('builtins.input', return_value='a')
    @patch('builtins.print')
    def test_string_input_when_allowed(self, mock_print, mock_input):
        """Test string input when only_return_number is False"""
        result = simple_console_menu(
            "Test Menu", 
            ["Option 1"], 
            only_return_number=False,
            allowed_characters=["a", "b", "c"]
        )
        
        assert result == "a"

    @patch('builtins.input', return_value='a')
    @patch('builtins.print')
    def test_string_input_when_allowed_string(self, mock_print, mock_input):
        """Test string input when only_return_number is False"""
        result = simple_console_menu(
            "Test Menu", 
            ["Option 1"], 
            only_return_number=False,
            allowed_characters="a;b;c"
        )
        
        assert result == "a"

    @patch('builtins.input', return_value='q')
    @patch('builtins.print')
    def test_quit_character(self, mock_print, mock_input):
        """Test quit character functionality"""
        with pytest.raises(SystemExit):
            simple_console_menu(
                "Test Menu", 
                ["Option 1"], 
                only_return_number=False,
                allowed_characters="a;b;c",
                accepted_quit_characters="q"
            )

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_custom_input_question(self, mock_print, mock_input):
        """Test custom input question"""
        result = simple_console_menu(
            "Test Menu", 
            ["Option 1"], 
            input_question="Choose an option: "
        )
        
        assert result == 1
        mock_input.assert_called_with("Choose an option: ")

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_custom_menu_size(self, mock_print, mock_input):
        """Test custom menu size"""
        result = simple_console_menu("Test Menu", ["Option 1"], menu_size=50)
        
        assert result == 1
        # Check that the separator line uses the custom size
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("50" in str(call) or "-" * 50 in str(call) for call in print_calls)

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_string_menu_items(self, mock_print, mock_input):
        """Test menu items provided as semicolon-separated string"""
        result = simple_console_menu("Test Menu", "Option 1;Option 2;Option 3")
        
        assert result == 1

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_return_menu_item_numeric_choice(self, mock_print, mock_input):
        """Test return_menu_item=True returns the actual menu item text"""
        result = simple_console_menu(
            "Test Menu", 
            ["First Option", "Second Option", "Third Option"],
            return_menu_item=True
        )
        
        assert result == "First Option"

    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_return_menu_item_second_choice(self, mock_print, mock_input):
        """Test return_menu_item=True returns correct item for choice 2"""
        result = simple_console_menu(
            "Test Menu", 
            ["Alpha", "Beta", "Gamma"],
            return_menu_item=True
        )
        
        assert result == "Beta"

    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_return_menu_item_out_of_range(self, mock_print, mock_input):
        """Test return_menu_item=True raises error for out of range choice"""
        with pytest.raises(ValueError, match="Choice number out of range"):
            simple_console_menu(
                "Test Menu", 
                ["Option 1", "Option 2"],
                return_menu_item=True
            )

    @patch('builtins.input', return_value='0')
    @patch('builtins.print')
    def test_return_menu_item_zero_choice(self, mock_print, mock_input):
        """Test return_menu_item=True raises error for choice 0"""
        with pytest.raises(ValueError, match="Choice number out of range"):
            simple_console_menu(
                "Test Menu", 
                ["Option 1", "Option 2"],
                return_menu_item=True
            )

    @patch('builtins.input', return_value='test')
    @patch('builtins.print')
    def test_return_menu_item_string_choice_valid(self, mock_print, mock_input):
        """Test return_menu_item=True with string choice that matches menu item"""
        result = simple_console_menu(
            "Test Menu", 
            ["test", "other", "option"],
            only_return_number=False,
            allowed_characters="test;other;option",
            return_menu_item=True
        )
        
        assert result == "test"

    @patch('builtins.input', return_value='invalid')
    @patch('builtins.print')
    def test_return_menu_item_string_choice_invalid(self, mock_print, mock_input):
        """Test return_menu_item=True with string choice that doesn't match menu items"""
        with pytest.raises(ValueError, match="Choice not in menu items"):
            simple_console_menu(
                "Test Menu", 
                ["test", "other", "option"],
                only_return_number=False,
                allowed_characters="test;other;option;invalid",
                return_menu_item=True
            )

    @patch('builtins.input', return_value='3')
    @patch('builtins.print')
    def test_return_menu_item_with_auto_quit(self, mock_print, mock_input):
        """Test return_menu_item=True with auto_add_quit option"""
        with pytest.raises(SystemExit):
            simple_console_menu(
                "Test Menu", 
                ["Option 1", "Option 2"],
                auto_add_quit=True,
                return_menu_item=True
            )

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_simple_menu_empty_name(self, mock_print, mock_input):
        """Test simple menu with empty name doesn't add extra spaces"""
        result = simple_console_menu("", ["Option 1", "Option 2"])
        
        assert result == 1
        
        # Get all print calls
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # The first print call should be just dashes, no spaces
        first_line = print_calls[0] if print_calls else ""
        # Should be 76 dashes, no spaces
        assert first_line == "-" * 76
        # Should not contain extra spaces
        assert "  " not in first_line

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_simple_menu_empty_name_custom_size(self, mock_print, mock_input):
        """Test simple menu with empty name and custom size"""
        result = simple_console_menu("", ["Option 1"], menu_size=40)
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        first_line = print_calls[0] if print_calls else ""
        # Should be exactly 40 dashes
        assert first_line == "-" * 40
        assert len(first_line) == 40

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_simple_menu_whitespace_only_name(self, mock_print, mock_input):
        """Test simple menu with whitespace-only name"""
        result = simple_console_menu("   ", ["Option 1"])
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # Should treat whitespace as a valid name and center it
        first_line = print_calls[0] if print_calls else ""
        assert "   " in first_line  # The whitespace name should be present
        assert first_line.count("-") > 0  # Should have dashes around it

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_empty_name_vs_normal_name_width_consistency(self, mock_print, mock_input):
        """Test that empty name and normal name produce same total width"""
        # Test with normal name
        mock_print.reset_mock()
        simple_console_menu("Test", ["Option 1"], menu_size=50)
        
        normal_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                normal_calls.append(call_text)
        
        # Test with empty name
        mock_print.reset_mock()
        mock_input.return_value = '1'  # Reset input mock
        simple_console_menu("", ["Option 1"], menu_size=50)
        
        empty_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                empty_calls.append(call_text)
        
        # Both should have lines that are exactly 50 characters wide
        normal_first_line = normal_calls[0] if normal_calls else ""
        empty_first_line = empty_calls[0] if empty_calls else ""
        
        # Check that the bottom separator lines are the same length
        normal_bottom_separator = [line for line in normal_calls if line == "-" * 50]
        empty_bottom_separator = [line for line in empty_calls if line == "-" * 50]
        
        # Both should have at least one separator line of the correct size
        assert len(normal_bottom_separator) > 0
        assert len(empty_bottom_separator) > 0
        
        # The bottom separator should be the same for both
        assert normal_bottom_separator[-1] == empty_bottom_separator[-1] == "-" * 50
        
        # Check that both produce lines of consistent width (50 characters)
        # The first line might be different (title vs just dashes), but should be same width
        assert len(normal_first_line) == len(empty_first_line) == 50
        
        # Empty name should be just dashes
        assert empty_first_line == "-" * 50
        
        # Normal name should contain the title with dashes around it
        assert "Test" in normal_first_line
        assert "-" in normal_first_line

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_simple_menu_empty_name_with_auto_quit(self, mock_print, mock_input):
        """Test simple menu with empty name and auto quit"""
        result = simple_console_menu("", ["Option 1"], auto_add_quit=True)
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # Should still be just dashes
        first_line = print_calls[0] if print_calls else ""
        assert first_line == "-" * 76

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_simple_menu_empty_name_with_return_menu_item(self, mock_print, mock_input):
        """Test simple menu with empty name and return_menu_item=True"""
        result = simple_console_menu("", ["Test Option"], return_menu_item=True)
        
        assert result == "Test Option"
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        first_line = print_calls[0] if print_calls else ""
        assert first_line == "-" * 76


class TestSimpleConsoleMenuBlock:
    """Test cases for simple_console_menu_block function"""

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_basic_block_menu(self, mock_print, mock_input):
        """Test basic block menu with box formatting"""
        result = simple_console_menu_block("Block Menu", ["Option 1", "Option 2"])
        
        assert result == 1
        
        # Verify box characters are used
        print_calls = [str(call) for call in mock_print.call_args_list]
        output = " ".join(print_calls)
        assert "╭" in output or "╮" in output or "│" in output or "╰" in output

    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_block_menu_multiple_options(self, mock_print, mock_input):
        """Test block menu with multiple options"""
        items = ["First", "Second", "Third", "Fourth"]
        result = simple_console_menu_block("Block Menu", items)
        
        assert result == 2

    @patch('builtins.input', return_value='3')
    @patch('builtins.print')
    def test_block_menu_with_auto_quit(self, mock_print, mock_input):
        """Test block menu with auto quit option"""
        with pytest.raises(SystemExit):
            simple_console_menu_block("Block Menu", ["Option 1", "Option 2"], auto_add_quit=True)

    @patch('builtins.input', side_effect=['invalid', '1'])
    @patch('builtins.print')
    def test_block_menu_invalid_input_handling(self, mock_print, mock_input):
        """Test block menu handling of invalid input"""
        result = simple_console_menu_block("Block Menu", ["Option 1"])
        
        assert result == 1
        assert mock_input.call_count == 2

    @patch('builtins.input', return_value='x')
    @patch('builtins.print')
    def test_block_menu_string_input(self, mock_print, mock_input):
        """Test block menu with string input when allowed"""
        result = simple_console_menu_block(
            "Block Menu", 
            ["Option 1"], 
            only_return_number=False,
            allowed_characters="x;y;z"
        )
        
        assert result == "x"

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_even_title_length(self, mock_print, mock_input):
        """Test block menu with even title length for proper centering"""
        result = simple_console_menu_block("Even", ["Option 1"], menu_size=20)
        
        assert result == 1
        # Verify the menu renders without errors

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_odd_title_length(self, mock_print, mock_input):
        """Test block menu with odd title length for proper centering"""
        result = simple_console_menu_block("Odd Title", ["Option 1"], menu_size=21)
        
        assert result == 1
        # Verify the menu renders without errors

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_return_menu_item(self, mock_print, mock_input):
        """Test block menu with return_menu_item=True"""
        result = simple_console_menu_block(
            "Block Menu", 
            ["First Choice", "Second Choice"],
            return_menu_item=True
        )
        
        assert result == "First Choice"

    @patch('builtins.input', return_value='3')
    @patch('builtins.print')
    def test_block_menu_return_menu_item_third_choice(self, mock_print, mock_input):
        """Test block menu return_menu_item=True returns correct item for choice 3"""
        result = simple_console_menu_block(
            "Block Menu", 
            ["Alpha", "Beta", "Gamma", "Delta"],
            return_menu_item=True
        )
        
        assert result == "Gamma"

    @patch('builtins.input', return_value='10')
    @patch('builtins.print')
    def test_block_menu_return_menu_item_out_of_range(self, mock_print, mock_input):
        """Test block menu return_menu_item=True raises error for out of range choice"""
        with pytest.raises(ValueError, match="Choice number out of range"):
            simple_console_menu_block(
                "Block Menu", 
                ["Option 1", "Option 2"],
                return_menu_item=True
            )

    @patch('builtins.input', return_value='custom')
    @patch('builtins.print')
    def test_block_menu_return_menu_item_string_choice(self, mock_print, mock_input):
        """Test block menu return_menu_item=True with string choice"""
        result = simple_console_menu_block(
            "Block Menu", 
            ["custom", "menu", "items"],
            only_return_number=False,
            allowed_characters=["custom", "menu", "items"],
            return_menu_item=True
        )
        
        assert result == "custom"

    @patch('builtins.input', return_value='custom')
    @patch('builtins.print')
    def test_block_menu_return_menu_item_string_choice_string(self, mock_print, mock_input):
        """Test block menu return_menu_item=True with string choice"""
        result = simple_console_menu_block(
            "Block Menu", 
            ["custom", "menu", "items"],
            only_return_number=False,
            allowed_characters="custom;menu;items",
            return_menu_item=True
        )
        
        assert result == "custom"

    @patch('builtins.input', return_value='notfound')
    @patch('builtins.print')
    def test_block_menu_return_menu_item_invalid_string(self, mock_print, mock_input):
        """Test block menu return_menu_item=True with invalid string choice"""
        with pytest.raises(ValueError, match="Choice not in menu items"):
            simple_console_menu_block(
                "Block Menu", 
                ["valid", "options", "only"],
                only_return_number=False,
                allowed_characters="valid;options;only;notfound",
                return_menu_item=True
            )


class TestMenuComparison:
    """Test cases comparing both menu functions"""

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_both_menus_same_functionality(self, mock_print, mock_input):
        """Test that both menu functions return the same result for same input"""
        menu_items = ["Option 1", "Option 2"]
        
        # Reset mocks between calls
        mock_input.reset_mock()
        mock_print.reset_mock()
        
        result1 = simple_console_menu("Test", menu_items)
        
        mock_input.reset_mock()
        mock_print.reset_mock()
        mock_input.return_value = '1'
        
        result2 = simple_console_menu_block("Test", menu_items)
        
        assert result1 == result2 == 1

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_both_menus_different_output_format(self, mock_print, mock_input):
        """Test that the two menu functions produce different visual output"""
        menu_items = ["Option 1"]
        
        # Test simple menu
        mock_print.reset_mock()
        simple_console_menu("Test", menu_items)
        simple_output = " ".join(str(call) for call in mock_print.call_args_list)
        
        # Test block menu
        mock_print.reset_mock()
        mock_input.return_value = '1'  # Reset input mock
        simple_console_menu_block("Test", menu_items)
        block_output = " ".join(str(call) for call in mock_print.call_args_list)
        
        # Simple menu should use dashes, block menu should use box characters
        assert "-" in simple_output
        assert any(char in block_output for char in ["╭", "╮", "│", "╰", "─"])

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_empty_name(self, mock_print, mock_input):
        """Test block menu with empty name doesn't add extra spaces"""
        result = simple_console_menu_block("", ["Option 1", "Option 2"])
        
        assert result == 1
        
        # Get all print calls
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # The first print call should be box top without spaces
        first_line = print_calls[0] if print_calls else ""
        # Should be ╭ + 74 dashes + ╮ (total width 76)
        expected = "╭" + "─" * 74 + "╮"
        assert first_line == expected
        # Should not contain extra spaces in the middle
        assert "  " not in first_line.replace(" ", "")  # Remove any single spaces

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_empty_name_custom_size(self, mock_print, mock_input):
        """Test block menu with empty name and custom size"""
        result = simple_console_menu_block("", ["Option 1"], menu_size=40)
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        first_line = print_calls[0] if print_calls else ""
        # Should be ╭ + 38 dashes + ╮ (total width 40)
        expected = "╭" + "─" * 38 + "╮"
        assert first_line == expected
        assert len(first_line) == 40

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_whitespace_only_name(self, mock_print, mock_input):
        """Test block menu with whitespace-only name"""
        result = simple_console_menu_block("   ", ["Option 1"])
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # Should treat whitespace as a valid name and center it
        first_line = print_calls[0] if print_calls else ""
        assert "╭" in first_line and "╮" in first_line
        assert "   " in first_line  # The whitespace name should be present

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_empty_name_vs_normal_name_width_consistency(self, mock_print, mock_input):
        """Test that block menu empty name and normal name produce same total width"""
        # Test with normal name
        mock_print.reset_mock()
        simple_console_menu_block("Test", ["Option 1"], menu_size=50)
        
        normal_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                normal_calls.append(call_text)
        
        # Test with empty name
        mock_print.reset_mock()
        mock_input.return_value = '1'  # Reset input mock
        simple_console_menu_block("", ["Option 1"], menu_size=50)
        
        empty_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                empty_calls.append(call_text)
        
        # Both should have box lines that are exactly 50 characters wide
        normal_first_line = normal_calls[0] if normal_calls else ""
        empty_first_line = empty_calls[0] if empty_calls else ""
        
        # Both first lines should be exactly 50 characters
        assert len(normal_first_line) == 50
        assert len(empty_first_line) == 50
        
        # Empty name should be just box characters
        expected_empty = "╭" + "─" * 48 + "╮"
        assert empty_first_line == expected_empty

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_empty_name_with_auto_quit(self, mock_print, mock_input):
        """Test block menu with empty name and auto quit"""
        result = simple_console_menu_block("", ["Option 1"], auto_add_quit=True)
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # Should still be just box with dashes
        first_line = print_calls[0] if print_calls else ""
        expected = "╭" + "─" * 74 + "╮"
        assert first_line == expected

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_empty_name_with_return_menu_item(self, mock_print, mock_input):
        """Test block menu with empty name and return_menu_item=True"""
        result = simple_console_menu_block("", ["Test Option"], return_menu_item=True)
        
        assert result == "Test Option"
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        first_line = print_calls[0] if print_calls else ""
        expected = "╭" + "─" * 74 + "╮"
        assert first_line == expected

    @patch('builtins.input', return_value='1')
    @patch('builtins.print')
    def test_block_menu_empty_name_box_structure(self, mock_print, mock_input):
        """Test that block menu with empty name maintains proper box structure"""
        result = simple_console_menu_block("", ["Option 1", "Option 2"], menu_size=30)
        
        assert result == 1
        
        print_calls = []
        for call_obj in mock_print.call_args_list:
            if call_obj[0]:
                call_text = " ".join(str(arg) for arg in call_obj[0])
                print_calls.append(call_text)
        
        # Check box structure
        assert len(print_calls) >= 4  # At least top, 2 items, bottom
        
        # Top should be proper box top
        top_line = print_calls[0]
        assert top_line.startswith("╭") and top_line.endswith("╮")
        assert len(top_line) == 30
        
        # Bottom should be proper box bottom
        bottom_line = print_calls[-1]
        assert bottom_line.startswith("╰") and bottom_line.endswith("╯")
        assert len(bottom_line) == 30
        
        # Middle lines should have proper sides
        for i in range(1, len(print_calls) - 1):
            line = print_calls[i]
            assert line.startswith("│") and line.endswith("│")
            assert len(line) == 30