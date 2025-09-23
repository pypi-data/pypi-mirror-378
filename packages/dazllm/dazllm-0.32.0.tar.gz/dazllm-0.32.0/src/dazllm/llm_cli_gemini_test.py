"""
Comprehensive tests for Gemini CLI structured output with result.json separation

Tests various schemas and ensures proper separation of output logs from results.
"""

import pytest
import os
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from .llm_cli_gemini import LlmGeminiCli
from .llm_gemini_cli import LlmGeminiCli as OriginalLlmGeminiCli


# Define test schemas (same as Claude/Codex tests for consistency)

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
    not LlmGeminiCli.is_available(),
    reason="Gemini CLI not available"
)
class TestGeminiCliStructured:
    """Test Gemini CLI structured output with real calls"""

    def test_simple_schema(self):
        """Test with a simple schema"""
        cli = LlmGeminiCli()

        conversation = [
            {
                "role": "user",
                "content": "Create a person named Emma who is 27 years old and active."
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Verify result
        assert result.value.name == "Emma"
        assert result.value.age == 27
        assert result.value.is_active is True

        # Verify logs are present
        assert "Gemini CLI Structured Output" in result.output
        assert "Schema: SimpleSchema" in result.output
        assert "Validation: PASSED" in result.output

    def test_file_listing_task(self):
        """Test with actual file system task"""
        cli = LlmGeminiCli()

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
        cli = LlmGeminiCli()

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
        cli = LlmGeminiCli()

        conversation = [
            {
                "role": "user",
                "content": """Create a developer profile for Sarah Williams, age 29,
                email sarah@example.com. She has 2 projects:
                1. "ReactApp" in JavaScript with 300 stars and contributors ["Tom", "Jerry"]
                2. "BackendAPI" in Python with 250 stars and contributors ["Alice"]
                She has made 750 total contributions and has been active since 2020."""
            }
        ]

        result = cli.chat_structured(conversation, ComplexNestedSchema)

        # Verify nested structures
        assert result.value.user.name == "Sarah Williams"
        assert result.value.user.age == 29
        assert result.value.user.email == "sarah@example.com"

        assert len(result.value.projects) == 2
        assert result.value.projects[0].name == "ReactApp"
        assert result.value.projects[0].language == "JavaScript"
        assert result.value.projects[0].stars == 300
        assert "Tom" in result.value.projects[0].contributors

        assert result.value.total_contributions == 750
        assert "2020" in result.value.active_since

    def test_task_with_file_creation(self):
        """Test task that creates files and returns structured result"""
        cli = LlmGeminiCli()

        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_file = os.path.join(tmpdir, "gemini_summary.txt")

            conversation = [
                {
                    "role": "user",
                    "content": f"""Execute the following task:
                    1. Create a file at {summary_file} containing a list of programming languages
                    2. Count how many languages you listed
                    3. Return the results in the required schema format

                    Task name should be "Programming Languages Summary"
                    List the files you created
                    Indicate success
                    Provide a summary of what you did
                    Include metrics for: language_count, categories_count"""
                }
            ]

            result = cli.chat_structured(conversation, TaskExecutionSchema)

            # Verify result
            assert result.value.task_name == "Programming Languages Summary"
            assert result.value.success is True
            assert summary_file in result.value.files_created or "gemini_summary.txt" in str(result.value.files_created)
            assert len(result.value.output_summary) > 20
            assert "language_count" in result.value.metrics
            assert result.value.metrics["language_count"] > 0

            # Verify file was actually created
            assert os.path.exists(summary_file)

    def test_schema_validation_with_markers(self):
        """Test that marker-based extraction works"""
        cli = LlmGeminiCli()

        # Use a prompt that should produce markers
        conversation = [
            {
                "role": "user",
                "content": """Think about the task, then create:
                name: "Marker Test", age: 35, is_active: false"""
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Should successfully parse with markers
        assert result.value.name == "Marker Test"
        assert result.value.age == 35
        assert result.value.is_active is False

        # Check that processing was mentioned in logs
        assert "Processing Response" in result.output
        assert ("Found JSON between markers" in result.output or
                "Falling back to JSON extraction" in result.output)

    def test_multiple_calls_consistency(self):
        """Test that multiple calls produce consistent results"""
        cli = LlmGeminiCli()

        results = []
        for i in range(3):
            conversation = [
                {
                    "role": "user",
                    "content": f"Create person number {i+1}, age {40+i}, active: false"
                }
            ]

            result = cli.chat_structured(conversation, SimpleSchema)
            results.append(result)

            # Each result should be valid
            assert result.value.age == 40 + i
            assert result.value.is_active is False

        # All results should have proper logging
        for result in results:
            assert "Gemini CLI Structured Output" in result.output
            assert "Validation: PASSED" in result.output

    def test_session_metrics(self):
        """Test that session metrics are captured in logs"""
        cli = LlmGeminiCli()

        conversation = [
            {
                "role": "user",
                "content": "Create a simple person: name is Session Test, age 50, active true"
            }
        ]

        result = cli.chat_structured(conversation, SimpleSchema)

        # Verify result
        assert result.value.name == "Session Test"
        assert result.value.age == 50
        assert result.value.is_active is True

        # Check for session information in logs (if available)
        # Gemini CLI may include session metrics
        assert "Gemini CLI" in result.output


@pytest.mark.skipif(
    not OriginalLlmGeminiCli.check_config if hasattr(OriginalLlmGeminiCli, 'check_config') else True,
    reason="Gemini CLI not configured"
)
class TestGeminiCliEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_response_handling(self):
        """Test handling of empty or invalid responses"""
        cli = LlmGeminiCli()

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

        cli = LlmGeminiCli()

        conversation = [
            {
                "role": "user",
                "content": """Create data with:
                - 3 items, each with keys "id", "title", "status"
                - metadata with keys "priorities" containing [1,2,3,4,5] and "levels" containing [10,20]"""
            }
        ]

        result = cli.chat_structured(conversation, LargeSchema)

        assert len(result.value.items) == 3
        assert all("id" in item for item in result.value.items)
        assert result.value.metadata["priorities"] == [1, 2, 3, 4, 5]
        assert result.value.metadata["levels"] == [10, 20]
