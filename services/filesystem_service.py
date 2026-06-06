import os
from pathlib import Path


def list_files(path: str = ".") -> list[str]:
    """
    List files in a directory.
    """

    return os.listdir(path)


def read_file(path: str) -> str:
    """
    Read a file content.
    """
    if not Path(path).exists():
        return "File not found"

    file_content = Path(path).read_text(
        encoding="utf-8"
    )

    return file_content

    
    

def write_file(path: str, content: str) -> str:
    """
    Write content into a file.
    """
    Path(path).write_text(
        content,
        encoding="utf-8"
    )
    return "File written"

def create_directory(path: str) -> str:
    """
    Create directory.
    """
    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )
    return "Directory created"