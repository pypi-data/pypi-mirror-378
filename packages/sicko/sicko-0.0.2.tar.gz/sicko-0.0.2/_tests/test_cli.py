"""
Tests for sicko CLI module
"""

from io import StringIO
from unittest.mock import patch

from sicko.cli import main


def test_main_function_exists():
    """Test that main function exists and is callable"""
    assert callable(main)


def test_main_prints_expected_output():
    """Test that main function prints 'sicko works!'"""
    # Capture stdout
    captured_output = StringIO()
    with patch("sys.stdout", captured_output):
        main()

    output = captured_output.getvalue().strip()
    assert output == "sicko works!"


def test_main_function_has_no_parameters():
    """Test that main function takes no parameters"""
    import inspect

    sig = inspect.signature(main)
    assert len(sig.parameters) == 0


def test_main_returns_none():
    """Test that main function returns None"""
    result = main()
    assert result is None


def test_main_function_docstring():
    """Test that main function has proper docstring"""
    assert main.__doc__ is not None
    assert "entrypoint" in main.__doc__.lower()
