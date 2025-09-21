"""
CLI User Experience Improvements Tests
=====================================

Tests for enhanced CLI user experience including progress indicators,
colored output, interactive prompts, and improved help system.
"""

import pytest
import sys
import io
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import os

from genebot.cli.utils.formatting import (
    ColorFormatter, ProgressIndicator, ProgressBar, Table, InteractivePrompt,
    Banner, TableColumn, Color, Icons
)
from genebot.cli.utils.output_manager import OutputManager, OutputMode
from genebot.cli.utils.completion import CommandCompletion, HelpFormatter, InteractiveHelp
from genebot.cli.result import CommandResult, ResultStatus


class TestColorFormatter:
    """Test color formatting utilities"""
    
    def test_color_formatter_with_colors(self):
        """Test color formatter when colors are enabled"""
        formatter = ColorFormatter(use_colors=True)
        
        # Test basic colorization
        colored_text = formatter.colorize("test", Color.RED)
        assert Color.RED.value in colored_text
        assert Color.RESET.value in colored_text
        assert "test" in colored_text
    
    def test_color_formatter_without_colors(self):
        """Test color formatter when colors are disabled"""
        formatter = ColorFormatter(use_colors=False)
        
        # Test that no color codes are added
        colored_text = formatter.colorize("test", Color.RED)
        assert colored_text == "test"
        assert Color.RED.value not in colored_text
    
    def test_status_formatting(self):
        """Test status message formatting"""
        formatter = ColorFormatter(use_colors=True)
        
        success_msg = formatter.success("Operation completed")
        assert Icons.SUCCESS in success_msg
        assert "Operation completed" in success_msg
        
        error_msg = formatter.error("Operation failed")
        assert Icons.ERROR in error_msg
        assert "Operation failed" in error_msg
        
        warning_msg = formatter.warning("Warning message")
        assert Icons.WARNING in warning_msg
        assert "Warning message" in warning_msg
    
    def test_auto_color_detection(self):
        """Test automatic color support detection"""
        # Test with TTY
        with patch('sys.stdout.isatty', return_value=True):
            with patch.dict(os.environ, {'TERM': 'xterm-256color'}, clear=False):
                formatter = ColorFormatter()
                assert formatter.use_colors is True
        
        # Test without TTY
        with patch('sys.stdout.isatty', return_value=False):
            formatter = ColorFormatter()
            assert formatter.use_colors is False
        
        # Test with NO_COLOR environment variable
        with patch('sys.stdout.isatty', return_value=True):
            with patch.dict(os.environ, {'NO_COLOR': '1'}, clear=False):
                formatter = ColorFormatter()
                assert formatter.use_colors is False


class TestProgressIndicator:
    """Test progress indicator functionality"""
    
    def test_progress_indicator_basic(self):
        """Test basic progress indicator functionality"""
        with patch('sys.stdout') as mock_stdout:
            indicator = ProgressIndicator("Testing", use_colors=False)
            
            # Test context manager
            with indicator:
                pass
            
            # Verify output was written
            assert mock_stdout.write.called
    
    def test_progress_indicator_with_messages(self):
        """Test progress indicator with success/error messages"""
        with patch('sys.stdout') as mock_stdout:
            indicator = ProgressIndicator("Testing", use_colors=False)
            
            indicator.start()
            indicator.stop(success_message="Completed successfully")
            
            # Check that success message was printed
            print_calls = [call for call in mock_stdout.write.call_args_list]
            assert any("Completed successfully" in str(call) for call in print_calls)


class TestProgressBar:
    """Test progress bar functionality"""
    
    def test_progress_bar_basic(self):
        """Test basic progress bar functionality"""
        with patch('sys.stdout') as mock_stdout:
            progress = ProgressBar(100, "Testing", use_colors=False)
            
            # Test progress updates
            progress.update(25)
            progress.update(25)
            progress.set_progress(75)
            progress.finish()
            
            # Verify output was written
            assert mock_stdout.write.called
    
    def test_progress_bar_percentage_calculation(self):
        """Test progress bar percentage calculations"""
        progress = ProgressBar(100, "Testing", use_colors=False)
        
        # Test normal progress
        progress.set_progress(50)
        assert progress.current == 50
        
        # Test overflow protection
        progress.set_progress(150)
        assert progress.current == 100
        
        # Test underflow protection
        progress.set_progress(-10)
        assert progress.current == 0


