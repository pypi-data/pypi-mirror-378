"""
File Handler

This module provides functionality to handle various file types for reading and writing.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import chardet


class FileHandlerBase(ABC):
    """Base class for file handlers."""

    @abstractmethod
    def can_handle(self, file_path: str) -> bool:
        """Check if this handler can process the given file."""
        pass

    @abstractmethod
    def read_content(self, file_path: str) -> str:
        """Read content from file."""
        raise NotImplementedError()

    @abstractmethod
    def write_content(self, file_path: str, content: str) -> None:
        """Write content to file."""
        # Ensure consistent line endings
        content = content.replace("\r\n", "\n")

        with open(file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)


class TextFileHandler(FileHandlerBase):
    """Handler for text files."""

    def __init__(self):
        self.supported_extensions = {
            ".txt",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".md",
            ".rst",
            ".yaml",
            ".yml",
            ".ini",
            ".cfg",
            ".conf",
            ".log",
            ".csv",
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".rb",
            ".php",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".cs",
            ".go",
            ".rs",
            ".swift",
            ".kt",
            ".scala",
            ".r",
            ".m",
            ".pl",
            ".lua",
            ".dart",
        }

    def can_handle(self, file_path: str) -> bool:
        """Check if this is a text file we can handle."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions

    def read_content(self, file_path: str) -> str:
        """Read text file content with automatic encoding detection."""
        # First, try to detect encoding
        with open(file_path, "rb") as f:
            raw_data = f.read()

        # Detect encoding
        detected = chardet.detect(raw_data)
        encoding = detected.get("encoding", "utf-8")

        # Fallback encodings to try
        encodings_to_try = [
            encoding,
            "utf-8",
            "latin-1",
            "cp1252",
            "shift_jis",
            "euc-jp",
        ]

        for enc in encodings_to_try:
            if enc is None:
                continue
            try:
                content = raw_data.decode(enc)
                # 改行文字を統一（Windowsの\r\nを\nに変換）
                return content.replace("\r\n", "\n")
            except (UnicodeDecodeError, LookupError):
                continue

        # If all else fails, use utf-8 with error handling
        content = raw_data.decode("utf-8", errors="replace")
        return content.replace("\r\n", "\n")

    def write_content(self, file_path: str, content: str) -> None:
        """Write content to text file."""
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)


