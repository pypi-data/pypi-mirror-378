"""Fluent YAML file handler for Bear Dereth."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, NoReturn

from ._base_file_handler import FluentFileHandlerBase

if TYPE_CHECKING:
    from pathlib import Path

try:
    import yaml  # type: ignore[import]

    HAS_YAML = True
except ImportError:

    class yaml:  # noqa: N801
        """Mock yaml module when PyYAML is not installed."""

        class YAMLError(Exception):
            """Mock YAMLError exception."""

        @staticmethod
        def safe_load(_) -> NoReturn:  # noqa: D102 ANN001
            raise ImportError("PyYAML is not installed")

        @staticmethod
        def load(*_, **__) -> NoReturn:  # noqa: D102
            raise ImportError("PyYAML is not installed")

        @staticmethod
        def dump(*_, **__) -> NoReturn:  # noqa: D102
            raise ImportError("PyYAML is not installed")

        def FullLoader(self) -> NoReturn:  # noqa: D102 N802
            raise ImportError("PyYAML is not installed")

    HAS_YAML = False


class YamlFileHandler(FluentFileHandlerBase):
    """Fluent YAML file handler with method chaining support.

    Supports reading, writing, and transforming YAML files with safe defaults
    and configurable formatting options.

    Example:
        # Read and transform YAML
        config = (YamlFileHandler("config.yaml")
                 .read()
                 .transform(update_config)
                 .pretty()
                 .save()
                 .data)

        # Convert between formats
        (YamlFileHandler("input.yaml")
            .read()
            .write_to("output.json"))  # Auto-converts to JSON

        # Control YAML formatting
        (YamlFileHandler("messy.yml")
            .read()
            .compact()  # Use flow style
            .sorted_keys()
            .save())
    """

    valid_extensions: ClassVar[list[str]] = ["yaml", "yml"]

    def __init__(self, file_path: Path | str, safe_mode: bool = True) -> None:
        """Initialize YAML handler with safety options.

        Args:
            file_path: Path to the YAML file
            safe_mode: Whether to use safe loading (recommended: True)

        Raises:
            ImportError: If PyYAML is not installed
        """
        if not HAS_YAML:
            raise ImportError("PyYAML is required for YAML file handling. Install it with: pip install pyyaml")

        super().__init__(file_path)
        self.safe_mode = safe_mode
        self.flow_style = False  # Pretty formatting by default
        self.sort_keys = False
        self.indent = 2
        self.width = None  # No line wrapping by default

    def _read_implementation(self) -> dict[str, Any] | list[Any]:
        """Read and parse YAML file.

        Returns:
            Parsed YAML data (dict, list, or other YAML types)

        Raises:
            yaml.YAMLError: If file contains invalid YAML
            ValueError: If file cannot be read
        """
        try:
            with open(self._path, encoding="utf-8") as file:
                if self.safe_mode:
                    return yaml.safe_load(file)

                return yaml.load(file, Loader=yaml.FullLoader)  # Only use unsafe loader if explicitly requested
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self._path}: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading YAML file {self._path}: {e}") from e

    def _write_implementation(self, target_path: Path, data: Any) -> None:
        """Write data as YAML to target file.

        Args:
            target_path: Path to write to
            data: Data to serialize as YAML

        Raises:
            yaml.YAMLError: If data cannot be YAML serialized
            ValueError: If file cannot be written
        """
        try:
            with open(target_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    data,
                    file,
                    default_flow_style=self.flow_style,
                    sort_keys=self.sort_keys,
                    indent=self.indent,
                    width=self.width,
                    allow_unicode=True,
                    # Security: never allow arbitrary Python objects
                    default_style=None,
                )
        except yaml.YAMLError as e:
            raise ValueError(f"Cannot serialize data to YAML: {e}") from e
        except Exception as e:
            raise ValueError(f"Error writing YAML file {target_path}: {e}") from e

    def unsafe_mode(self, enabled: bool = True) -> YamlFileHandler:
        """Enable or disable unsafe YAML loading (fluent).

        WARNING: Unsafe mode can execute arbitrary code! Only use with trusted files.

        Args:
            enabled: Whether to enable unsafe loading

        Returns:
            Self for method chaining
        """
        self.safe_mode: bool = not enabled
        return self

    def set_formatting(
        self,
        flow_style: bool = False,
        sort_keys: bool = False,
        indent: int = 2,
        width: int | None = None,
    ) -> YamlFileHandler:
        """Configure YAML formatting options (fluent).

        Args:
            flow_style: Use compact flow style (like JSON)
            sort_keys: Sort dictionary keys
            indent: Number of spaces for indentation
            width: Maximum line width (None for no limit)

        Returns:
            Self for method chaining
        """
        self.flow_style: bool = flow_style
        self.sort_keys: bool = sort_keys
        self.indent: int = indent
        self.width: int | None = width
        return self

    def pretty(self) -> YamlFileHandler:
        """Enable pretty formatting with block style (fluent).

        Returns:
            Self for method chaining
        """
        return self.set_formatting(flow_style=False, indent=2)

    def compact(self) -> YamlFileHandler:
        """Enable compact flow style formatting (fluent).

        Returns:
            Self for method chaining
        """
        return self.set_formatting(flow_style=True)

    def sorted_keys(self) -> YamlFileHandler:
        """Enable sorted keys in output (fluent).

        Returns:
            Self for method chaining
        """
        self.sort_keys = True
        return self

    def set_width(self, width: int | None) -> YamlFileHandler:
        """Set maximum line width for YAML output (fluent).

        Args:
            width: Maximum line width (None for unlimited)

        Returns:
            Self for method chaining
        """
        self.width = width
        return self

    def to_yaml_string(self) -> str:
        """Convert current data to YAML string without writing to file.

        Returns:
            YAML formatted string

        Raises:
            ValueError: If no data loaded
        """
        if self._data is None:
            raise ValueError("No data loaded. Call read() first.")

        try:
            return yaml.dump(
                self._data,
                default_flow_style=self.flow_style,
                sort_keys=self.sort_keys,
                indent=self.indent,
                width=self.width,
                allow_unicode=True,
            )
        except yaml.YAMLError as e:
            raise ValueError(f"Cannot serialize data to YAML: {e}") from e
