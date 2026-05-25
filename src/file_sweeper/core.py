"""Core functionality for file sweeper."""

import click
from pathlib import Path
from typing import List


class FileOrganizer:
    """Utility class for organizing files by extension."""

    def __init__(self, root_path: Path) -> None:
        """Initialize the FileOrganizer.

        Args:
            root_path: Root directory to scan for files.
        """
        self.root_path = root_path

    def scan(self) -> List[Path]:
        """Scan root_path for all files (excluding subdirectories and hidden files).

        Returns:
            List of file paths.

        Raises:
            FileNotFoundError: If root_path doesn't exist.
            NotADirectoryError: If root_path is not a directory.
        """
        if not self.root_path.exists():
            raise FileNotFoundError(f"Path not found: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.root_path}")

        files = []
        for item in self.root_path.iterdir():
            if item.is_file() and not item.name.startswith("."):
                files.append(item)

        return sorted(files)

    def categorize(self, file_path: Path) -> str:
        """Categorize a file based on its extension.

        Args:
            file_path: The file path to categorize.

        Returns:
            Category name as string.

        Raises:
            FileNotFoundError: If file_path doesn't exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.is_dir():
            raise ValueError(f"Path is a directory: {file_path}")

        extension = file_path.suffix.lower()

        category_map = {
            ".jpg": "Images",
            ".jpeg": "Images",
            ".png": "Images",
            ".gif": "Images",
            ".txt": "Documents",
            ".md": "Documents",
            ".py": "Python",
            ".js": "Python",
            ".cpp": "Python",
            ".java": "Python",
            ".c": "Python",
            ".pyw": "Python",
        }

        return category_map.get(extension, "Others")


class FileSweeper:
    """Utility class for cleaning up files."""

    def __init__(self, paths: list[str], dry_run: bool = False) -> None:
        """Initialize the FileSweeper.

        Args:
            paths: List of file/directory paths to clean.
            dry_run: If True, don't actually delete files.
        """
        self.paths = [Path(p) for p in paths]
        self.dry_run = dry_run

    def clean(self) -> None:
        """Clean up files according to the configured paths."""
        for path in self.paths:
            self._clean_path(path)

    def _clean_path(self, path: Path) -> None:
        """Clean a single path.

        Args:
            path: The path to clean.

        Raises:
            FileNotFoundError: If the path doesn't exist.
            NotADirectoryError: If the path is not a directory.
        """
        if not path.exists():
            raise FileNotFoundError(f"Path not found: {path}")

        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        for file_path in path.iterdir():
            if file_path.is_file():
                self._delete_file(file_path)

    def _delete_file(self, file_path: Path) -> None:
        """Delete a single file.

        Args:
            file_path: The file path to delete.

        Raises:
            OSError: If deletion fails.
        """
        if self.dry_run:
            click.echo(f"[DRY RUN] Would delete: {file_path}")
            return

        file_path.unlink()


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--dry-run", "-n", is_flag=True, help="Don't actually delete files")
def cli(paths: tuple[str, ...], dry_run: bool) -> None:
    """Clean up files in the specified paths.

    Args:
        paths: One or more file/directory paths to clean.
        dry_run: If True, show what would be deleted without deleting.
    """
    if not paths:
        click.echo("Error: No paths specified. Use: python -m file_sweeper <paths...>")
        raise click.Exit(1)

    sweeper = FileSweeper(paths, dry_run)
    sweeper.clean()
    click.echo("Cleanup complete.")


if __name__ == "__main__":
    cli()
