#!/usr/bin/env python3
# Author: Arun Brahma

from __future__ import annotations

import glob
import re
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Final

if TYPE_CHECKING:
    from collections.abc import Iterable


class AccessController:
    """Handles file system access control and security validation."""

    # Security constants
    _MAX_GLOB_RESULTS: Final[int] = 1000
    _DANGEROUS_SEQUENCES: Final[list[str]] = [
        "../",
        "..\\",
        "//",
        "\\\\",
        "*" * 10,
        "{" * 5,
    ]
    _DANGEROUS_ROOTS: Final[list[str]] = [
        "/etc",
        "/proc",
        "/sys",
        "/dev",
        "/boot",
        "c:\\windows",
        "c:\\system32",
        "c:\\program files",
        "~/.ssh",
        "~/.aws",
        "~/.config",
    ]
    _ROOT_PATHS: Final[set[str]] = {"/", "\\", "C:\\", "C:/", "C:", "/root", "/home"}
    _DANGEROUS_PATTERNS: Final[list[str]] = [
        "/etc",
        "/proc",
        "/sys",
        "/dev",
        "/boot",
        "C:\\Windows",
        "C:\\System32",
        "C:\\Program Files",
        "~/.ssh",
        "~/.aws",
        "~/.config",
    ]
    _WINDOWS_INDICATORS: Final[list[str]] = ["windows", "system32", "program files"]
    _RESERVED_NAMES: Final[set[str]] = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
    _ALLOWED_FFMPEG_FLAGS: Final[set[str]] = {
        "-i",
        "-f",
        "-y",
        "-n",
        "-c:v",
        "-vcodec",
        "-codec:v",
        "-vf",
        "-filter:v",
        "-aspect",
        "-pix_fmt",
        "-r",
        "-s",
        "-vframes",
        "-vn",
        "-frame_pts",
        "-frame_pkt_pts",
        "-c:a",
        "-acodec",
        "-codec:a",
        "-af",
        "-filter:a",
        "-ar",
        "-ac",
        "-ab",
        "-aq",
        "-an",
        "-c",
        "-codec",
        "-ss",
        "-t",
        "-to",
        "-itsoffset",
        "-b:v",
        "-b:a",
        "-b",
        "-crf",
        "-qp",
        "-q:v",
        "-q:a",
        "-maxrate",
        "-bufsize",
        "-minrate",
        "-filter_complex",
        "-lavfi",
        "-map",
        "-map_metadata",
        "-map_chapters",
        "-metadata",
        "-disposition",
        "-movflags",
        "-preset",
        "-tune",
        "-profile:v",
        "-level",
        "-hwaccel",
        "-hwaccel_device",
    }
    _DANGEROUS_CMD_PATTERNS: Final[list[str]] = [
        "|",
        "&",
        "&&",
        "||",
        "$",
        "`",
        "$(",
        "${",
        ">",
        "<",
        ">>",
        "<<",
        "\n",
        "\r",
    ]
    _FILTER_FLAGS: Final[list[str]] = [
        "-vf",
        "-filter:v",
        "-af",
        "-filter:a",
        "-filter_complex",
        "-lavfi",
    ]
    _DANGEROUS_SHELL_CHARS: Final[list[str]] = [
        ";",
        "|",
        "&",
        "$",
        "`",
        "<",
        ">",
        "\x00",
    ]
    _DANGEROUS_COMMAND_PATTERNS: Final[list[str]] = [
        r"\brm\s+",
        r"\bmv\s+",
        r"\bcp\s+",
        r"\bchmod\s+",
        r"\bsudo\s+",
        r"\bsu\s+",
        r"\bcurl\s+",
        r"\bwget\s+",
        r"\bsh\s+",
        r"\bbash\s+",
        r"\beval\s+",
        r"\bexec\s+",
    ]

    @classmethod
    def expand_globs(cls, patterns: Iterable[str], allowed_dirs: list[Path] | None = None) -> list[Path]:
        """Expand glob patterns safely with comprehensive path validation."""
        if allowed_dirs is None:
            allowed_dirs = [Path.cwd()]

        paths: list[Path] = []

        for pattern in patterns:
            if not cls._is_safe_glob_pattern(pattern):
                continue

            try:
                matches = glob.glob(pattern, recursive=True)
                if len(matches) > cls._MAX_GLOB_RESULTS:
                    matches = matches[: cls._MAX_GLOB_RESULTS]

                for match in matches:
                    path_obj = Path(match).resolve()
                    if cls.is_safe_path(path_obj, allowed_dirs):
                        paths.append(path_obj)

            except (OSError, ValueError):
                continue

        return cls._remove_duplicates(paths)

    @classmethod
    def _remove_duplicates(cls, paths: list[Path]) -> list[Path]:
        """Remove duplicate paths while preserving order."""
        unique: list[Path] = []
        seen = set()
        for p in paths:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        return unique

    @classmethod
    def _is_safe_glob_pattern(cls, pattern: str) -> bool:
        """Validate glob pattern is safe to use."""
        if not pattern or not isinstance(pattern, str):
            return False

        pattern_lower = pattern.lower()

        # Check for dangerous sequences
        for dangerous in cls._DANGEROUS_SEQUENCES:
            if dangerous in pattern_lower:
                return False

        # Check for system directory access attempts
        return all(not pattern_lower.startswith(root.lower()) for root in cls._DANGEROUS_ROOTS)

    @classmethod
    def is_safe_path(cls, path: object, allowed_dirs: list[Path] | None = None) -> bool:
        """Validate path is safe and within allowed directories."""
        try:
            path_obj = cls._convert_to_path(path)
            if path_obj is None:
                return False

            resolved_path = cls._resolve_path_safely(path_obj)
            if resolved_path is None:
                return False

            if not cls._is_valid_path_string(path_obj, resolved_path):
                return False

            if not cls._is_allowed_path_pattern(resolved_path):
                return False

            return cls._is_within_allowed_directories(resolved_path, allowed_dirs)

        except Exception:
            return False

    @classmethod
    def _convert_to_path(cls, path: object) -> Path | None:
        """Convert input to Path object with validation."""
        if path is None:
            return None

        if not isinstance(path, Path):
            path_str_check = str(path)
            if not path_str_check or not path_str_check.strip():
                return None
            path_obj = Path(path_str_check)
        else:
            path_obj = path

        return path_obj

    @classmethod
    def _resolve_path_safely(cls, path_obj: Path) -> Path | None:
        """Safely resolve path to absolute form."""
        try:
            return path_obj.resolve()
        except (OSError, RuntimeError):
            return None

    @classmethod
    def _is_valid_path_string(cls, path_obj: Path, resolved_path: Path) -> bool:
        """Validate path strings and detect traversal attempts."""
        path_str = str(resolved_path)
        original_str = str(path_obj)

        if not path_str.strip() or not original_str.strip():
            return False

        # Block root and system paths
        if path_str in cls._ROOT_PATHS:
            return False

        # Additional check for single character paths that could be roots
        if len(original_str.strip()) <= 3 and any(c in original_str for c in ["/", "\\"]):
            return False

        # Detect path traversal attempts in path components
        path_parts = path_obj.parts
        return not (".." in path_parts or any("." * 3 in part for part in path_parts))

    @classmethod
    def _is_allowed_path_pattern(cls, resolved_path: Path) -> bool:
        """Check if path matches allowed patterns."""
        path_str = str(resolved_path)
        path_lower = path_str.lower()

        # Check for dangerous path patterns
        for pattern in cls._DANGEROUS_PATTERNS:
            if cls._pattern_matches_path(path_str, resolved_path, pattern):
                return False

        # Additional checks for Windows patterns on any system
        return all(indicator not in path_lower for indicator in cls._WINDOWS_INDICATORS)

    @classmethod
    def _is_within_allowed_directories(cls, resolved_path: Path, allowed_dirs: list[Path] | None) -> bool:
        """Check if path is within allowed directories."""
        if allowed_dirs is None:
            allowed_dirs = [Path.cwd()]

        return any(cls._is_within_single_allowed(resolved_path, allowed_dir) for allowed_dir in allowed_dirs)

    @staticmethod
    def _pattern_matches_path(path_str: str, resolved_path: Path, pattern: str) -> bool:
        """Safely check whether a pattern matches the path without try/except in the loop."""
        try:
            return path_str.startswith(pattern) or Path(pattern).resolve() in resolved_path.parents
        except (OSError, ValueError):
            return path_str.lower().startswith(pattern.lower())

    @staticmethod
    def _is_within_single_allowed(resolved_path: Path, allowed_dir: Path) -> bool:
        """Safely check containment within a single allowed directory."""
        try:
            resolved_allowed = allowed_dir.resolve()
            return resolved_path == resolved_allowed or resolved_path.is_relative_to(resolved_allowed)
        except (ValueError, OSError):
            return False

    @staticmethod
    def ensure_parent_dir(path: Path) -> None:
        """Ensure parent directory exists, creating it if necessary."""
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def quote_path(path: Path) -> str:
        """Quote path for safe display in preview text."""
        return str(path)

    @staticmethod
    def most_recent_file(paths: Iterable[Path]) -> Path | None:
        """Find the most recently modified file from a collection."""
        latest: tuple[float, Path] | None = None
        for p in paths:
            try:
                mtime = p.stat().st_mtime
            except OSError:
                continue
            if latest is None or mtime > latest[0]:
                latest = (mtime, p)
        return latest[1] if latest else None

    @classmethod
    def sanitize_filename(cls, filename: str, max_length: int = 255) -> str:
        """Sanitize filename to prevent security issues and filesystem problems."""
        if not filename or not isinstance(filename, str):
            return "sanitized_file"

        # Remove or replace dangerous characters
        sanitized = re.sub(r"[^a-zA-Z0-9\s\._-]", "_", filename)

        # Prevent multiple consecutive dots (could be path traversal)
        sanitized = re.sub(r"\.{2,}", ".", sanitized)

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip(". ")

        # Prevent reserved names on Windows
        name_without_ext = sanitized.rsplit(".", 1)[0].upper()
        if name_without_ext in cls._RESERVED_NAMES:
            sanitized = f"safe_{sanitized}"

        # Truncate if too long while preserving extension
        if len(sanitized) > max_length:
            sanitized = cls._truncate_filename(sanitized, max_length)

        # Ensure we have something valid
        return sanitized if sanitized else "sanitized_file"

    @staticmethod
    def _truncate_filename(filename: str, max_length: int) -> str:
        """Truncate filename while preserving extension."""
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        max_name_length = max_length - len(ext) - 1 if ext else max_length
        return name[:max_name_length] + ("." + ext if ext else "")

    @classmethod
    def validate_ffmpeg_command(cls, cmd: list[str]) -> bool:
        """Validate ffmpeg command arguments for security."""
        if not cls._is_valid_command_structure(cmd):
            return False

        if not cls._check_command_injection_patterns(cmd):
            return False

        return cls._validate_command_flags_and_args(cmd)

    @staticmethod
    def _is_valid_command_structure(cmd: list[str]) -> bool:
        """Validate basic command structure."""
        if not cmd or not isinstance(cmd, list):
            return False
        return bool(cmd[0] and cmd[0] == "ffmpeg")

    @classmethod
    def _check_command_injection_patterns(cls, cmd: list[str]) -> bool:
        """Check for dangerous command injection patterns."""
        for i, arg in enumerate(cmd):
            is_filter_value = cls._is_filter_value(cmd, i)

            patterns_to_check = (
                [p for p in cls._DANGEROUS_CMD_PATTERNS if p != ";"]
                if is_filter_value
                else [*cls._DANGEROUS_CMD_PATTERNS, ";"]
            )

            for pattern in patterns_to_check:
                if pattern in arg:
                    return False
        return True

    @classmethod
    def _is_filter_value(cls, cmd: list[str], index: int) -> bool:
        """Check if argument is a filter value."""
        return index > 0 and cmd[index - 1].startswith("-") and cmd[index - 1] in cls._FILTER_FLAGS

    @classmethod
    def _validate_command_flags_and_args(cls, cmd: list[str]) -> bool:
        """Validate command flags and arguments."""
        i = 1  # Skip 'ffmpeg'
        while i < len(cmd):
            arg = cmd[i]

            if arg.startswith("-"):
                if arg not in cls._ALLOWED_FFMPEG_FLAGS:
                    return False

                # Skip flag value if present
                if i + 1 < len(cmd) and not cmd[i + 1].startswith("-"):
                    i += 1
            # Non-flag argument should be a safe file path
            elif not cls.is_safe_path(arg):
                return False

            i += 1

        return True

    @classmethod
    def sanitize_user_input(cls, user_input: str, max_length: int = 1000) -> str:
        """Sanitize user input to prevent injection attacks."""
        if not user_input or not isinstance(user_input, str):
            return ""

        # Truncate if too long
        if len(user_input) > max_length:
            user_input = user_input[:max_length]

        # Remove control characters (except normal whitespace)
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", user_input)

        # Remove dangerous shell characters
        for char in cls._DANGEROUS_SHELL_CHARS:
            sanitized = sanitized.replace(char, " ")

        # Remove dangerous command patterns
        for pattern in cls._DANGEROUS_COMMAND_PATTERNS:
            sanitized = re.sub(pattern, " ", sanitized, flags=re.IGNORECASE)

        # Normalize whitespace
        return " ".join(sanitized.split())


