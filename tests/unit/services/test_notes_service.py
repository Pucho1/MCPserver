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
    # commit() funciona
    # → devuelve lastrowid

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
async def test_get_single_note_returns_none_when_not_exists(notes_context):
    
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
    service = NotesService(db_mock)
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
