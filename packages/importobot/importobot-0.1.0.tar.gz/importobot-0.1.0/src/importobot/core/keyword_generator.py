"""Implementation of keyword generation components."""

import re
from typing import Any

from importobot.core.context_analyzer import ContextAnalyzer
from importobot.core.keywords.base_generator import BaseKeywordGenerator
from importobot.core.keywords.generators.api_keywords import APIKeywordGenerator
from importobot.core.keywords.generators.builtin_keywords import BuiltInKeywordGenerator
from importobot.core.keywords.generators.database_keywords import (
    DatabaseKeywordGenerator,
)
from importobot.core.keywords.generators.file_keywords import FileKeywordGenerator
from importobot.core.keywords.generators.operating_system_keywords import (
    OperatingSystemKeywordGenerator,
)
from importobot.core.keywords.generators.ssh_keywords import SSHKeywordGenerator
from importobot.core.keywords.generators.web_keywords import WebKeywordGenerator
from importobot.core.keywords_registry import IntentRecognitionEngine
from importobot.core.multi_command_parser import MultiCommandParser
from importobot.core.parsers import GenericTestFileParser
from importobot.core.pattern_matcher import LibraryDetector
from importobot.utils.field_extraction import extract_field
from importobot.utils.pattern_extraction import extract_pattern
from importobot.utils.ssh_patterns import (
    SSH_FILE_PATH_INDICATORS,
    SSH_STRONG_INDICATORS,
)
from importobot.utils.step_processing import (
    extract_step_information,
)