class TestTable:
    """Test table formatting"""
    
    def test_table_creation_and_rendering(self):
        """Test table creation and rendering"""
        columns = [
            TableColumn("Name", 15),
            TableColumn("Status", 10),
            TableColumn("Value", 12, align='right')
        ]
        
        table = Table(columns, use_colors=False)
        table.add_row("Test Account", "Active", "1000.00")
        table.add_row("Demo Account", "Inactive", "500.50")
        
        rendered = table.render()
        
        # Check that table contains expected content
        assert "Test Account" in rendered
        assert "Active" in rendered
        assert "1000.00" in rendered
        assert "Demo Account" in rendered
        
        # Check table structure
        assert "│" in rendered  # Table borders
        assert "─" in rendered  # Table separators
    
    def test_table_with_formatters(self):
        """Test table with custom formatters"""
        def currency_formatter(value):
            return f"${float(value):,.2f}"
        
        columns = [
            TableColumn("Account", 15),
            TableColumn("Balance", 12, formatter=currency_formatter)
        ]
        
        table = Table(columns, use_colors=False)
        table.add_row("Test", "1234.56")
        
        rendered = table.render()
        assert "$1,234.56" in rendered
    
    def test_empty_table(self):
        """Test empty table handling"""
        columns = [TableColumn("Name", 10)]
        table = Table(columns, use_colors=False)
        
        rendered = table.render()
        assert "No data to display" in rendered


class TestInteractivePrompt:
    """Test interactive prompt functionality"""
    
    def test_confirm_prompt_yes(self):
        """Test confirmation prompt with yes response"""
        prompt = InteractivePrompt(use_colors=False)
        
        with patch('builtins.input', return_value='y'):
            result = prompt.confirm("Continue?")
            assert result is True
        
        with patch('builtins.input', return_value='yes'):
            result = prompt.confirm("Continue?")
            assert result is True
    
    def test_confirm_prompt_no(self):
        """Test confirmation prompt with no response"""
        prompt = InteractivePrompt(use_colors=False)
        
        with patch('builtins.input', return_value='n'):
            result = prompt.confirm("Continue?")
            assert result is False
        
        with patch('builtins.input', return_value='no'):
            result = prompt.confirm("Continue?")
            assert result is False
    
    def test_confirm_prompt_default(self):
        """Test confirmation prompt with default values"""
        prompt = InteractivePrompt(use_colors=False)
        
        # Test default True
        with patch('builtins.input', return_value=''):
            result = prompt.confirm("Continue?", default=True)
            assert result is True
        
        # Test default False
        with patch('builtins.input', return_value=''):
            result = prompt.confirm("Continue?", default=False)
            assert result is False
    
    def test_select_option(self):
        """Test option selection"""
        prompt = InteractivePrompt(use_colors=False)
        options = ["Option 1", "Option 2", "Option 3"]
        
        with patch('builtins.input', return_value='2'):
            result = prompt.select("Choose option:", options)
            assert result == 1  # Zero-based index
        
        # Test default selection
        with patch('builtins.input', return_value=''):
            result = prompt.select("Choose option:", options, default=2)
            assert result == 2
    
    def test_text_input(self):
        """Test text input functionality"""
        prompt = InteractivePrompt(use_colors=False)
        
        with patch('builtins.input', return_value='test input'):
            result = prompt.input_text("Enter text:")
            assert result == "test input"
        
        # Test with default
        with patch('builtins.input', return_value=''):
            result = prompt.input_text("Enter text:", default="default value")
            assert result == "default value"
    
    def test_text_input_validation(self):
        """Test text input with validation"""
        prompt = InteractivePrompt(use_colors=False)
        
        def email_validator(text):
            return "@" in text
        
        # Test valid input
        with patch('builtins.input', return_value='test@example.com'):
            result = prompt.input_text("Enter email:", validator=email_validator)
            assert result == "test@example.com"
        
        # Test invalid then valid input
        with patch('builtins.input', side_effect=['invalid', 'valid@example.com']):
            result = prompt.input_text("Enter email:", validator=email_validator)
            assert result == "valid@example.com"
    
    def test_password_input(self):
        """Test password input functionality"""
        prompt = InteractivePrompt(use_colors=False)
        
        with patch('getpass.getpass', return_value='secret123'):
            result = prompt.input_password("Enter password:")
            assert result == "secret123"


