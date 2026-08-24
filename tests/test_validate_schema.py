import json
from unittest.mock import mock_open, patch

from jsonschema import ValidationError

from src.utils.validate_schema import main


def test_main_success(capsys):
    """Verifies successful schema validation and correct success output message."""
    with patch("builtins.open", mock_open(read_data="{}")), \
         patch("json.load", return_value={"type": "object"}), \
         patch("jsonschema.validate") as mock_validate, \
         patch("sys.exit") as mock_exit:
        
        main()
        
        mock_validate.assert_called_once()
        mock_exit.assert_not_called()
        captured = capsys.readouterr()
        assert "Schema Compliance Audit PASSED" in captured.out


def test_main_validation_error(capsys):
    """Verifies handling of a jsonschema ValidationError (Constitution Violation branch)."""
    with patch("builtins.open", mock_open(read_data="{}")), \
         patch("json.load", return_value={}), \
         patch("jsonschema.validate", side_effect=ValidationError("Missing required property 'nx'")), \
         patch("sys.exit") as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "CONSTITUTION VIOLATION" in captured.err
        assert "Missing required property 'nx'" in captured.err


def test_main_os_error(capsys):
    """Verifies handling of OSError when schema or output files cannot be accessed."""
    with patch("builtins.open", side_effect=OSError("No such file or directory")), \
         patch("sys.exit") as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "CRITICAL ERROR" in captured.err
        assert "No such file or directory" in captured.err


def test_main_json_decode_error(capsys):
    """Verifies handling of malformed JSON input or schema files."""
    with patch("builtins.open", mock_open(read_data="invalid json data")), \
         patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "invalid json data", 0)), \
         patch("sys.exit") as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "CRITICAL ERROR" in captured.err


def test_main_type_error(capsys):
    """Verifies handling of unexpected TypeError or ValueError exceptions during execution."""
    with patch("builtins.open", mock_open(read_data="{}")), \
         patch("json.load", return_value={}), \
         patch("jsonschema.validate", side_effect=TypeError("Unsupported type encountered")), \
         patch("sys.exit") as mock_exit:
        
        main()
        
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "CRITICAL ERROR" in captured.err
        assert "Unsupported type encountered" in captured.err