class BinaryFileHandler(FileHandlerBase):
    """Handler for binary files (converts to base64 for processing)."""

    def __init__(self):
        self.supported_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".bz2",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".svg",
            ".ico",
            ".mp3",
            ".wav",
            ".flac",
            ".ogg",
            ".mp4",
            ".avi",
            ".mkv",
            ".exe",
            ".dll",
            ".so",
            ".dylib",
        }

    def can_handle(self, file_path: str) -> bool:
        """Check if this is a binary file we can handle."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_extensions

    def read_content(self, file_path: str) -> str:
        """Read binary file and convert to base64 string."""
        import base64

        with open(file_path, "rb") as f:
            binary_data = f.read()

        # Convert to base64 string
        b64_string = base64.b64encode(binary_data).decode("ascii")

        # Add metadata header
        ext = Path(file_path).suffix.lower()
        header = f"BINARY_FILE:{ext}:BASE64:\n"

        return header + b64_string

    def write_content(self, file_path: str, content: str) -> None:
        """Write base64 content back to binary file."""
        import base64

        # Parse header and content
        lines = content.split("\n", 1)
        if len(lines) < 2 or not lines[0].startswith("BINARY_FILE:"):
            raise ValueError("Invalid binary file content format")

        header = lines[0]
        b64_content = lines[1]

        # Extract file extension from header
        parts = header.split(":")
        if len(parts) < 4:
            raise ValueError("Invalid binary file header format")

        # Decode base64 content
        try:
            binary_data = base64.b64decode(b64_content)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 content: {e}")

        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Write binary data
        with open(file_path, "wb") as f:
            f.write(binary_data)


class FileHandler:
    """Main file handler that delegates to appropriate specialized handlers."""

    def __init__(self):
        self.handlers: List[FileHandlerBase] = [
            TextFileHandler(),
            BinaryFileHandler(),
        ]

    def can_handle(self, file_path: str) -> bool:
        """Check if any handler can process the given file."""
        return any(handler.can_handle(file_path) for handler in self.handlers)

    def read_file(self, file_path: str) -> str:
        """
        Read content from file using appropriate handler.

        Args:
            file_path: Path to the file to read

        Returns:
            File content as string

        Raises:
            ValueError: If no handler can process the file
            FileNotFoundError: If file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        for handler in self.handlers:
            if handler.can_handle(file_path):
                return handler.read_content(file_path)

        # If no specific handler found, try text handler as fallback
        try:
            return TextFileHandler().read_content(file_path)
        except Exception as e:
            raise ValueError(f"Cannot read file {file_path}: {e}")

    def write_file(self, file_path: str, content: str) -> None:
        """
        Write content to file using appropriate handler.

        Args:
            file_path: Path to the file to write
            content: Content to write

        Raises:
            ValueError: If content format is not supported
        """
        # Check if content is binary format
        if content.startswith("BINARY_FILE:"):
            BinaryFileHandler().write_content(file_path, content)
        else:
            # Default to text handler
            TextFileHandler().write_content(file_path, content)

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        path_obj = Path(file_path)
        stat = path_obj.stat()

        # Determine file type
        file_type = "unknown"
        handler_name = None

        for handler in self.handlers:
            if handler.can_handle(file_path):
                file_type = handler.__class__.__name__.replace(
                    "FileHandler", ""
                ).lower()
                handler_name = handler.__class__.__name__
                break

        # Try to detect encoding for text files
        encoding = None
        if isinstance(self._get_handler(file_path), TextFileHandler):
            try:
                with open(file_path, "rb") as f:
                    sample = f.read(1024)
                detected = chardet.detect(sample)
                encoding = detected.get("encoding")
            except Exception:
                encoding = "unknown"

        return {
            "path": str(path_obj.absolute()),
            "name": path_obj.name,
            "extension": path_obj.suffix,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "file_type": file_type,
            "handler": handler_name,
            "encoding": encoding,
            "is_text": file_type == "text",
            "is_binary": file_type == "binary",
        }

    def list_supported_extensions(self) -> Dict[str, List[str]]:
        """Get list of supported file extensions by handler type."""
        result = {}

        for handler in self.handlers:
            handler_name = handler.__class__.__name__
            if hasattr(handler, "supported_extensions"):
                result[handler_name] = sorted(list(handler.supported_extensions))

        return result

    def _get_handler(self, file_path: str) -> Optional[FileHandlerBase]:
        """Get the appropriate handler for a file."""
        for handler in self.handlers:
            if handler.can_handle(file_path):
                return handler
        return None

    def batch_read_files(
        self, file_paths: List[str]
    ) -> Dict[str, Union[str, Exception]]:
        """
        Read multiple files at once.

        Args:
            file_paths: List of file paths to read

        Returns:
            Dictionary mapping file paths to their content or exceptions
        """
        results: Dict[str, Union[str, Exception]] = {}

        for file_path in file_paths:
            try:
                content = self.read_file(file_path)
                results[file_path] = content
            except Exception as e:
                results[file_path] = e

        return results

    def find_files(
        self,
        directory: str,
        patterns: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
        recursive: bool = True,
    ) -> List[str]:
        """
        Find files in directory matching criteria.

        Args:
            directory: Directory to search
            patterns: List of filename patterns (glob-style)
            extensions: List of file extensions to include
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        import glob

        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        found_files = []
        search_dir = Path(directory)

        if patterns:
            # Use glob patterns
            for pattern in patterns:
                if recursive:
                    glob_pattern = str(search_dir / "**" / pattern)
                    found_files.extend(glob.glob(glob_pattern, recursive=True))
                else:
                    glob_pattern = str(search_dir / pattern)
                    found_files.extend(glob.glob(glob_pattern))
        else:
            # Find all files
            if recursive:
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        found_files.append(str(file_path))
            else:
                for file_path in search_dir.glob("*"):
                    if file_path.is_file():
                        found_files.append(str(file_path))

        # Filter by extensions if specified
        if extensions:
            extensions = [
                ext.lower() if ext.startswith(".") else f".{ext.lower()}"
                for ext in extensions
            ]
            found_files = [
                f for f in found_files if Path(f).suffix.lower() in extensions
            ]

        # Filter to only supported files
        found_files = [f for f in found_files if self.can_handle(f)]

        return sorted(list(set(found_files)))

    def get_directory_summary(self, directory: str) -> Dict[str, Any]:
        """
        Get summary information about files in a directory.

        Args:
            directory: Directory to analyze

        Returns:
            Dictionary with summary statistics
        """
        files = self.find_files(directory, recursive=True)

        total_files = len(files)
        total_size = 0
        file_types: Dict[str, int] = {}
        extensions: Dict[str, int] = {}

        for file_path in files:
            try:
                info = self.get_file_info(file_path)
                total_size += info["size"]

                file_type = info["file_type"]
                file_types[file_type] = file_types.get(file_type, 0) + 1

                ext = info["extension"].lower()
                extensions[ext] = extensions.get(ext, 0) + 1

            except Exception:  # nosec B112
                # Skip files that can't be processed
                continue

        return {
            "directory": directory,
            "total_files": total_files,
            "total_size": total_size,
            "file_types": file_types,
            "extensions": extensions,
            "supported_files": len([f for f in files if self.can_handle(f)]),
        }
