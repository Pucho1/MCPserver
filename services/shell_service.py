# ----- SHELL ------

@mcp.tool()
async def run_git_status() -> str:
    """
    Run git status command safely and return the output.
    """

    try:

        result = await asyncio.to_thread(
            subprocess.run,
            ["git", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:

            error_message = result.stderr.decode().strip()

            raise Exception(
                f"Error running git status: {error_message}"
            )

        return result.stdout.strip()

    except asyncio.TimeoutError:

        raise TimeoutError(
            "git status command timed out"
        )

    except Exception as e:

        raise Exception(
            f"Unexpected error running git status: {str(e)}"
        )

