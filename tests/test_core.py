import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import tempfile
import shutil
from pathlib import Path

from file_sweeper.core import FileOrganizer


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def test_files(temp_dir):
    """Create test files in the temporary directory."""
    files = []
    # Regular files
    files.append(temp_dir / "image1.jpg")
    files.append(temp_dir / "image2.png")
    files.append(temp_dir / "image3.gif")
    files.append(temp_dir / "document1.txt")
    files.append(temp_dir / "readme.md")
    files.append(temp_dir / "script.py")
    files.append(temp_dir / "unknown_file.xyz")

    # Hidden files (should be excluded)
    files.append(temp_dir / ".hidden_file")
    files.append(temp_dir / ".gitignore")

    # Subdirectory with files (should be excluded)
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    files.append(subdir / "sub_file.txt")

    for file_path in files:
        file_path.touch()

    return files


def test_file_organizer_init(temp_dir):
    """Test FileOrganizer initialization."""
    organizer = FileOrganizer(temp_dir)
    assert organizer.root_path == temp_dir


def test_file_organizer_scan(temp_dir, test_files):
    """Test scan returns all files excluding subdirectories and hidden files."""
    organizer = FileOrganizer(temp_dir)
    files = organizer.scan()

    # Should only include regular files (7 files)
    assert len(files) == 7

    # All scanned files should be in the test_files list
    scanned_names = {f.name for f in files}
    expected_names = {
        "image1.jpg",
        "image2.png",
        "image3.gif",
        "document1.txt",
        "readme.md",
        "script.py",
        "unknown_file.xyz",
    }
    assert scanned_names == expected_names


def test_file_organizer_scan_nonexistent_path():
    """Test that FileNotFoundError is raised for nonexistent paths."""
    organizer = FileOrganizer(Path("nonexistent_path"))
    with pytest.raises(FileNotFoundError):
        organizer.scan()


def test_file_organizer_scan_not_directory(temp_dir, test_files):
    """Test that NotADirectoryError is raised for file paths."""
    file_path = test_files[0]
    organizer = FileOrganizer(file_path)
    with pytest.raises(NotADirectoryError):
        organizer.scan()


def test_file_organizer_categorize_images(temp_dir):
    """Test categorization for image files."""
    organizer = FileOrganizer(temp_dir)

    # Create test files
    (temp_dir / "test1.jpg").touch()
    (temp_dir / "test2.jpeg").touch()
    (temp_dir / "test3.png").touch()
    (temp_dir / "test4.gif").touch()

    files = [
        (temp_dir / "test1.jpg", "Images"),
        (temp_dir / "test2.jpeg", "Images"),
        (temp_dir / "test3.png", "Images"),
        (temp_dir / "test4.gif", "Images"),
    ]

    for file_path, expected_category in files:
        category = organizer.categorize(file_path)
        assert category == expected_category


def test_file_organizer_categorize_documents(temp_dir):
    """Test categorization for document files."""
    organizer = FileOrganizer(temp_dir)

    # Create test files
    (temp_dir / "note.txt").touch()
    (temp_dir / "README.md").touch()

    files = [
        (temp_dir / "note.txt", "Documents"),
        (temp_dir / "README.md", "Documents"),
    ]

    for file_path, expected_category in files:
        category = organizer.categorize(file_path)
        assert category == expected_category


def test_file_organizer_categorize_python(temp_dir):
    """Test categorization for Python files."""
    organizer = FileOrganizer(temp_dir)

    # Create test files
    (temp_dir / "script.py").touch()
    (temp_dir / "main.pyw").touch()

    files = [
        (temp_dir / "script.py", "Python"),
        (temp_dir / "main.pyw", "Python"),
    ]

    for file_path, expected_category in files:
        category = organizer.categorize(file_path)
        assert category == expected_category


def test_file_organizer_categorize_others(temp_dir):
    """Test categorization for unknown file types."""
    organizer = FileOrganizer(temp_dir)

    # Create test files
    (temp_dir / "file1.dat").touch()
    (temp_dir / "file2.zip").touch()
    (temp_dir / "file3.doc").touch()

    files = [
        (temp_dir / "file1.dat", "Others"),
        (temp_dir / "file2.zip", "Others"),
        (temp_dir / "file3.doc", "Others"),
    ]

    for file_path, expected_category in files:
        category = organizer.categorize(file_path)
        assert category == expected_category


def test_file_organizer_categorize_case_insensitive(temp_dir):
    """Test that categorization is case insensitive."""
    organizer = FileOrganizer(temp_dir)

    # Create test files
    (temp_dir / "test.JPG").touch()
    (temp_dir / "test.PNG").touch()
    (temp_dir / "test.GIF").touch()
    (temp_dir / "test.txt").touch()
    (temp_dir / "test.PY").touch()

    files = [
        (temp_dir / "test.JPG", "Images"),
        (temp_dir / "test.PNG", "Images"),
        (temp_dir / "test.GIF", "Images"),
        (temp_dir / "test.txt", "Documents"),
        (temp_dir / "test.PY", "Python"),
    ]

    for file_path, expected_category in files:
        category = organizer.categorize(file_path)
        assert category == expected_category


def test_file_organizer_categorize_nonexistent_file():
    """Test that FileNotFoundError is raised for nonexistent files."""
    organizer = FileOrganizer(Path("nonexistent_path"))
    with pytest.raises(FileNotFoundError):
        organizer.categorize(Path("test.txt"))
