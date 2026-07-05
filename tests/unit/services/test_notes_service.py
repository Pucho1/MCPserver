from unittest.mock import AsyncMock

import pytest

from services.notes_service import NotesService

@pytest.fixture
def notes_context():
    db_mock     = AsyncMock()
    cursor_mock = AsyncMock()
    service     = NotesService(db_mock)

    return {
        "db_mock": db_mock,
        "cursor_mock": cursor_mock,
        "service": service,
    }


@pytest.mark.asyncio
async def test_get_single_note_returns_note_when_exists(notes_context):

    # Éxito
    # execute() funciona
    # → devuelve la nota solicitada

    # Arrange

    db_mock     = notes_context["db_mock"] # Obtengo el mock que preparé de la conexión a la base de datos
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.fetchone.return_value = (
        1,
        "Hola"
    )

    service = notes_context["service"] # Recupero la instancia de NotesService que usa el mock de la base de datos

    # Act

    result = await service.get_single_note(1)

    # Assert

    assert result == {
        "id": 1,
        "content": "Hola"
    }


@pytest.mark.asyncio
async def test_get_single_note_raises_error_when_not_exists(notes_context):
    
    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.fetchone.return_value = None

    service = notes_context["service"] # Recupero la instancia de NotesService que usa el mock de la base de datos

    # Act & Assert

    with pytest.raises(ValueError, match=r"No se encontró ninguna nota con id 123"):
        await service.get_single_note(123)


@pytest.mark.asyncio
async def test_create_note_returns_lastrowid(notes_context):

    #Arrange
    db_mock     = notes_context["db_mock"] # Obtengo el mock que preparé de la conexión a la base de datos
    cursor_mock = notes_context["cursor_mock"] # Obteno el mock del cursor que se devuelve al ejecutar la consulta

    db_mock.execute.return_value = cursor_mock # Cuando se llama a db_mock.execute, devuelve cursor_mock

    cursor_mock.lastrowid = 1

    #Act
    service = notes_context["service"] # Recupero la instancia de NotesService que usa el mock de la base de datos
    content = "Hola"

    result = await service.create_note(content)

    # Assert
    db_mock.execute.assert_awaited_once_with(
        "INSERT INTO notes (content) VALUES (?)",
        (content,)
    )

    db_mock.commit.assert_awaited_once()


    assert result == 1



@pytest.mark.asyncio
async def test_create_note_when_DB_fails_execution(notes_context):

    # execute() lanza excepción
    # → commit() NO se ejecuta
    # → la excepción se propaga

    #Arrange
    db_mock = notes_context["db_mock"]

    db_mock.execute.side_effect = Exception("Database error")


    #Act
    service = notes_context["service"]
    content = "Hola"

    # Assert
    with pytest.raises(Exception, match=r"Database error"):
        await service.create_note(content)
  
    db_mock.commit.assert_not_awaited() # Aseguro que no se llamó a commit() ya que la inserción falló


@pytest.mark.asyncio
async def test_create_note_when_DB_fails_commit(notes_context):

    # Fallo en commit()
    # execute() funciona
    # commit() lanza excepción
    # → execute() ocurrió correctamente
    # → commit() fue intentado exactamente una vez
    # → la excepción se propaga

    #Arrange
    db_mock     = notes_context["db_mock"] # Preparo un mock de la conexión a la base de datos
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock # Cuando se llama a db_mock.execute, devuelve cursor_mock
    db_mock.commit.side_effect = Exception("Commit error")

    #Act
    service = notes_context["service"] # Recupero la instancia de NotesService que usa el mock de la base de datos
    content = "Hola" # Preparo la data para ejecutar la función create_note

    # Assert
    with pytest.raises(Exception, match=r"Commit error"): # Aseguro que se lanza la excepción esperada cuando falla el commit
        await service.create_note(content) # ejecuto el metodo create_note con la data preparada

    db_mock.commit.assert_awaited_once()

    db_mock.execute.assert_awaited_once_with(
        "INSERT INTO notes (content) VALUES (?)",
        (content,)
    ) # Aseguro que se llamó a execute() con los parámetros correctos