# Backward compatibility wrapper functions
def expand_globs(patterns: Iterable[str], allowed_dirs: list[Path] | None = None) -> list[Path]:
    """Expand glob patterns safely with comprehensive path validation."""
    return AccessController.expand_globs(patterns, allowed_dirs)


def is_safe_path(path: object, allowed_dirs: list[Path] | None = None) -> bool:
    """Validate path is safe and within allowed directories."""
    return AccessController.is_safe_path(path, allowed_dirs)


def ensure_parent_dir(path: Path) -> None:
    """Ensure parent directory exists, creating it if necessary."""
    AccessController.ensure_parent_dir(path)


def quote_path(path: Path) -> str:
    """Quote path for safe display in preview text."""
    return AccessController.quote_path(path)


def most_recent_file(paths: Iterable[Path]) -> Path | None:
    """Find the most recently modified file from a collection."""
    return AccessController.most_recent_file(paths)


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename to prevent security issues and filesystem problems."""
    return AccessController.sanitize_filename(filename, max_length)


def validate_ffmpeg_command(cmd: list[str]) -> bool:
    """Validate ffmpeg command arguments for security."""
    return AccessController.validate_ffmpeg_command(cmd)


def sanitize_user_input(user_input: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    return AccessController.sanitize_user_input(user_input, max_length)


# Export the allowed FFmpeg flags for external use
ALLOWED_FFMPEG_FLAGS = AccessController._ALLOWED_FFMPEG_FLAGS
