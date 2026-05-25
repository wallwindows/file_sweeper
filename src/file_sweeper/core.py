"""Core functionality for file sweeper."""

import click
from pathlib import Path


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
