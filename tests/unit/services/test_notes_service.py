from unittest.mock import AsyncMock

import pytest

from services.notes_service import NotesService


@pytest.mark.asyncio
async def test_get_single_note_returns_note_when_exists():

    # Arrange

    db_mock = AsyncMock()
    cursor_mock = AsyncMock()

    db_mock.execute.return_value = cursor_mock

    cursor_mock.fetchone.return_value = (
        1,
        "Hola"
    )

    service = NotesService(db_mock)

    # Act

    result = await service.get_single_note(1)

    # Assert

    assert result == {
        "id": 1,
        "content": "Hola"
    }