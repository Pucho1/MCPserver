from fastmcp import Context
from core.mcp_instance import mcp

# ----- SQLITE ------

@mcp.tool()
async def create_note(content: str, context: Context,) -> str:
    """
    Create a note in the database.
    """

    notes_service = context.lifespan_context["notes_service"]


    services_result = await notes_service.create_note(content)

    
    return f"Nota creada con id {services_result}"


@mcp.tool()
async def get_single_note(
    note_id:int,
    context:Context,
) -> dict:
    """
    Fetch a note from the database.
    """

    # accedo a la conexion de la base de datos que cree en el lifespan a traves del context.lifespan_context 
    # y lo guardo en una variable para usarlo en esta funcion
    notes_service = context.lifespan_context["notes_service"]

    data_of_note = await notes_service.get_single_note(note_id)

    return data_of_note


@mcp.tool()
async def get_list_notes(context:Context,) -> dict:
    """
    Fetch all notes from the database.
    """

    notes_service = context.lifespan_context["notes_service"]

    all_notes = await notes_service.get_all_notes()

    return all_notes


@mcp.tool()
async def update_note(
    note_id: int,
    new_content: str,
    context: Context,
) -> str:
    
    """
    Update a note in the database.
    """
    notes_service = context.lifespan_context["notes_service"]

    note_updated = await notes_service.update_note(note_id, new_content)

    return note_updated


@mcp.tool()
async def delete_note(
    note_id: int,
    context: Context,
) -> str:
    """
    Delete a note from the database.
    """
    notes_service = context.lifespan_context["notes_service"]

    note_deleted = await notes_service.delete_note(note_id)

    return note_deleted
