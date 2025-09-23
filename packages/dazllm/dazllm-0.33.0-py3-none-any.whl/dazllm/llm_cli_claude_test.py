"""
Comprehensive tests for Claude CLI structured output with result.json separation

Tests various schemas and ensures proper separation of output logs from results.
"""

import pytest
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .llm_cli_claude import LlmClaudeCliWithLogging as LlmClaudeCli
from .llm_claude_cli import LlmClaudeCli as OriginalLlmClaudeCli


# Define test schemas

class SimpleSchema(BaseModel):
    """Simple schema with basic types"""
    name: str
    age: int
    is_active: bool


class FileListSchema(BaseModel):
    """Schema for file listing task"""
    total_files: int = Field(description="Total number of files found")
    directories: List[str] = Field(description="List of directory names")
    files: List[str] = Field(description="List of file names")
    most_common_extensions: Dict[str, int] = Field(description="Extension counts")


class AnalysisResultSchema(BaseModel):
    """Schema for code analysis result"""
    file_count: int = Field(description="Number of Python files")
    total_lines: int = Field(description="Total lines of code")
    function_count: int = Field(description="Number of functions")
    class_count: int = Field(description="Number of classes")
    summary: str = Field(description="Brief summary of findings")


class ComplexNestedSchema(BaseModel):
    """Complex schema with nested structures"""

    class PersonInfo(BaseModel):
        name: str
        age: int
        email: Optional[str] = None

    class ProjectInfo(BaseModel):
        name: str
        language: str
        stars: int
        contributors: List[str]

    user: PersonInfo
    projects: List[ProjectInfo]
    total_contributions: int
    active_since: str


class TaskExecutionSchema(BaseModel):
    """Schema for task execution with file creation"""
    task_name: str = Field(description="Name of the executed task")
    files_created: List[str] = Field(description="List of files created")
    success: bool = Field(description="Whether task succeeded")
    output_summary: str = Field(description="Summary of what was done")
    metrics: Dict[str, int] = Field(description="Numeric metrics from the task")


