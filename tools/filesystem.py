from pathlib import Path

from mcp_instance import mcp

from schemas.write_file import (
    WriteFileRequest
)

# ----- TOOLS ------

@mcp.tool()
async def list_files(path: str = ".") -> list[str]:
    # De aqui sale la descripcion de la tool
    """
    List files in a directory. 
    """

    import os

    return os.listdir(path)

@mcp.tool()
async def read_file(path: str) -> str:
    """
    Read a file content.
    """

    from pathlib import Path

    return Path(path).read_text(
        encoding="utf-8"
    )


@mcp.tool()
async def write_file(
    request: WriteFileRequest
):

    try:

        file_path = Path(
            request.path
        )

        if (
            file_path.exists()
            and
            not request.overwrite
        ):

            raise FileExistsError(
                "File already exists"
            )

        file_path.write_text(
            request.content,
            encoding="utf-8"
        )

        return "ok"

    except PermissionError:

        raise PermissionError(
            "Permission denied"
        )

    except FileNotFoundError:

        raise FileNotFoundError(
            "Directory does not exist"
        )


@mcp.tool()
async def create_directory(
    path: str
) -> str:
    """
    Create directory.
    """

    from pathlib import Path

    Path(path).mkdir(
        parents=True,
        exist_ok=True
    )

    return "Directory created"


