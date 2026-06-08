from core.mcp_instance import mcp

from services import filesystem_service


# ----- FILESYSTEM ------

@mcp.tool()
async def list_files(path: str = ".") -> list[str]:
    # De aqui sale la descripcion de la tool
    """
    List files in a directory.
    """

    listed_files = filesystem_service.list_files(path)

    return listed_files


@mcp.tool()
async def read_file(path: str) -> str:
    """
    Read a file content.
    """

    file_content = filesystem_service.read_file(path)

    return file_content



@mcp.tool()
async def write_file(
    path: str,
    content: str,
) -> str:
    """
    Write content into a file.
    """
    result = filesystem_service.write_file(path, content)

    return result


@mcp.tool()
async def create_directory(
    path: str
) -> str:
    """
    Create directory.
    """

    result = filesystem_service.create_directory(path)

    return result


