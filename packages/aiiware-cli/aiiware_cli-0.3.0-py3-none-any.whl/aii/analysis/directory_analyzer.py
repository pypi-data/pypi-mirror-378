"""Directory analysis and structure scanning for AI analysis."""

from pathlib import Path
from typing import Any


class DirectoryAnalyzer:
    """Analyzes directory structures and generates summaries for AI analysis."""

    def __init__(self) -> None:
        self.ignore_patterns = {
            ".git",
            ".svn",
            ".hg",  # VCS directories
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",  # Python cache
            "node_modules",
            ".npm",  # Node.js
            ".venv",
            "venv",
            "env",  # Python virtual environments
            "dist",
            "build",
            "target",  # Build directories
            ".DS_Store",
            "Thumbs.db",  # OS files
            ".env",
            ".env.local",  # Environment files
        }

    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        path_str = str(path)
        path_name = path.name

        # Check if any part of the path matches ignore patterns
        for pattern in self.ignore_patterns:
            # Exact match of directory/file name
            if path_name == pattern:
                return True
            # Pattern appears as a full path component (e.g., path/pattern/file)
            if f"/{pattern}/" in path_str or path_str.endswith(f"/{pattern}"):
                return True
            # For the specific case of checking if the path starts with pattern (like .git)
            if path_str.startswith(pattern + "/") or path_str == pattern:
                return True
        return False

    def scan_directory(
        self, directory_path: str | Path, max_depth: int = 3
    ) -> dict[str, Any]:
        """Scan directory and return structure information."""
        directory_path = Path(directory_path).resolve()

        if not directory_path.exists():
            return {"error": f"Directory does not exist: {directory_path}"}

        if not directory_path.is_dir():
            return {"error": f"Path is not a directory: {directory_path}"}

        structure = {
            "path": str(directory_path),
            "name": directory_path.name,
            "files": [],
            "directories": [],
            "file_counts": {},
            "total_files": 0,
            "total_directories": 0,
        }

        try:
            self._scan_recursive(directory_path, structure, 0, max_depth)
        except PermissionError:
            structure["error"] = f"Permission denied accessing: {directory_path}"
        except Exception as e:
            structure["error"] = f"Error scanning directory: {str(e)}"

        return structure

    def _scan_recursive(
        self, path: Path, structure: dict, current_depth: int, max_depth: int
    ) -> None:
        """Recursively scan directory structure."""
        if current_depth >= max_depth:
            return

        for item in sorted(path.iterdir()):
            if self.should_ignore(item):
                continue

            relative_path = item.relative_to(Path(structure["path"]))

            if item.is_file():
                file_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "size": item.stat().st_size,
                    "extension": item.suffix.lower(),
                }
                structure["files"].append(file_info)
                structure["total_files"] += 1

                # Count file types
                ext = item.suffix.lower() or "no_extension"
                structure["file_counts"][ext] = structure["file_counts"].get(ext, 0) + 1

            elif item.is_dir():
                dir_info = {
                    "name": item.name,
                    "path": str(relative_path),
                    "depth": current_depth + 1,
                }
                structure["directories"].append(dir_info)
                structure["total_directories"] += 1

                # Recursively scan subdirectory
                self._scan_recursive(item, structure, current_depth + 1, max_depth)

    def generate_summary(self, structure: dict) -> str:
        """Generate a text summary of the directory structure for AI analysis."""
        if "error" in structure:
            return f"Error: {structure['error']}"

        lines = []
        lines.append(f"📁 Directory Analysis: {structure['name']}")
        lines.append(f"📍 Path: {structure['path']}")
        lines.append("")

        # Summary statistics
        lines.append("📊 Summary Statistics:")
        lines.append(f"  • Total files: {structure['total_files']}")
        lines.append(f"  • Total directories: {structure['total_directories']}")
        lines.append("")

        # File type breakdown
        if structure["file_counts"]:
            lines.append("📄 File Types:")
            for ext, count in sorted(
                structure["file_counts"].items(), key=lambda x: x[1], reverse=True
            ):
                ext_display = ext if ext != "no_extension" else "(no extension)"
                lines.append(f"  • {ext_display}: {count} files")
            lines.append("")

        # Directory structure (top-level)
        if structure["directories"]:
            lines.append("📂 Directory Structure:")
            for dir_info in structure["directories"][:20]:  # Limit to first 20
                indent = "  " * (dir_info["depth"])
                lines.append(f"{indent}📁 {dir_info['name']}/")
            if len(structure["directories"]) > 20:
                lines.append(
                    f"  ... and {len(structure['directories']) - 20} more directories"
                )
            lines.append("")

        # Key files (common important files)
        important_files = []
        for file_info in structure["files"]:
            name = file_info["name"].lower()
            if name in [
                "readme.md",
                "package.json",
                "requirements.txt",
                "cargo.toml",
                "pom.xml",
                "build.gradle",
                "makefile",
                "dockerfile",
                ".gitignore",
            ]:
                important_files.append(file_info["name"])

        if important_files:
            lines.append("📋 Key Configuration Files:")
            for file in important_files:
                lines.append(f"  • {file}")
            lines.append("")

        return "\n".join(lines)

    def analyze_directory(self, directory_path: str | Path, max_depth: int = 3) -> str:
        """Analyze directory and return formatted summary text."""
        structure = self.scan_directory(directory_path, max_depth)
        return self.generate_summary(structure)
