"""Fluent TOML file handler for Bear Dereth."""

from __future__ import annotations

import tomllib
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel
import tomli_w

from ._base_file_handler import FluentFileHandlerBase as FileHandler

if TYPE_CHECKING:
    from pathlib import Path


class TomlFileHandler(FileHandler[dict[str, Any]]):
    """Fluent TOML file handler with method chaining support.

    Supports reading, writing, and transforming TOML files with automatic
    validation and Pydantic model integration.

    Example:
        # Read and transform TOML
        config = (TomlFileHandler("pyproject.toml")
                 .read()
                 .transform(update_dependencies)
                 .save()
                 .data)

        # Convert Pydantic model to TOML
        (TomlFileHandler("config.toml")
            .set_data(my_model)
            .from_pydantic(exclude_none=True)
            .save())

        # Convert between formats
        (TomlFileHandler("input.toml")
            .read()
            .write_to("output.json"))  # Auto-converts to JSON
    """

    valid_extensions: ClassVar[list[str]] = ["toml"]

    def _read_implementation(self) -> dict[str, Any]:
        """Read and parse TOML file.

        Returns:
            Parsed TOML data as dictionary

        Raises:
            tomllib.TOMLDecodeError: If file contains invalid TOML
            ValueError: If file cannot be read
        """
        try:
            with open(self._path, "rb") as file:
                return tomllib.load(file)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML in {self._path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading TOML file {self._path}: {e}") from e

    def _write_implementation(self, target_path: Path, data: Any) -> None:
        """Write data as TOML to target file.

        Args:
            target_path: Path to write to
            data: Data to serialize as TOML (must be dict-like)

        Raises:
            TypeError: If data cannot be TOML serialized
            ValueError: If file cannot be written
        """
        if not isinstance(data, dict):
            raise TypeError(f"TOML data must be a dictionary, got {type(data)}")

        try:
            toml_string: str = tomli_w.dumps(data)
            target_path.write_text(toml_string, encoding="utf-8")
        except Exception as e:
            raise ValueError(f"Error writing TOML file {target_path}: {e}") from e

    def from_pydantic(self, model: BaseModel, exclude_none: bool = True, **kwargs) -> TomlFileHandler:
        """Convert Pydantic model to TOML data (fluent).

        Args:
            model: Pydantic model to convert
            exclude_none: Whether to exclude None values
            **kwargs: Additional arguments to model_dump

        Returns:
            Self for method chaining
        """
        self._data = model.model_dump(exclude_none=exclude_none, **kwargs)
        return self

    def to_pydantic(self, model_class: type[BaseModel]) -> BaseModel:
        """Convert current TOML data to Pydantic model (helper method).

        This is a helper method that doesn't mutate the internal state.
        The internal data remains as a dict for consistency.

        Args:
            model_class: Pydantic model class to create

        Returns:
            Validated Pydantic model instance

        Raises:
            ValueError: If no data loaded or data cannot be converted
        """
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")

        try:
            return model_class.model_validate(self._data)
        except Exception as e:
            raise ValueError(f"Cannot convert data to {model_class.__name__}: {e}") from e

    def get_section(self, section: str, default: dict[str, Any] | None = None) -> dict[str, Any] | None:
        """Get a specific section from TOML data (helper method).

        Args:
            section: Section name (supports dot notation like 'tool.poetry')
            default: Default value if section not found

        Returns:
            Section data or default
        """
        if self._data is None:
            return default

        current: dict[str, Any] = self._data
        for key in section.split("."):
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current if isinstance(current, dict) else default

    def update_section(self, section: str, data: dict[str, Any]) -> TomlFileHandler:
        """Update a specific section in TOML data (fluent).

        Args:
            section: Section name (supports dot notation)
            data: Data to merge into section

        Returns:
            Self for method chaining
        """
        if self._data is None:
            self._data = {}

        keys: list[str] = section.split(".")
        current: dict[str, Any] = self._data

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            if not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        final_key: str = keys[-1]
        if final_key not in current or not isinstance(current[final_key], dict):
            current[final_key] = {}

        current[final_key].update(data)
        return self

    def to_toml_string(self, save: bool = False) -> str:
        """Convert current data to TOML string.

        Args:
            save: If True, also write to the file path

        Returns:
            TOML formatted string

        Raises:
            ValueError: If no data loaded or data cannot be serialized
        """
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")

        try:
            data: str = tomli_w.dumps(self._data)
            if save and self._path:
                self._path.write_text(data, encoding="utf-8")
            return data
        except Exception as e:
            raise ValueError(f"Cannot serialize data to TOML: {e}") from e


class PyProjectToml(BaseModel):
    """Pydantic model for pyproject.toml files.

    Simplified representation focusing on common project metadata.
    For full pyproject.toml support, use the raw TOML data.
    """

    name: str
    version: str | None = None
    dynamic: list[str] | None = None
    description: str | None = None
    author_name: str | None = None
    author_email: str | None = None
    dependencies: list[str] | None = None

    def model_post_init(self, context: Any) -> None:
        """Clean up dependencies after initialization."""
        if self.dependencies:
            cleaned = []
            for dep in self.dependencies:
                if isinstance(dep, str):
                    clean_name = dep.split(" ")[0].split(">=")[0].split("==")[0].split("<=")[0]
                    cleaned.append(clean_name)
            self.dependencies = cleaned
        return super().model_post_init(context)

    @classmethod
    def from_toml_data(cls, data: dict[str, Any]) -> PyProjectToml:
        """Create PyProjectToml from parsed TOML data.

        Args:
            data: Full pyproject.toml data dictionary

        Returns:
            PyProjectToml instance with extracted project data
        """
        project_data: dict = data.get("project", {})
        authors: list = project_data.get("authors", [])
        first_author: dict[str, str] = authors[0] if authors else {}

        return cls(
            name=project_data.get("name", ""),
            version=project_data.get("version"),
            dynamic=project_data.get("dynamic"),
            description=project_data.get("description"),
            author_name=first_author.get("name") if first_author else None,
            author_email=first_author.get("email") if first_author else None,
            dependencies=project_data.get("dependencies"),
        )
