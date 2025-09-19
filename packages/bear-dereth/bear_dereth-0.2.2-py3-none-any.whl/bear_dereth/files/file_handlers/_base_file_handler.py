"""Base class for fluent file handlers with method chaining support."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Self

from bear_dereth.files.file_handlers._file_info import FileInfo

if TYPE_CHECKING:
    from collections.abc import Callable


class FluentFileHandlerBase[T](ABC):
    """Abstract base class for fluent file handlers that support method chaining.

    This base class provides a fluent interface for file operations where methods
    return self to enable chaining. Each handler maintains state (file path and data)
    and can read, transform, and write data in a chainable manner.

    Example:
        data = (FileHandler("config.json")
               .read()
               .transform(some_function)
               .write_to("output.yaml")
               .data)
    """

    valid_extensions: ClassVar[list[str]] = []
    """List of file extensions this handler supports (without dots)."""

    def __init__(self, file_path: Path | str | None) -> None:
        """Initialize the handler with a file path.

        Args:
            file_path: Path to the file to handle
        """
        self._path: Path = Path(file_path) if file_path is not None else Path()
        self._data: T | None = None
        self._info = FileInfo(path=self._path)

    @property
    def path(self) -> Path:
        """Get the current file path."""
        return self._path

    @property
    def data(self) -> T | None:
        """Get the currently loaded data."""
        return self._data

    def get(self) -> T:
        """Alias for data property to get the currently loaded data."""
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")
        return self._data

    @classmethod
    def supports_extension(cls, file_path: Path | str) -> bool:
        """Check if this handler supports the given file extension.

        Args:
            file_path: Path to check

        Returns:
            True if this handler supports the file extension
        """
        return Path(file_path).suffix.lstrip(".") in cls.valid_extensions

    @abstractmethod
    def _read_implementation(self) -> T:
        """Read and parse the file. Must be implemented by subclasses.

        Returns:
            Parsed file data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        ...

    @abstractmethod
    def _write_implementation(self, target_path: Path, data: T) -> None:
        """Write data to file. Must be implemented by subclasses.

        Args:
            target_path: Path to write to
            data: Data to write

        Raises:
            ValueError: If data cannot be serialized to target format
            OSError: If file cannot be written
        """
        ...

    def read(self) -> Self:
        """Read the file and store data internally for chaining.

        Returns:
            Self for method chaining

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        if not self._path.exists():
            raise FileNotFoundError(f"File not found: {self._path}")

        self._data = self._read_implementation()
        return self

    def write_to(self, target_path: Path | str, mkdir: bool = True) -> Self:
        """Write current data to a target file.

        Args:
            target_path: Path to write to
            mkdir: Whether to create parent directories if they don't exist

        Returns:
            Self for method chaining

        Raises:
            ValueError: If no data has been loaded or data is invalid for target format
            OSError: If file cannot be written
        """
        if self._data is None:
            raise ValueError("No data loaded. Call read() first or set data manually.")

        target = Path(target_path)

        if mkdir and not target.parent.exists():
            target.parent.mkdir(parents=True, exist_ok=True)

        self._write_implementation(target, self._data)
        return self

    def save(self, mkdir: bool = True) -> Self:
        """Save current data back to the original file path.

        Args:
            mkdir: Whether to create parent directories if they don't exist

        Returns:
            Self for method chaining
        """
        return self.write_to(self._path, mkdir=mkdir)

    def transform(self, func: Callable[[T], T]) -> Self:
        """Apply a transformation function to the current data.

        Args:
            func: Function that takes current data and returns transformed data

        Returns:
            Self for method chaining

        Raises:
            ValueError: If no data has been loaded
        """
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")

        self._data = func(self._data)
        return self

    def set_data(self, data: T) -> Self:
        """Manually set the internal data.

        Args:
            data: Data to set

        Returns:
            Self for method chaining
        """
        self._data = data
        return self

    def get_file_info(self) -> FileInfo:
        """Get information about the current file.

        Returns:
            Dictionary with file metadata
        """
        return self._info


class FileHandler(FluentFileHandlerBase[str]):
    """Alias for FluentFileHandlerBase for easier imports."""

    def _read_implementation(self) -> str:
        """Default implementation - read as text."""
        return self._path.read_text(encoding="utf-8")

    def _write_implementation(self, target_path: Path, data: str) -> None:
        """Default implementation - write as text."""
        target_path.write_text(data, encoding="utf-8")