class TestOutputManager:
    """Test output manager functionality"""
    
    def test_output_manager_modes(self):
        """Test different output modes"""
        # Test normal mode
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            output.info("Test message")
            assert "Test message" in mock_stdout.getvalue()
        
        # Test quiet mode
        output = OutputManager(OutputMode.QUIET, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            output.info("Test message")
            assert mock_stdout.getvalue() == ""  # Should be suppressed
        
        # Test verbose mode
        output = OutputManager(OutputMode.VERBOSE, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            output.verbose("Verbose message")
            assert "Verbose message" in mock_stdout.getvalue()
    
    def test_result_printing(self):
        """Test command result printing"""
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Test success result
            result = CommandResult.success("Operation completed")
            output.print_result(result)
            assert "Operation completed" in mock_stdout.getvalue()
        
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            # Test error result
            result = CommandResult.error("Operation failed")
            output.print_result(result)
            assert "Operation failed" in mock_stderr.getvalue()
    
    def test_suggestions_printing(self):
        """Test suggestions printing"""
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            suggestions = ["Try this", "Or this", "Maybe this"]
            output.print_suggestions(suggestions)
            
            output_text = mock_stdout.getvalue()
            assert "Suggestions:" in output_text
            assert "Try this" in output_text
            assert "Or this" in output_text
    
    def test_table_printing(self):
        """Test table printing through output manager"""
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        data = [
            {"name": "Account 1", "status": "Active", "balance": "1000.00"},
            {"name": "Account 2", "status": "Inactive", "balance": "500.00"}
        ]
        columns = ["name", "status", "balance"]
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            output.print_table(data, columns, title="Test Accounts")
            
            output_text = mock_stdout.getvalue()
            assert "Test Accounts" in output_text
            assert "Account 1" in output_text
            assert "Active" in output_text
    
    def test_dangerous_operation_confirmation(self):
        """Test dangerous operation confirmation"""
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        # Test successful confirmation
        with patch.object(output, '_confirm_dangerous_operation', return_value=True):
            with patch.object(output.prompt, 'confirm', return_value=True):
                result = output.confirm("Delete all data?", dangerous=True)
                assert result is True
        
        # Test failed confirmation
        with patch.object(output, '_confirm_dangerous_operation', return_value=False):
            result = output.confirm("Delete all data?", dangerous=True)
            assert result is False
    
    def test_file_output(self):
        """Test output to file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            output = OutputManager(OutputMode.NORMAL, use_colors=False, output_file=temp_path)
            output.info("Test message")
            
            # Check that message was written to file
            content = temp_path.read_text()
            assert "Test message" in content
        finally:
            temp_path.unlink()


class TestCommandCompletion:
    """Test command completion functionality"""
    
    def test_command_registration(self):
        """Test command registration for completion"""
        completion = CommandCompletion()
        
        completion.register_command(
            'test-command',
            subcommands=['sub1', 'sub2'],
            options=['--option1', '--option2'],
            description='Test command'
        )
        
        assert 'test-command' in completion.commands
        assert completion.commands['test-command']['subcommands'] == ['sub1', 'sub2']
        assert completion.commands['test-command']['options'] == ['--option1', '--option2']
    
    def test_completion_generation(self):
        """Test completion suggestions generation"""
        completion = CommandCompletion()
        completion.register_command('start', subcommands=['bot'], options=['--config'])
        completion.register_command('stop', subcommands=['bot'], options=['--force'])
        
        # Test main command completion
        completions = completion.get_completions('st', 'st', 0, 2)
        assert 'start' in completions
        assert 'stop' in completions
        
        # Test subcommand completion
        completions = completion.get_completions('bot', 'start bot', 6, 9)
        assert 'bot' in completions
    
    def test_bash_completion_script_generation(self):
        """Test bash completion script generation"""
        completion = CommandCompletion()
        completion.register_command('start', options=['--config'])
        completion.register_command('stop', options=['--force'])
        
        script = completion.generate_bash_completion()
        
        assert '#!/bin/bash' in script
        assert '_genebot_completion' in script
        assert 'start stop' in script
        assert 'complete -F _genebot_completion genebot' in script


class TestHelpFormatter:
    """Test help formatting functionality"""
    
    def test_command_help_formatting(self):
        """Test command help formatting"""
        formatter = HelpFormatter(use_colors=False)
        
        options = [
            {
                'flag': '--config',
                'short': '-c',
                'description': 'Configuration file path',
                'default': 'config.yaml'
            }
        ]
        
        examples = [
            {
                'description': 'Start with custom config',
                'command': 'genebot start --config my-config.yaml'
            }
        ]
        
        help_text = formatter.format_command_help(
            command='start',
            description='Start the trading bot',
            usage='genebot start [OPTIONS]',
            options=options,
            examples=examples,
            see_also=['stop', 'status']
        )
        
        assert 'COMMAND: start' in help_text
        assert 'Start the trading bot' in help_text
        assert '--config' in help_text
        assert 'Configuration file path' in help_text
        assert 'genebot start --config my-config.yaml' in help_text
        assert 'stop' in help_text
    
    def test_command_list_formatting(self):
        """Test command list formatting"""
        formatter = HelpFormatter(use_colors=False)
        
        commands = {
            'start': {
                'description': 'Start the trading bot',
                'category': 'Bot Control'
            },
            'stop': {
                'description': 'Stop the trading bot',
                'category': 'Bot Control'
            },
            'list-accounts': {
                'description': 'List all accounts',
                'category': 'Account Management'
            }
        }
        
        formatted = formatter.format_command_list(commands)
        
        assert 'AVAILABLE COMMANDS' in formatted
        assert 'Bot Control:' in formatted
        assert 'Account Management:' in formatted
        assert 'start' in formatted
        assert 'Start the trading bot' in formatted


class TestInteractiveHelp:
    """Test interactive help system"""
    
    def test_interactive_help_initialization(self):
        """Test interactive help system initialization"""
        help_system = InteractiveHelp(use_colors=False)
        
        assert 'getting-started' in help_system.help_topics
        assert 'configuration' in help_system.help_topics
        assert 'troubleshooting' in help_system.help_topics
    
    def test_help_topic_handlers(self):
        """Test help topic handlers exist and are callable"""
        help_system = InteractiveHelp(use_colors=False)
        
        for topic, handler in help_system.help_topics.items():
            assert callable(handler)
            
            # Test that handler can be called without errors
            with patch('sys.stdout', new_callable=io.StringIO):
                try:
                    handler()
                except Exception as e:
                    pytest.fail(f"Help topic '{topic}' handler failed: {e}")


class TestUserAcceptanceScenarios:
    """User acceptance tests for CLI UX improvements"""
    
    def test_progress_indicator_user_experience(self):
        """Test that progress indicators improve user experience"""
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # Simulate a long-running operation with progress indicator
            with ProgressIndicator("Processing accounts", use_colors=False) as progress:
                # Simulate work
                pass
            
            output = mock_stdout.getvalue()
            # Should show some indication of progress
            assert len(output) > 0
    
    def test_colored_output_enhancement(self):
        """Test that colored output enhances readability"""
        formatter = ColorFormatter(use_colors=True)
        
        # Test that different message types have different formatting
        success_msg = formatter.success("Success message")
        error_msg = formatter.error("Error message")
        warning_msg = formatter.warning("Warning message")
        
        # Each should be different when colors are enabled
        assert success_msg != error_msg
        assert error_msg != warning_msg
        assert success_msg != warning_msg
    
    def test_interactive_prompts_safety(self):
        """Test that interactive prompts prevent dangerous operations"""
        output = OutputManager(OutputMode.NORMAL, use_colors=False)
        
        # Test that dangerous operations require special confirmation
        with patch.object(output, '_confirm_dangerous_operation', return_value=False) as mock_confirm:
            result = output.confirm("Delete all data?", dangerous=True)
            assert result is False
            mock_confirm.assert_called_once()
    
    def test_help_system_accessibility(self):
        """Test that help system is accessible and informative"""
        help_system = InteractiveHelp(use_colors=False)
        
        # Test that help topics provide useful information
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            help_system._help_getting_started()
            
            output = mock_stdout.getvalue()
            # Should contain actionable information
            assert "genebot" in output.lower()
            assert len(output) > 100  # Should be substantial
    
    def test_quiet_mode_functionality(self):
        """Test that quiet mode suppresses non-essential output"""
        output = OutputManager(OutputMode.QUIET, use_colors=False)
        
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            # These should be suppressed in quiet mode
            output.info("Info message")
            output.verbose("Verbose message")
            output.debug("Debug message")
            
            assert mock_stdout.getvalue() == ""
        
        with patch('sys.stderr', new_callable=io.StringIO) as mock_stderr:
            # Errors should still be shown
            output.error("Error message")
            assert "Error message" in mock_stderr.getvalue()
    
    def test_verbose_mode_detail(self):
        """Test that verbose mode provides additional detail"""
        normal_output = OutputManager(OutputMode.NORMAL, use_colors=False)
        verbose_output = OutputManager(OutputMode.VERBOSE, use_colors=False)
        
        result = CommandResult.success("Operation completed", data={"details": "extra info"})
        
        with patch('sys.stdout', new_callable=io.StringIO) as normal_stdout:
            normal_output.print_result(result)
            normal_text = normal_stdout.getvalue()
        
        with patch('sys.stdout', new_callable=io.StringIO) as verbose_stdout:
            verbose_output.print_result(result)
            verbose_text = verbose_stdout.getvalue()
        
        # Verbose mode should include more information
        assert len(verbose_text) >= len(normal_text)
    
    def test_command_completion_usability(self):
        """Test that command completion improves usability"""
        completion = CommandCompletion()
        completion.register_command('start', subcommands=['bot'], options=['--config'])
        completion.register_command('status', options=['--detailed'])
        
        # Test that partial commands return relevant completions
        completions = completion.get_completions('sta', 'sta', 0, 3)
        assert 'start' in completions
        assert 'status' in completions
        
        # Test that completions are contextually relevant
        completions = completion.get_completions('--', 'start --', 6, 8)
        assert '--config' in completions
    
    def test_table_formatting_readability(self):
        """Test that table formatting improves data readability"""
        columns = [
            TableColumn("Account Name", 20),
            TableColumn("Status", 10),
            TableColumn("Balance", 15, align='right')
        ]
        
        table = Table(columns, use_colors=False)
        table.add_row("Long Account Name Here", "Active", "1,234.56")
        table.add_row("Short", "Inactive", "0.00")
        
        rendered = table.render()
        
        # Should be properly aligned and formatted
        lines = rendered.split('\n')
        # Should have consistent structure
        assert len(set(len(line) for line in lines if line.strip())) <= 2  # Allow for minor variations
        
        # Should contain proper table structure
        assert any('│' in line for line in lines)  # Vertical borders
        assert any('─' in line for line in lines)  # Horizontal borders


if __name__ == '__main__':
    pytest.main([__file__])