class GenericKeywordGenerator(BaseKeywordGenerator):
    """Generic keyword generator for Robot Framework conversion."""

    def __init__(self) -> None:
        """Initialize the generator with specialized generators."""
        super().__init__()  # Initialize the base class
        self.web_generator = WebKeywordGenerator()
        self.database_generator = DatabaseKeywordGenerator()
        self.api_generator = APIKeywordGenerator()
        self.file_generator = FileKeywordGenerator()
        self.ssh_generator = SSHKeywordGenerator()
        self.operating_system_generator = OperatingSystemKeywordGenerator()
        self.builtin_generator = BuiltInKeywordGenerator()
        self.multi_command_parser = MultiCommandParser()
        self.context_analyzer = ContextAnalyzer()

    def generate_step_keywords(self, step: dict[str, Any]) -> list[str]:
        """Generate Robot Framework keywords for a step."""
        lines = []

        description, test_data, expected = extract_step_information(step)

        # Add traceability comments in the correct order
        indent = "    "
        if description:
            lines.append(f"{indent}# Step: {description}")
        if test_data:
            lines.append(f"{indent}# Test Data: {test_data}")

        # Add security warnings if sensitive data is detected (before Expected Result)
        if test_data:
            security_warnings = self._generate_security_warnings(test_data)
            lines.extend(security_warnings)

        if expected:
            lines.append(f"{indent}# Expected Result: {expected}")

        # Check if test_data contains multiple fields that should generate multiple
        # commands
        parsed_data = self.multi_command_parser.parse_test_data(test_data)
        if len(
            parsed_data
        ) > 1 and self.multi_command_parser.should_generate_multiple_commands(
            description, parsed_data
        ):
            # Generate multiple Robot Framework commands
            keyword_lines = self.multi_command_parser.generate_multiple_robot_keywords(
                description, parsed_data, expected
            )
            lines.extend([f"    {line}" for line in keyword_lines])
        else:
            # Generate single Robot keyword (existing behavior)
            keyword_line = self._determine_robot_keyword(
                description, test_data, expected
            )
            lines.append(f"    {keyword_line}")

        return lines

    def detect_libraries(self, steps: list[dict[str, Any]]) -> set[str]:
        """Detect required Robot Framework libraries from step content."""
        return LibraryDetector.detect_libraries_from_steps(steps)

    def _get_parser(self) -> GenericTestFileParser:
        """Get parser instance."""
        return GenericTestFileParser()

    def _extract_field(self, data: dict[str, Any], field_names: list[str]) -> str:
        """Extract value from first matching field name."""
        return extract_field(data, field_names)

    def _determine_robot_keyword(
        self, description: str, test_data: str, expected: str
    ) -> str:
        """Determine Robot Framework keyword based on step content."""
        combined = f"{description} {test_data}".lower()
        intent = IntentRecognitionEngine.recognize_intent(combined)

        # Check for ambiguous cases and provide suggestions
        ambiguous_keywords = self._detect_ambiguous_cases(
            description, test_data, expected
        )
        if ambiguous_keywords:
            return self._format_suggestions(ambiguous_keywords)

        # Delegate to specialized generators based on intent
        intent_handlers = {
            # Web operations
            "web_navigation": lambda: self.web_generator.generate_browser_keyword(
                test_data
            ),
            "browser_open": lambda: self.web_generator.generate_browser_keyword(
                test_data
            ),
            "browser_navigate": lambda: self.web_generator.generate_navigation_keyword(
                test_data
            ),
            "web_input_username": lambda: self.web_generator.generate_input_keyword(
                "username", test_data
            ),
            "input_username": lambda: self.web_generator.generate_input_keyword(
                "username", test_data
            ),
            "web_input_password": lambda: self.web_generator.generate_password_keyword(
                test_data
            ),
            "input_password": lambda: self.web_generator.generate_password_keyword(
                test_data
            ),
            "web_click": lambda: self.web_generator.generate_click_keyword(
                description, test_data
            ),
            "click": lambda: self.web_generator.generate_click_keyword(
                description, test_data
            ),
            "web_verify_text": lambda: (
                self.web_generator.generate_page_verification_keyword(
                    test_data, expected
                )
            ),
            # Page assertions (SeleniumLibrary)
            "page_assertion_contains": lambda: (
                self.web_generator.generate_page_verification_keyword(
                    test_data, expected
                )
            ),
            # Database operations
            "db_connect": lambda: self.database_generator.generate_connect_keyword(
                test_data
            ),
            "db_execute": lambda: self.database_generator.generate_query_keyword(
                test_data
            ),
            "db_disconnect": lambda: "Disconnect From Database",
            "db_modify": lambda: self.database_generator.generate_modify_keyword(
                test_data
            ),
            "db_row_count": lambda: self.database_generator.generate_row_count_keyword(
                test_data
            ),
            # API operations
            "api_request": lambda: self.api_generator.generate_request_keyword(
                test_data
            ),
            "api_session": lambda: self.api_generator.generate_session_keyword(
                test_data
            ),
            "api_response": lambda: self.api_generator.generate_response_keyword(
                test_data
            ),
            # File operations (check for SSH context first)
            "file_exists": lambda: self._handle_file_verification(
                description, test_data
            ),
            "file_remove": lambda: self._handle_file_removal(description, test_data),
            "file_verification": lambda: self._handle_file_verification(
                description, test_data
            ),
            "file_removal": lambda: self._handle_file_removal(description, test_data),
            "file_transfer": lambda: self._handle_file_transfer(description, test_data),
            "file_creation": lambda: self._handle_file_creation(description, test_data),
            "file_operation": lambda: self._handle_file_operation(
                description, test_data
            ),
            # SSH operations
            "ssh_connect": lambda: self.ssh_generator.generate_connect_keyword(
                test_data
            ),
            "ssh_login": lambda: self._handle_ssh_authentication(
                description, test_data
            ),
            "ssh_authenticate": lambda: self._handle_ssh_authentication(
                description, test_data
            ),
            "ssh_configuration": lambda: self._handle_ssh_configuration(
                description, test_data
            ),
            "ssh_logging": lambda: self._handle_ssh_logging(description, test_data),
            "ssh_disconnect": lambda: self._handle_ssh_disconnect(
                description, test_data
            ),
            "ssh_execute": lambda: self._handle_ssh_command_execution(
                description, test_data
            ),
            "ssh_file_upload": lambda: (
                self.ssh_generator.generate_file_transfer_keyword(test_data, "upload")
            ),
            "ssh_file_download": lambda: (
                self.ssh_generator.generate_file_transfer_keyword(test_data, "download")
            ),
            "ssh_read_until": lambda: (
                self.ssh_generator.generate_interactive_shell_keyword(
                    test_data, "read_until"
                )
            ),
            "ssh_write": lambda: (
                self.ssh_generator.generate_interactive_shell_keyword(
                    test_data, "write"
                )
            ),
            "ssh_directory_create": lambda: (
                self.ssh_generator.generate_directory_operations_keyword(
                    test_data, "create"
                )
            ),
            "ssh_directory_list": lambda: (
                self.ssh_generator.generate_directory_operations_keyword(
                    test_data, "list"
                )
            ),
            "ssh_switch_connection": lambda: (
                "Switch Connection    ${connection_alias}"
            ),
            "ssh_enable_logging": lambda: (self._handle_ssh_enable_logging(test_data)),
            # Command execution
            "command": lambda: (
                self.operating_system_generator.generate_command_keyword(test_data)
            ),
            # Verification operations
            "assertion_contains": lambda: (
                self.builtin_generator.generate_assert_contains_keyword(
                    test_data, expected
                )
            ),
            "element_verification": lambda: (
                self.builtin_generator.generate_verification_keyword(
                    description, test_data, expected
                )
            ),
            "content_verification": lambda: (
                self.builtin_generator.generate_verification_keyword(
                    description, test_data, expected
                )
            ),
            "content_comparison": lambda: (
                self.builtin_generator.generate_comparison_keyword(
                    description, test_data
                )
            ),
            # BuiltIn keywords
            "convert_to_integer": lambda: (
                self.builtin_generator.generate_convert_to_integer_keyword(test_data)
            ),
            "convert_to_string": lambda: (
                self.builtin_generator.generate_convert_to_string_keyword(test_data)
            ),
            "convert_to_boolean": lambda: (
                self.builtin_generator.generate_convert_to_boolean_keyword(test_data)
            ),
            "convert_to_number": lambda: (
                self.builtin_generator.generate_convert_to_number_keyword(test_data)
            ),
            "log_message": lambda: (
                self.builtin_generator.generate_log_keyword(test_data)
            ),
            "set_variable": lambda: (
                self.builtin_generator.generate_set_variable_keyword(test_data)
            ),
            "get_variable": lambda: (
                self.builtin_generator.generate_get_variable_keyword(test_data)
            ),
            "create_list": lambda: self.builtin_generator.generate_create_list_keyword(
                test_data
            ),
            "create_dictionary": lambda: (
                self.builtin_generator.generate_create_dictionary_keyword(test_data)
            ),
            "get_length": lambda: (
                self.builtin_generator.generate_get_length_keyword(test_data)
            ),
            "length_should_be": lambda: (
                self.builtin_generator.generate_length_should_be_keyword(
                    test_data, expected
                )
            ),
            "should_start_with": lambda: (
                self.builtin_generator.generate_should_start_with_keyword(
                    test_data, expected
                )
            ),
            "should_end_with": lambda: (
                self.builtin_generator.generate_should_end_with_keyword(
                    test_data, expected
                )
            ),
            "should_match": lambda: (
                self.builtin_generator.generate_should_match_keyword(
                    test_data, expected
                )
            ),
            "evaluate_expression": lambda: (
                self.builtin_generator.generate_evaluate_keyword(test_data)
            ),
            "run_keyword_if": lambda: (
                self.builtin_generator.generate_run_keyword_if_keyword(test_data)
            ),
            "repeat_keyword": lambda: (
                self.builtin_generator.generate_repeat_keyword_keyword(test_data)
            ),
            "fail_test": lambda: (
                self.builtin_generator.generate_fail_keyword(test_data)
            ),
            "get_count": lambda: self.builtin_generator.generate_get_count_keyword(
                test_data, expected
            ),
        }

        # Execute handler if intent is recognized
        if intent in intent_handlers:
            return intent_handlers[intent]()

        # Check if this is SSH context but unrecognized operation
        if self._is_ssh_context(description, test_data):
            return "No Operation  # SSH operation not recognized"

        return "No Operation"

    def _is_ssh_context(self, description: str, test_data: str) -> bool:
        """Check if the operation is in SSH context."""
        combined = f"{description} {test_data}".lower()
        # Combine shared SSH patterns with additional local indicators
        additional_indicators = [
            "remote",
            "server",
            "connection",
            "host:",
            "username:",
            "password:",
            "file transfer",
        ]
        ssh_indicators = (
            SSH_STRONG_INDICATORS + additional_indicators + SSH_FILE_PATH_INDICATORS
        )
        return any(indicator in combined for indicator in ssh_indicators)

    def _handle_file_transfer(self, description: str, test_data: str) -> str:
        """Handle file transfer operations, routing to SSH or local file operations."""
        if self._is_ssh_context(description, test_data):
            # Determine if it's upload or download
            if any(word in description.lower() for word in ["upload", "put", "send"]):
                return self.ssh_generator.generate_file_transfer_keyword(
                    test_data, "upload"
                )
            if any(
                word in description.lower()
                for word in ["download", "get", "receive", "retrieve"]
            ):
                return self.ssh_generator.generate_file_transfer_keyword(
                    test_data, "download"
                )
            # Default to upload for SSH file transfers
            return self.ssh_generator.generate_file_transfer_keyword(
                test_data, "upload"
            )
        return self.file_generator.generate_transfer_keyword(test_data)

    def _handle_file_verification(self, description: str, test_data: str) -> str:
        """Handle file verification operations."""
        if self._is_ssh_context(description, test_data):
            return self.ssh_generator.generate_file_verification_keyword(test_data)
        # Un-escape double backslashes for proper file path handling
        processed_data = test_data.replace("\\\\", "\\")
        return self.file_generator.generate_exists_keyword(processed_data)

    def _handle_file_removal(self, description: str, test_data: str) -> str:
        """Handle file removal operations."""
        if self._is_ssh_context(description, test_data):
            file_path = extract_pattern(test_data, r"(?:file|path):\s*([^,\s]+)")
            if file_path:
                return f"Remove File    {file_path}"
            return "Remove File    ${file_path}"
        return self.file_generator.generate_remove_keyword(test_data)

    def _handle_file_creation(self, description: str, test_data: str) -> str:
        """Handle file creation operations."""
        if self._is_ssh_context(description, test_data):
            file_path = extract_pattern(test_data, r"(?:file|path):\s*([^,\s]+)")
            content = extract_pattern(test_data, r"(?:content|data):\s*(.+)")
            if file_path:
                if content:
                    return f"Create File    {file_path}    {content}"
                return f"Create File    {file_path}"
            return "Create File    ${file_path}    ${content}"
        return self.file_generator.generate_create_keyword(description, test_data)

    def _handle_file_operation(self, description: str, test_data: str) -> str:
        """Handle general file operations."""
        if self._is_ssh_context(description, test_data):
            # Use SSH generators for general operations
            combined = f"{description} {test_data}".lower()
            if "directory" in combined:
                if "create" in combined:
                    return self.ssh_generator.generate_directory_operations_keyword(
                        test_data, "create"
                    )
                if "list" in combined:
                    return self.ssh_generator.generate_directory_operations_keyword(
                        test_data, "list"
                    )
                return self.ssh_generator.generate_directory_operations_keyword(
                    test_data, "list"
                )
            return "No Operation"
        return self.file_generator.generate_operation_keyword(description, test_data)

    def _handle_ssh_enable_logging(self, test_data: str) -> str:
        """Handle SSH logging operations."""
        logfile = extract_pattern(test_data, r"(?:logfile|log):\s*([^,\s]+)")
        if logfile:
            return f"Enable Ssh Logging    {logfile}"
        return "Enable Ssh Logging    ${logfile}"

    def _handle_ssh_authentication(self, description: str, test_data: str) -> str:
        """Handle SSH authentication operations."""
        combined = f"{description} {test_data}".lower()

        if "key" in combined or "public" in combined or "private" in combined:
            # SSH key-based authentication
            username = extract_pattern(test_data, r"username:\s*([^,\s]+)")
            keyfile = extract_pattern(test_data, r"(?:keyfile|key):\s*([^,\s]+)")

            if username and keyfile:
                return f"Login With Public Key    {username}    {keyfile}"
            if username:
                return f"Login With Public Key    {username}    ${{keyfile}}"
            return "Login With Public Key    ${username}    ${keyfile}"
        # Regular username/password authentication
        username = extract_pattern(test_data, r"username:\s*([^,\s]+)")
        password = extract_pattern(test_data, r"password:\s*([^,\s]+)")

        if username and password:
            return f"Login    {username}    {password}"
        if username:
            return f"Login    {username}    ${{password}}"
        return "Login    ${username}    ${password}"

    def _handle_ssh_disconnect(self, description: str, test_data: str) -> str:
        """Handle SSH disconnect operations."""
        combined = f"{description} {test_data}".lower()

        if "close all" in combined or ("close" in combined and "all" in combined):
            return "Close All Connections"
        return "Close Connection"

    def _handle_ssh_command_execution(self, description: str, test_data: str) -> str:
        """Handle SSH command execution operations."""
        combined = f"{description} {test_data}".lower()

        if "start" in combined and (
            "command" in combined or "background" in combined or "process" in combined
        ):
            command = extract_pattern(test_data, r"(?:command|cmd):\s*(.+)")
            if command:
                return f"Start Command    {command}"
            return "Start Command    ${command}"
        if "read" in combined and "output" in combined:
            return "Read Command Output"
        return self.ssh_generator.generate_execute_keyword(test_data)

    def analyze_step_context(self, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Analyze context across multiple steps for intelligent suggestions."""
        return self.context_analyzer.analyze_step_context(steps)

    def _handle_ssh_configuration(self, description: str, test_data: str) -> str:
        """Handle SSH configuration operations."""
        combined = f"{description} {test_data}".lower()

        if "client" in combined:
            return self.ssh_generator.generate_configuration_keyword(
                test_data, "client"
            )
        if "default" in combined:
            return self.ssh_generator.generate_configuration_keyword(
                test_data, "default"
            )
        return self.ssh_generator.generate_configuration_keyword(test_data, "client")

    def _handle_ssh_logging(self, description: str, test_data: str) -> str:
        """Handle SSH logging operations."""
        combined = f"{description} {test_data}".lower()

        if "enable" in combined or "start" in combined:
            return self.ssh_generator.generate_logging_keyword(test_data, "enable")
        if "disable" in combined or "stop" in combined:
            return self.ssh_generator.generate_logging_keyword(test_data, "disable")
        return self.ssh_generator.generate_logging_keyword(test_data, "enable")

    def _detect_ambiguous_cases(
        self, description: str, test_data: str, expected: str
    ) -> list[str]:
        """Detect cases where multiple keywords could be appropriate.

        Analyze the provided description and test data to identify cases where
        multiple Robot Framework keywords could be appropriate and return suggestions.
        """
        # expected parameter is kept for interface consistency
        # but not used in this implementation
        _ = expected  # Mark as intentionally unused
        ambiguous_suggestions = []
        combined = f"{description} {test_data}".lower()

        # Define ambiguous patterns and their potential keywords
        ambiguous_patterns = {
            # Cases where both logging and verification could apply
            r"\b(?:log|record).*(?:and|then|&).*(?:verify|check|assert)": [
                "Log    ${message}",
                "Should Contain    ${container}    ${item}",
            ],
            r"\bverify.*(?:and|then|&).*(?:log|record)": [
                "Should Contain    ${container}    ${item}",
                "Log    ${message}",
            ],
            # Cases where conversion and validation could apply
            r"\b(?:convert|transform).*(?:and|then|&).*(?:validate|verify|check)": [
                "Convert To Integer    ${value}",
                "Should Be Equal    ${actual}    ${expected}",
            ],
            r"\bvalidate.*(?:and|then|&).*(?:convert|transform)": [
                "Should Be Equal    ${actual}    ${expected}",
                "Convert To Integer    ${value}",
            ],
            # Cases where length operations could be either get or assert
            r"\b(?:check|verify|get).*length": [
                "Get Length    ${container}",
                "Length Should Be    ${container}    ${expected_length}",
            ],
            # Cases involving counts that could be get or assert operations
            r"\b(?:count|get.*count).*(?:items|elements)": [
                "Get Count    ${container}    ${item}",
                "Should Contain X Times    ${container}    ${item}    ${count}",
            ],
        }

        for pattern, suggestions in ambiguous_patterns.items():
            if re.search(pattern, combined):
                ambiguous_suggestions.extend(suggestions)

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in ambiguous_suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        return unique_suggestions

    def _format_suggestions(self, suggestions: list[str]) -> str:
        """Format multiple keyword suggestions with comments."""
        if not suggestions:
            return "No Operation"

        if len(suggestions) == 1:
            return suggestions[0]

        # Return the first suggestion with a comment about alternatives
        primary = suggestions[0]
        alternatives = ", ".join(suggestions[1:])
        return f"{primary}    # Alternative keywords: {alternatives}"

    def _format_wrapped_comment(
        self, label: str, content: str, max_length: int = 80
    ) -> list[str]:
        """Format long comments with line wrapping to match expected test patterns."""
        if not content:
            return []

        prefix = f"    # {label}: "
        continuation_prefix = "    # Test Data (cont.): "

        # If content is short enough, return single line
        if len(prefix + content) <= max_length:
            return [f"{prefix}{content}"]

        # Handle specific patterns first
        result = self._handle_specific_patterns(content, prefix, continuation_prefix)
        if result:
            return result

        # Handle password content with special care
        result = self._handle_password_content(
            content, prefix, continuation_prefix, max_length
        )
        if result:
            return result

        # Fallback to generic wrapping
        return self._generic_wrapping(content, prefix, continuation_prefix, max_length)

    def _handle_specific_patterns(
        self, content: str, prefix: str, continuation_prefix: str
    ) -> list[str] | None:
        """Handle specific test patterns with predefined splitting rules."""
        lines = []

        # Handle SSH connection pattern
        if (
            "Remote Host:" in content
            and "Username:" in content
            and "Password:" in content
        ):
            if content.count(",") >= 2:
                first_comma = content.find(",")
                first_comma_iter = first_comma + 1
                second_comma = content.find(",", first_comma_iter)
                if second_comma != -1:
                    second_comma_iter = second_comma + 1
                    first_part = content[:second_comma_iter].rstrip()
                    remaining_part = content[second_comma_iter:].lstrip()
                    lines.append(f"{prefix}{first_part}")
                    lines.append(f"{continuation_prefix}{remaining_part}")
                    return lines

        # Handle file transfer pattern
        elif "Remote File Path:" in content and "Local Destination Path:" in content:
            comma_pos = content.find(",")
            if comma_pos != -1:
                comma_pos_iter = comma_pos + 1
                first_part = content[:comma_pos_iter].rstrip()
                remaining_part = content[comma_pos_iter:].lstrip()
                lines.append(f"{prefix}{first_part}")
                lines.append(f"{continuation_prefix}{remaining_part}")
                return lines

        return None

    def _handle_password_content(
        self, content: str, prefix: str, continuation_prefix: str, max_length: int
    ) -> list[str] | None:
        """Handle content containing passwords with conservative wrapping."""
        if "password:" not in content.lower():
            return None

        lines = []

        # Only wrap if the line is extremely long
        if len(prefix + content) <= 100:
            return None

        # Find a safe split point that doesn't break password field
        comma_positions = [i for i, c in enumerate(content) if c == ","]
        for comma_pos in comma_positions:
            comma_pos_iter = comma_pos + 1
            if comma_pos_iter <= max_length - len(prefix):
                # Check if this split would break password field
                before_comma = content[:comma_pos_iter]
                after_comma = content[comma_pos_iter:].strip()
                if "password:" not in after_comma.lower():
                    first_part = before_comma.rstrip()
                    remaining_part = after_comma
                    lines.append(f"{prefix}{first_part}")
                    lines.append(f"{continuation_prefix}{remaining_part}")
                    return lines

        # If we can't find a safe split, use single line even if long
        lines.append(f"{prefix}{content}")
        return lines

    def _generic_wrapping(
        self, content: str, prefix: str, continuation_prefix: str, max_length: int
    ) -> list[str]:
        """Wrap lines generically for content without special patterns."""
        lines = []
        remaining_content = content
        first_line_space = max_length - len(prefix)

        if first_line_space > 20:
            # Find last comma that fits
            comma_positions = [i for i, c in enumerate(remaining_content) if c == ","]
            split_pos = first_line_space

            for comma_pos in reversed(comma_positions):
                if comma_pos + 1 <= first_line_space:
                    split_pos = comma_pos + 1
                    break

            if split_pos < len(remaining_content):
                first_part = remaining_content[:split_pos].rstrip()
                remaining_content = remaining_content[split_pos:].lstrip()
                lines.append(f"{prefix}{first_part}")
            else:
                lines.append(f"{prefix}{remaining_content}")
                remaining_content = ""

        # Continuation lines
        while remaining_content:
            cont_space = max_length - len(continuation_prefix)
            if len(remaining_content) <= cont_space:
                lines.append(f"{continuation_prefix}{remaining_content}")
                break

            # Find split point
            split_pos = self._find_split_point(remaining_content, cont_space)

            if split_pos < len(remaining_content):
                part = remaining_content[:split_pos].rstrip()
                remaining_content = remaining_content[split_pos:].lstrip()
                lines.append(f"{continuation_prefix}{part}")
            else:
                lines.append(f"{continuation_prefix}{remaining_content}")
                break

        return lines

    def _find_split_point(self, content: str, cont_space: int) -> int:
        """Find the best split point for continuation lines."""
        split_pos = cont_space
        for i in range(min(cont_space, len(content)), max(0, cont_space - 20), -1):
            i_iter = i + 1
            if i < len(content) and content[i:i_iter] == ",":
                split_pos = i + 1
                break
        return split_pos

    def _generate_security_warnings(self, test_data: str) -> list[str]:
        """Generate security warnings for sensitive data in test data."""
        warnings: list[str] = []

        if not test_data:
            return warnings

        test_data = test_data.lower()

        # Check for password usage
        if re.search(r"\bpassword\s*:\s*\S+", test_data, re.IGNORECASE):
            warnings.append(
                "    # ⚠️  Security Warning: Hardcoded password detected in test data"
            )

        # Check for other sensitive patterns
        if re.search(
            r"\b(?:api[_\s]*key|secret|token)\s*:\s*\S+", test_data, re.IGNORECASE
        ):
            warnings.append(
                "    # ⚠️  Security Warning: Sensitive credential detected in test data"
            )

        # Check for private key files
        if re.search(r"\.pem|\.key|id_rsa|id_dsa", test_data, re.IGNORECASE):
            warnings.append(
                "    # ⚠️  Security Warning: Private key file reference detected"
            )

        return warnings
