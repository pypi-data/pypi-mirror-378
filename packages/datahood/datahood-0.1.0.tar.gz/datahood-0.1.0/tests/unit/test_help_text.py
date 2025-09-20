"""Tests for CLI help text components."""

from datahood.cli.help_text import CLI_EXAMPLES
from datahood.cli.help_text import CLICommands
from datahood.cli.help_text import ExampleCategories
from datahood.cli.help_text import get_all_commands
from datahood.cli.help_text import get_examples_by_category
from datahood.cli.help_text import validate_command_format


class TestCLICommands:
    """Test CLI command constants."""

    def test_transfer_commands_not_empty(self):
        """Test that transfer command constants are not empty."""
        assert CLICommands.TRANSFER_MONGO_TO_BSON
        assert CLICommands.TRANSFER_BSON_TO_MONGO
        assert CLICommands.TRANSFER_MONGO_TO_MONGO

    def test_schema_commands_not_empty(self):
        """Test that schema command constants are not empty."""
        assert CLICommands.SCHEMA_FROM_MONGO
        assert CLICommands.SCHEMA_FROM_BSON

    def test_import_commands_not_empty(self):
        """Test that import command constants are not empty."""
        assert CLICommands.IMPORT_BSON_SIMPLE

    def test_commands_start_with_dh(self):
        """Test that all CLI commands start with 'dh'."""
        commands = [
            CLICommands.TRANSFER_MONGO_TO_BSON,
            CLICommands.TRANSFER_BSON_TO_MONGO,
            CLICommands.SCHEMA_FROM_MONGO,
            CLICommands.SCHEMA_FROM_BSON,
            CLICommands.IMPORT_BSON_SIMPLE,
        ]
        for command in commands:
            assert command.startswith("dh "), (
                f"Command should start with 'dh ': {command}"
            )


class TestCLIExamples:
    """Test CLI examples dictionary."""

    def test_cli_examples_not_empty(self):
        """Test that CLI examples dictionary is not empty."""
        assert CLI_EXAMPLES
        assert len(CLI_EXAMPLES) > 0

    def test_cli_examples_have_valid_keys(self):
        """Test that CLI examples have properly formatted keys."""
        expected_prefixes = ["main_", "transfer_", "schema_", "import_"]
        for key in CLI_EXAMPLES.keys():
            assert any(key.startswith(prefix) for prefix in expected_prefixes), (
                f"Key '{key}' has invalid prefix"
            )

    def test_cli_examples_values_are_commands(self):
        """Test that all CLI example values are valid command strings."""
        for key, value in CLI_EXAMPLES.items():
            assert isinstance(value, str), f"Example '{key}' should be a string"
            assert len(value) > 0, f"Example '{key}' should not be empty"


class TestExampleCategories:
    """Test the ExampleCategories enum."""

    def test_enum_values(self):
        """Test that enum has expected values."""
        expected_values = {"main", "transfer", "schema", "import"}
        actual_values = {category.value for category in ExampleCategories}
        assert actual_values == expected_values

    def test_enum_members(self):
        """Test that enum has expected members."""
        assert hasattr(ExampleCategories, "MAIN")
        assert hasattr(ExampleCategories, "TRANSFER")
        assert hasattr(ExampleCategories, "SCHEMA")
        assert hasattr(ExampleCategories, "IMPORT")


class TestHelperFunctions:
    """Test helper functions."""

    def test_get_examples_by_category(self):
        """Test getting examples by category."""
        transfer_examples = get_examples_by_category(ExampleCategories.TRANSFER)
        assert isinstance(transfer_examples, dict)

        # Should only contain transfer examples
        for key in transfer_examples:
            assert key.startswith("transfer_")

    def test_get_all_commands(self):
        """Test getting all commands."""
        all_commands = get_all_commands()
        assert isinstance(all_commands, list)
        assert len(all_commands) > 0

    def test_validate_command_format(self):
        """Test command format validation."""
        # Valid commands
        assert validate_command_format("dh transfer mongo-to-bson")
        assert validate_command_format("dh schema from-mongo")

        # Invalid commands
        assert not validate_command_format("transfer mongo-to-bson")  # Missing dh
        assert not validate_command_format("dh")  # Too short
        assert not validate_command_format("")  # Empty


class TestCommandConsistency:
    """Test consistency across command definitions."""

    def test_all_categories_represented(self):
        """Test that all categories have examples in CLI_EXAMPLES."""
        for category in ExampleCategories:
            examples = get_examples_by_category(category)
            assert len(examples) > 0, f"Category '{category.value}' has no examples"

    def test_no_duplicate_commands(self):
        """Test that there are no duplicate command strings."""
        all_commands = get_all_commands()
        assert len(all_commands) == len(set(all_commands)), "Duplicate commands found"
