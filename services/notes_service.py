# validar -> insertar -> gestionar errores -> devolver resultado

class NotesService:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    # cada una de las funciones de este servicio se encargará de una tarea 
    # concreta, en este caso de gestionar las notas en la base de datos, 
    # cada función se encargará de una tarea concreta, como crear una nota, 
    # obtener una nota, actualizar una nota o eliminar una nota.

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

        # el lastrowid es un atributo del cursor que devuelve el id de la 
        # ultima fila insertada en la base de datos, en este caso el id de la nota que acabamos de crear.
        return cursor.lastrowid
 

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


    async def get_all_notes(self) -> dict:
        
        # hago la consulta a la base de datos de forma asíncrona usando aiosqlite
        cursor = await self.db_conn.execute(
            "SELECT * FROM notes"
        )

        rows = await cursor.fetchall()

        if not rows:
            raise ValueError("No se encontró ninguna nota")

        return {"notes": [{"id": row[0], "content": row[1]} for row in rows]}


    async def update_note(
        self,
        note_id: int,
        new_content: str
    ) -> str:

        cursor  = await self.db_conn.execute(
            """
                UPDATE notes
                SET
                content=?,
                updated_at=
                datetime(
                    'now',
                    'localtime'
                )
                WHERE id=?
            """,
            (new_content, note_id)
        )


        if cursor.rowcount == 0:
            raise ValueError(
                f"Nota {note_id} no encontrada"
            )
        
        await self.db_conn.commit()

        return f"Nota {note_id} actualizada correctamente"
    

    async def delete_note(
        self,
        note_id: int
    ) -> str:

        cursor = await self.db_conn.execute(
            "DELETE FROM notes WHERE id=?",
            (note_id,)
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"Nota {note_id} no encontrada"
            )
        
        await self.db_conn.commit()

        return f"Nota {note_id} eliminada correctamente"