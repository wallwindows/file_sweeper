"""Core functionality for file sweeper."""

from pathlib import Path
from typing import List, Dict, Any
import click


class FileOrganizer:
    """Utility class for organizing files by extension."""

    def __init__(self, root_path: Path) -> None:
        """Initialize the FileOrganizer.

        Args:
            root_path: Root directory to scan for files.
        """
        self.root_path = root_path
        self.last_operation: List[Dict[str, Any]] = []

    def scan(self) -> List[Path]:
        """Scan root_path for all files (excluding hidden files).

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

    def organize(self, dry_run: bool = False) -> List[Dict[str, Any]]:
        """Organize files by moving them to category subdirectories.

        Args:
            dry_run: If True, don't actually move files.

        Returns:
            List of operation records.

        Raises:
            FileNotFoundError: If root_path doesn't exist.
            NotADirectoryError: If root_path is not a directory.
        """
        if not self.root_path.exists():
            raise FileNotFoundError(f"Path not found: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.root_path}")

        files = self.scan()
        records: List[Dict[str, Any]] = []

        for file in files:
            category = self.categorize(file)
            dst_dir = self.root_path / category

            # If category directory exists, move to category/category
            if dst_dir.exists():
                dst_dir = dst_dir / category
            dst_dir.mkdir(exist_ok=True)

            dst_path = dst_dir / file.name

            record = {
                "src": str(file),
                "dst": str(dst_path),
                "category": category,
            }

            if not dry_run:
                try:
                    if not dst_path.exists():
                        file.rename(dst_path)
                except Exception as e:
                    print(f"Error moving {file} to {dst_path}: {e}")
                    raise

            records.append(record)

        # Also scan subdirectories for files that may have been missed
        subdirs = [d for d in self.root_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
        for subdir in subdirs:
            for item in subdir.rglob("*"):
                if item.is_file() and not item.name.startswith("."):
                    category = self.categorize(item)
                    dst_dir = self.root_path / category

                    # If category directory exists, move to category/category
                    if dst_dir.exists():
                        dst_dir = dst_dir / category
                    dst_dir.mkdir(exist_ok=True)

                    dst_path = dst_dir / item.name

                    record = {
                        "src": str(item),
                        "dst": str(dst_path),
                        "category": category,
                    }

                    if not dry_run:
                        item.rename(dst_path)

                    records.append(record)

        self.last_operation = records
        return records

    def undo_last(self) -> bool:
        """Undo the last organize operation by moving files back to their original locations.

        Returns:
            True if undo was successful, False if no operations to undo.
        """
        if not self.last_operation:
            return False

        # Make a copy of last_operation since we'll be modifying it
        ops = list(self.last_operation)
        self.last_operation.clear()

        # Collect all dst paths that exist
        existing_dsts = [Path(op["dst"]) for op in ops if Path(op["dst"]).exists()]

        if not existing_dsts:
            return False

        # Move files up multiple levels to root
        # Files from root->subdir should go subdir->root
        # Files from root->subdir->subsubdir should go subsubdir->subdir
        for dst in reversed(existing_dsts):
            # Get the current location of the file/directory
            current = Path(dst)
            # Move up until we reach or pass root
            while True:
                parent = current.parent
                if parent == self.root_path:
                    # At root level, move to root
                    if current.is_file():
                        target = self.root_path / current.name
                        if target != current:
                            current.rename(target)
                    elif current.is_dir():
                        for item in current.iterdir():
                            target = self.root_path / item.name
                            if target != item:
                                item.rename(target)
                    break
                else:
                    # Move up one level
                    if current.is_dir():
                        for item in current.iterdir():
                            target = parent / item.name
                            if target != item:
                                item.rename(target)
                    else:
                        target = parent / current.name
                        if target != current:
                            current.rename(target)
                    current = parent

        return True


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
