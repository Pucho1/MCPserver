# validar -> insertar -> gestionar errores -> devolver resultado

class NotesService:

    def __init__(self, db_conn):
        self.db_conn = db_conn


    async def create_note(
        self,
        content: str
    ):

        # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
        cursor = await self.db_conn.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,)
        )

        # guardo los cambios en la base de datos
        await self.db_conn.commit()

        return cursor
 

    async def get_single_note(
        self,
        note_id: int
    ) -> dict:

        # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
        cursor = await self.db_conn.execute(
            "SELECT * FROM notes WHERE id = ?",
            (note_id,)
        )

        # obtengo la fila resultante
        row = await cursor.fetchone()

        if row is None:
            raise ValueError(f"No se encontró ninguna nota con id {note_id}")

        return {"id": row[0], "content": row[1]}
