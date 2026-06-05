# validar -> insertar -> gestionar errores -> devolver resultado

class NotesService:

    def __init__(self, db_conn):
        self.db_conn = db_conn


    async def create_note(
        self,
        content: str
    ) -> int:

        # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
        cursor = await self.db_conn.execute(
            "INSERT INTO notes (content) VALUES (?)",
            (content,)
        )

        # guardo los cambios en la base de datos
        await self.db_conn.commit()

        return cursor.lastrowid
 
