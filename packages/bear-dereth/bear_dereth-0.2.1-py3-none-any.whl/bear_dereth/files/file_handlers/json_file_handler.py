"""Fluent JSON file handler for Bear Dereth."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar, Self

from ._base_file_handler import FluentFileHandlerBase as FileHandler

if TYPE_CHECKING:
    from pathlib import Path


JSONData = dict[str, Any] | list[Any]


class JsonFileHandler(FileHandler[JSONData]):
    """Fluent JSON file handler with method chaining support.

    Supports reading, writing, and transforming JSON files with automatic
    validation and pretty formatting.

    Example:
        # Read and transform JSON
        data = (JsonFileHandler("config.json")
               .read()
               .transform(lambda d: {**d, "updated": True})
               .save()
               .data)

        # Convert JSON to another format
        (JsonFileHandler("input.json")
            .read()
            .write_to("output.yaml"))  # Auto-converts to YAML if handler exists
    """

    valid_extensions: ClassVar[list[str]] = ["json"]

    def __init__(self, file_path: Path | str, indent: int = 2, sort_keys: bool = False) -> None:
        """Initialize JSON handler with formatting options.

        Args:
            file_path: Path to the JSON file
            indent: Number of spaces for pretty printing (default: 2)
            sort_keys: Whether to sort keys in output (default: False)
        """
        super().__init__(file_path)
        self.indent = indent
        self.sort_keys = sort_keys

    def _read_implementation(self) -> dict[str, Any] | list[Any]:
        """Read and parse JSON file.

        Returns:
            Parsed JSON data (dict or list)

        Raises:
            json.JSONDecodeError: If file contains invalid JSON
            ValueError: If file cannot be read
        """
        try:
            with open(self._path, encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {self._path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading JSON file {self._path}: {e}") from e

    def _write_implementation(self, target_path: Path, data: Any) -> None:
        """Write data as JSON to target file.

        Args:
            target_path: Path to write to
            data: Data to serialize as JSON

        Raises:
            TypeError: If data cannot be JSON serialized
            ValueError: If file cannot be written
        """
        try:
            json_string: str = json.dumps(data, indent=self.indent, sort_keys=self.sort_keys, ensure_ascii=False)
            target_path.write_text(json_string, encoding="utf-8")
        except TypeError as e:
            raise ValueError(f"Data cannot be serialized to JSON: {e}") from e
        except Exception as e:
            raise ValueError(f"Error writing JSON file {target_path}: {e}") from e

    def set_formatting(self, indent: int | None = 2, sort_keys: bool = False) -> Self:
        """Set JSON formatting options (fluent).

        Args:
            indent: Number of spaces for indentation
            sort_keys: Whether to sort keys

        Returns:
            Self for method chaining
        """
        self.indent: int | None = indent
        self.sort_keys: bool = sort_keys
        return self

    def pretty(self) -> Self:
        """Enable pretty printing with 2-space indentation (fluent).

        Returns:
            Self for method chaining
        """
        return self.set_formatting(indent=2, sort_keys=False)

    def compact(self) -> Self:
        """Enable compact output with no indentation (fluent).

        Returns:
            Self for method chaining
        """
        return self.set_formatting(indent=None, sort_keys=False)

    def sorted_keys(self) -> Self:
        """Enable sorted keys in output (fluent).

        Returns:
            Self for method chaining
        """
        self.sort_keys = True
        return self


class JsonLFileHandler(FileHandler):
    """Fluent JSONL (JSON Lines) file handler.

    Handles files where each line is a separate JSON object.

    Example:
        lines = (JsonLFileHandler("data.jsonl")
                .read()
                .transform(lambda lines: [process(line) for line in lines])
                .save()
                .data)
    """

    valid_extensions: ClassVar[list[str]] = ["jsonl"]

    @property
    def lines(self) -> list[str]:
        """Get JSON data as a list of lines."""
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")
        return self._path.read_text(encoding="utf-8").splitlines()

    def _read_implementation(self) -> list[dict[str, Any]]:
        """Read JSONL file as list of JSON objects.

        Returns:
            List of parsed JSON objects, one per line
        """
        json_lines: list[dict[str, Any]] = []
        try:
            for ln_num, line in enumerate(self.lines, start=1):
                if not line.strip():
                    continue
                try:
                    json_lines.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON on line {ln_num}: {e}") from e
            return json_lines
        except Exception as e:
            raise ValueError(f"Error reading JSONL file {self._path}: {e}") from e

    def _write_implementation(self, target_path: Path, data: list[dict[str, Any]] | Any) -> None:
        """Write list of objects as JSONL.

        Args:
            target_path: Path to write to
            data: List of objects to write as JSONL
        """
        if not isinstance(data, list):
            raise TypeError("JSONL data must be a list of objects")

        try:
            lines: list[str] = [json.dumps(obj, ensure_ascii=False) for obj in data]
            content: str = "\n".join(lines) + "\n" if lines else ""
            target_path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Error writing JSONL file {target_path}: {e}") from e