@pytest.mark.asyncio
async def test_get_all_notes_returns_all_notes_when_exist(notes_context):

    # Éxito
    # execute() funciona
    # fetchall() devuelve múltiples notas
    # → devuelve todas las notas

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.fetchall.return_value = [
        (1, "Primera nota"),
        (2, "Segunda nota"),
        (3, "Tercera nota")
    ]

    service = notes_context["service"]

    # Act

    result = await service.get_all_notes()

    # Assert

    assert result == {
        "notes": [
            {"id": 1, "content": "Primera nota"},
            {"id": 2, "content": "Segunda nota"},
            {"id": 3, "content": "Tercera nota"}
        ]
    }

    db_mock.execute.assert_awaited_once_with("SELECT * FROM notes")


@pytest.mark.asyncio
async def test_get_all_notes_raises_error_when_no_notes_exist(notes_context):

    # No hay notas
    # fetchall() devuelve lista vacía
    # → lanza ValueError

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.fetchall.return_value = []

    service = notes_context["service"]

    # Act & Assert

    with pytest.raises(ValueError, match=r"No se encontró ninguna nota"):
        await service.get_all_notes()


@pytest.mark.asyncio
async def test_update_note_returns_success_message_when_note_exists(notes_context):

    # Éxito
    # execute() funciona
    # rowcount > 0 (nota encontrada)
    # commit() funciona
    # → devuelve mensaje de éxito

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 1

    service = notes_context["service"]

    note_id = 1
    new_content = "Contenido actualizado"

    # Act

    result = await service.update_note(note_id, new_content)

    # Assert

    assert result == f"Nota {note_id} actualizada correctamente"

    db_mock.commit.assert_awaited_once()

    db_mock.execute.assert_awaited_once()

    _, params = db_mock.execute.await_args.args # contiene la última llamada esperada registrada por el AsyncMock y .args

    assert params == (new_content, note_id) # Aseguro que los parámetros pasados a execute() son correctos


@pytest.mark.asyncio
async def test_update_note_raises_error_when_note_not_exists(notes_context):

    # Nota no existe
    # rowcount == 0
    # → lanza ValueError

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 0

    service = notes_context["service"]

    note_id = 999
    new_content = "Contenido actualizado"

    # Act & Assert

    with pytest.raises(ValueError, match=r"Nota 999 no encontrada"):
        await service.update_note(note_id, new_content)

    db_mock.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_note_when_db_fails_commit(notes_context):

    # execute() funciona
    # commit() lanza excepción
    # → la excepción se propaga

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 1

    db_mock.commit.side_effect = Exception("Commit error")

    service = notes_context["service"]

    note_id = 1
    new_content = "Contenido actualizado"

    # Act & Assert

    with pytest.raises(Exception, match=r"Commit error"):
        await service.update_note(note_id, new_content)

    db_mock.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_note_returns_success_message_when_note_exists(notes_context):

    # Éxito
    # execute() funciona
    # rowcount > 0 (nota encontrada)
    # commit() funciona
    # → devuelve mensaje de éxito

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 1

    service = notes_context["service"]

    note_id = 1

    # Act

    result = await service.delete_note(note_id)

    # Assert

    assert result == f"Nota {note_id} eliminada correctamente"

    db_mock.commit.assert_awaited_once()

    db_mock.execute.assert_awaited_once_with(
        "DELETE FROM notes WHERE id=?",
        (note_id,)
    )


@pytest.mark.asyncio
async def test_delete_note_raises_error_when_note_not_exists(notes_context):

    # Nota no existe
    # rowcount == 0
    # → lanza ValueError

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 0

    service = notes_context["service"]

    note_id = 999

    # Act & Assert

    with pytest.raises(ValueError, match=r"Nota 999 no encontrada"):
        await service.delete_note(note_id)

    db_mock.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_note_when_db_fails_commit(notes_context):

    # execute() funciona
    # commit() lanza excepción
    # → la excepción se propaga

    # Arrange

    db_mock = notes_context["db_mock"]
    cursor_mock = notes_context["cursor_mock"]

    db_mock.execute.return_value = cursor_mock

    cursor_mock.rowcount = 1

    db_mock.commit.side_effect = Exception("Commit error")

    service = notes_context["service"]

    note_id = 1

    # Act & Assert

    with pytest.raises(Exception, match=r"Commit error"):
        await service.delete_note(note_id)

    db_mock.commit.assert_awaited_once()