@pytest.mark.skipif(
    not LlmClaudeCli.is_available(),
    reason="Claude CLI not available"
)
class TestClaudeCliStructured:
    """Test Claude CLI structured output with real calls"""

    def test_simple_schema(self):
        """Test with a simple schema"""
        cli = LlmClaudeCli()

        conversation = [
            {
                "role": "user",
                "content": "Create a person named John who is 30 years old and active."
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Verify result
        assert result.value.name == "John"
        assert result.value.age == 30
        assert result.value.is_active is True

        # Verify logs are present
        assert "Claude CLI Structured Output" in result.output
        assert "Schema: SimpleSchema" in result.output
        assert "Validation: PASSED" in result.output

    def test_file_listing_task(self):
        """Test with actual file system task"""
        cli = LlmClaudeCli()

        # Get current directory for the task
        current_dir = os.path.dirname(os.path.abspath(__file__))

        conversation = [
            {
                "role": "user",
                "content": f"""List all files and directories in {current_dir}.
                Count the total files, list directory names and file names separately,
                and count the most common file extensions."""
            }
        ]

        result = cli.chat_structured(conversation, FileListSchema)

        # Verify result structure
        assert isinstance(result.value.total_files, int)
        assert result.value.total_files > 0
        assert isinstance(result.value.directories, list)
        assert isinstance(result.value.files, list)
        assert isinstance(result.value.most_common_extensions, dict)
        assert ".py" in result.value.most_common_extensions

        # Verify separation of logs and result
        assert "Schema file:" in result.output
        assert "Result file:" in result.output
        assert "Console Output" in result.output

    def test_code_analysis_task(self):
        """Test analyzing Python files in directory"""
        cli = LlmClaudeCli()

        current_dir = os.path.dirname(os.path.abspath(__file__))

        conversation = [
            {
                "role": "user",
                "content": f"""Analyze the Python files in {current_dir}.
                Count the number of .py files, estimate total lines of code,
                count functions and classes, and provide a brief summary."""
            }
        ]

        result = cli.chat_structured(conversation, AnalysisResultSchema)

        # Verify result
        assert result.value.file_count > 0
        assert result.value.total_lines > 0
        assert isinstance(result.value.summary, str)
        assert len(result.value.summary) > 10

        # Check logs
        assert "Validation: PASSED" in result.output

    def test_complex_nested_schema(self):
        """Test with complex nested schema"""
        cli = LlmClaudeCli()

        conversation = [
            {
                "role": "user",
                "content": """Create a developer profile for Alice Smith, age 28,
                email alice@example.com. She has 2 projects:
                1. "WebApp" in Python with 150 stars and contributors ["Bob", "Charlie"]
                2. "DataTool" in Go with 75 stars and contributors ["David"]
                She has made 523 total contributions and has been active since 2019."""
            }
        ]

        result = cli.chat_structured(conversation, ComplexNestedSchema)

        # Verify nested structures
        assert result.value.user.name == "Alice Smith"
        assert result.value.user.age == 28
        assert result.value.user.email == "alice@example.com"

        assert len(result.value.projects) == 2
        assert result.value.projects[0].name == "WebApp"
        assert result.value.projects[0].language == "Python"
        assert result.value.projects[0].stars == 150
        assert "Bob" in result.value.projects[0].contributors

        assert result.value.total_contributions == 523
        assert "2019" in result.value.active_since

    def test_task_with_file_creation(self):
        """Test task that creates files and returns structured result"""
        cli = LlmClaudeCli()

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_file = os.path.join(tmpdir, "file_summary.txt")

            conversation = [
                {
                    "role": "user",
                    "content": f"""Execute the following task:
                    1. Create a file at {summary_file} containing a list of all Python files in the current directory
                    2. Count how many lines are in each Python file
                    3. Return the results in the required schema format

                    Task name should be "Python File Summary"
                    List the files you created
                    Indicate success
                    Provide a summary of what you did
                    Include metrics for: total_files, total_lines, avg_lines_per_file"""
                }
            ]

            result = cli.chat_structured(conversation, TaskExecutionSchema)

            # Verify result
            assert result.value.task_name == "Python File Summary"
            assert result.value.success is True
            assert summary_file in result.value.files_created or "file_summary.txt" in str(result.value.files_created)
            assert len(result.value.output_summary) > 20
            assert "total_files" in result.value.metrics
            assert result.value.metrics["total_files"] > 0

            # Verify file was actually created
            assert os.path.exists(summary_file)

    def test_schema_validation_retry(self):
        """Test that schema validation retry works"""
        cli = LlmClaudeCli()

        # Use a prompt that might initially produce wrong format
        conversation = [
            {
                "role": "user",
                "content": """First, explain what you're doing, then create data for:
                name: "Test User", age: twenty-five (as a number), is_active: yes (as boolean)"""
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Should eventually succeed with correct types
        assert result.value.name == "Test User"
        assert result.value.age == 25
        assert result.value.is_active is True

        # Check that file paths were used
        assert "Schema file:" in result.output
        assert ".schema.json" in result.output
        assert ".result.json" in result.output

    def test_multiple_calls_cleanup(self):
        """Test that temporary files are cleaned up properly"""
        cli = LlmClaudeCli()

        # Track temp files mentioned in logs
        temp_files = []

        for i in range(3):
            conversation = [
                {
                    "role": "user",
                    "content": f"Create person number {i+1}, age {20+i}, active: true"
                }
            ]

            result = cli.chat_structured(conversation, SimpleSchema)

            # Extract file paths from output
            for line in result.output.split('\n'):
                if "Schema file:" in line or "Result file:" in line:
                    path = line.split(": ")[1].strip()
                    temp_files.append(path)

        # Verify no temp files remain
        for path in temp_files:
            assert not os.path.exists(path), f"Temp file not cleaned: {path}"


@pytest.mark.skipif(
    not OriginalLlmClaudeCli.check_config if hasattr(OriginalLlmClaudeCli, 'check_config') else True,
    reason="Claude CLI not configured"
)
class TestClaudeCliEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_response_handling(self):
        """Test handling of empty or invalid responses"""
        cli = LlmClaudeCli()

        # This should trigger fallback to console extraction
        conversation = [
            {
                "role": "user",
                "content": "Return an empty object: {}"
            }
        ]

        # Should handle empty object
        with pytest.raises(Exception) as exc_info:
            cli.chat_structured(conversation, SimpleSchema)

        # Should have tried and logged the attempt
        assert "Validation" in str(exc_info.value) or "required" in str(exc_info.value)

    def test_large_schema(self):
        """Test with large complex schema"""

        class LargeSchema(BaseModel):
            items: List[Dict[str, str]] = Field(description="List of items with string keys and values")
            metadata: Dict[str, List[int]] = Field(description="Metadata with lists of integers")

        cli = LlmClaudeCli()

        conversation = [
            {
                "role": "user",
                "content": """Create data with:
                - 3 items, each with keys "id", "name", "type"
                - metadata with keys "scores" containing [1,2,3] and "ratings" containing [4,5]"""
            }
        ]

        result = cli.chat_structured(conversation, LargeSchema)

        assert len(result.value.items) == 3
        assert all("id" in item for item in result.value.items)
        assert result.value.metadata["scores"] == [1, 2, 3]
        assert result.value.metadata["ratings"] == [4, 5]
