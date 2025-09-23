"""
Comprehensive tests for Codex CLI structured output with result.json separation

Tests various schemas and ensures proper separation of output logs from results.
"""

import pytest
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .llm_cli_codex import LlmCodexCli
from .llm_codex_cli import LlmCodexCli as OriginalLlmCodexCli


# Define test schemas (same as Claude tests for consistency)

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
    not LlmCodexCli.is_available(),
    reason="Codex CLI not available"
)
class TestCodexCliStructured:
    """Test Codex CLI structured output with real calls"""

    def test_simple_schema(self):
        """Test with a simple schema"""
        cli = LlmCodexCli()

        conversation = [
            {
                "role": "user",
                "content": "Create a person named Alice who is 25 years old and active."
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Verify result
        assert result.value.name == "Alice"
        assert result.value.age == 25
        assert result.value.is_active is True

        # Verify logs are present
        assert "Codex CLI Structured Output" in result.output
        assert "Schema: SimpleSchema" in result.output
        assert "Validation: PASSED" in result.output

    def test_file_listing_task(self):
        """Test with actual file system task"""
        cli = LlmCodexCli()

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
        assert "Console Output" in result.output
        assert "Processing Response" in result.output

    def test_code_analysis_task(self):
        """Test analyzing Python files in directory"""
        cli = LlmCodexCli()

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
        cli = LlmCodexCli()

        conversation = [
            {
                "role": "user",
                "content": """Create a developer profile for Bob Johnson, age 32,
                email bob@example.com. He has 2 projects:
                1. "APIServer" in Go with 200 stars and contributors ["Alice", "Charlie"]
                2. "MLPipeline" in Python with 150 stars and contributors ["David", "Eve"]
                He has made 1024 total contributions and has been active since 2018."""
            }
        ]

        result = cli.chat_structured(conversation, ComplexNestedSchema)

        # Verify nested structures
        assert result.value.user.name == "Bob Johnson"
        assert result.value.user.age == 32
        assert result.value.user.email == "bob@example.com"

        assert len(result.value.projects) == 2
        assert result.value.projects[0].name == "APIServer"
        assert result.value.projects[0].language == "Go"
        assert result.value.projects[0].stars == 200
        assert "Alice" in result.value.projects[0].contributors

        assert result.value.total_contributions == 1024
        assert "2018" in result.value.active_since

    def test_task_with_file_creation(self):
        """Test task that creates files and returns structured result"""
        cli = LlmCodexCli()

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_file = os.path.join(tmpdir, "codex_summary.txt")

            conversation = [
                {
                    "role": "user",
                    "content": f"""Execute the following task:
                    1. Create a file at {summary_file} containing a list of Python keywords
                    2. Count how many keywords there are
                    3. Return the results in the required schema format

                    Task name should be "Python Keywords Summary"
                    List the files you created
                    Indicate success
                    Provide a summary of what you did
                    Include metrics for: keyword_count, unique_chars"""
                }
            ]

            result = cli.chat_structured(conversation, TaskExecutionSchema)

            # Verify result
            assert result.value.task_name == "Python Keywords Summary"
            assert result.value.success is True
            assert summary_file in result.value.files_created or "codex_summary.txt" in str(result.value.files_created)
            assert len(result.value.output_summary) > 20
            assert "keyword_count" in result.value.metrics
            assert result.value.metrics["keyword_count"] > 0

            # Verify file was actually created
            assert os.path.exists(summary_file)

    def test_schema_validation_with_markers(self):
        """Test that marker-based extraction works"""
        cli = LlmCodexCli()

        # Use a prompt that should produce markers
        conversation = [
            {
                "role": "user",
                "content": """First explain your understanding, then create:
                name: "Test Person", age: 28, is_active: true"""
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Should successfully parse with markers
        assert result.value.name == "Test Person"
        assert result.value.age == 28
        assert result.value.is_active is True

        # Check that markers were mentioned in logs
        assert "Processing Response" in result.output
        assert ("Found JSON between markers" in result.output or
                "Falling back to JSON extraction" in result.output)

    def test_multiple_calls_consistency(self):
        """Test that multiple calls produce consistent results"""
        cli = LlmCodexCli()

        results = []
        for i in range(3):
            conversation = [
                {
                    "role": "user",
                    "content": f"Create person {i+1}, age {30+i}, active: true"
                }
            ]

            result = cli.chat_structured(conversation, SimpleSchema)
            results.append(result)

            # Each result should be valid
            assert result.value.age == 30 + i
            assert result.value.is_active is True

        # All results should have proper logging
        for result in results:
            assert "Codex CLI Structured Output" in result.output
            assert "Validation: PASSED" in result.output


@pytest.mark.skipif(
    not OriginalLlmCodexCli.check_config if hasattr(OriginalLlmCodexCli, 'check_config') else True,
    reason="Codex CLI not configured"
)
class TestCodexCliEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_response_handling(self):
        """Test handling of empty or invalid responses"""
        cli = LlmCodexCli()

        # This should trigger error handling
        conversation = [
            {
                "role": "user",
                "content": "Return an empty object: {}"
            }
        ]

        # Should handle empty object error
        with pytest.raises(Exception) as exc_info:
            cli.chat_structured(conversation, SimpleSchema)

        # Should have error in the log
        assert "ERROR" in str(exc_info.value) or "required" in str(exc_info.value)

    def test_large_schema(self):
        """Test with large complex schema"""

        class LargeSchema(BaseModel):
            items: List[Dict[str, str]] = Field(description="List of items with string keys and values")
            metadata: Dict[str, List[int]] = Field(description="Metadata with lists of integers")

        cli = LlmCodexCli()

        conversation = [
            {
                "role": "user",
                "content": """Create data with:
                - 2 items, each with keys "id", "name", "description"
                - metadata with keys "values" containing [10,20,30] and "codes" containing [1,2,3]"""
            }
        ]

        result = cli.chat_structured(conversation, LargeSchema)

        assert len(result.value.items) == 2
        assert all("id" in item for item in result.value.items)
        assert result.value.metadata["values"] == [10, 20, 30]
        assert result.value.metadata["codes"] == [1, 2, 3]
