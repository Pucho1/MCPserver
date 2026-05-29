from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import RequestContext
from mcp.types import (
    CreateMessageRequestParams,
    CreateMessageResult,
    TextContent,
    SamplingMessage,
)


import asyncio
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from pprint import pprint
import json
import sys

from server import get_post, update_note

load_dotenv()  # Esto carga las variables del archivo .env antes de arrancar el cliente MCP


anthropic_client = AsyncAnthropic()
model = "claude-sonnet-4-5"

server_params = StdioServerParameters(
    command="uv",
    args=["run", "server.py"],
)


async def chat(input_messages: list[SamplingMessage], max_tokens=4000):
    messages = []
    for msg in input_messages:
        if msg.role == "user" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "user", "content": content})
        elif msg.role == "assistant" and msg.content.type == "text":
            content = (
                msg.content.text
                if hasattr(msg.content, "text")
                else str(msg.content)
            )
            messages.append({"role": "assistant", "content": content})

    response = await anthropic_client.messages.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )

    text = "".join([p.text for p in response.content if p.type == "text"])
    return text


async def sampling_callback(
    context: RequestContext, params: CreateMessageRequestParams
):
    # Call Claude using the Anthropic SDK
    text = await chat(params.messages)

    return CreateMessageResult(
        role="assistant",
        model=model,
        content=TextContent(type="text", text=text),
    )


async def run():
    
    async with stdio_client(server_params, errlog=sys.stdout) as (read, write):

        async with ClientSession(
            read,
            write, 
            sampling_callback=sampling_callback
        ) as session:
            
            # Conectamos e inicializamos el canal IPC con el servidor FastMCP
            await session.initialize()

            print("\n--- Listado de todas mis TOOLS ---\n")
            tools = await session.list_tools()
            pprint(tools.model_dump(), indent=2)


            # print("--- PROBANDO TOOL: read_file ---")
            # files_result = await session.call_tool(
            #     name="read_file",
            #     arguments={"path": "README.md"} # Pasa los argumentos que espera la función en el servidor
            # )
            # # El resultado viene envuelto en una estructura de contenido, extraemos el texto/datos
            # print("Archivos encontrados:")
            # pprint(files_result.content[0].text)

            # print(result.content[0].text)

            


            # print("--- PROBANDO TOOL: get_list_notes ---")
            # result = await session.call_tool(
            #     "get_list_notes",
            #     arguments={}
            # )

            # print(result.content[0].text)   



                    
            print("--- PROBANDO TOOL: run_git_status ---")
            new_result = await session.call_tool(
                "run_git_status",
                arguments={}
            )

            print(new_result.content[0].text)





            
            # print("--- PROBANDO TOOL: delete_note ---")
            # new_result = await session.call_tool(
            #     "delete_note",
            #     arguments={"note_id": 3}
            # )

            # print(new_result.content[0].text)



            # print("--- PROBANDO TOOL: update_note ---")
            # new_result = await session.call_tool(
            #     "update_note",
            #     arguments={"note_id": 1, "new_content": "Este es el nuevo contenido de la nota."}
            # )

            # print(new_result.content[0].text)


            # print("--- PROBANDO TOOL: get_single_note ---")
            # new_result = await session.call_tool(
            #     "get_single_note",
            #     arguments={"note_id": 1}
            # )

            # print(new_result.content[0].text)




            # print("--- PROBANDO TOOL: create_note ---")
            # result = await session.call_tool(
            #     "create_note",
            #     arguments={
            #         "content": "Esta es una nueva nota."
            #     }
            # )

            # print(result.content[0].text)

            # print("--- PROBANDO TOOL: get_post ---")
            # result = await session.call_tool(
            #     "get_post",
            #     arguments={
            #         "post_id": 12
            #     }
            # )

            # print(result.content[0].text)





            # print("\n--- Listado de todos mis resources    ---\n")
            # resources = await session.list_resources()
            # pprint(resources.model_dump(), indent=2)

            # print("\n--- Datos de mi resource ---\n")
            # resource = await session.read_resource("filesystem://cwd")
            # pprint(resource.model_dump(), indent=2)


            # print("\n--- Listado de todos mis prompts ---\n")
            # prompts = await session.list_prompts()
            # pprint(prompts.model_dump(), indent=2)

            # print("\n--- Texto de mi prompt ---\n")
            # propmt = await session.get_prompt('summarize_file', arguments={"filename": "notes.txt"})
            # pprint(propmt.model_dump(), indent=2)

            
            # print("--- PROBANDO TOOL: write_file ---")
            # result = await session.call_tool(
            #     "write_file",
            #     arguments={
            #         "path": "notes.txt",
            #         "content": "Hola MCP"
            #     }
            # )
 


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())



#    print("\n--- PROBANDO TOOL: summarize (con arquitectura Sampling inversa) ---")

#     # Llamamos a la herramienta que le pedirá al cliente que "piense"
#     summary_result = await session.call_tool(
#         name="summarize",
#         arguments={"text_to_summarize": "El protocolo MCP (Model Context Protocol) es "
#             "una especificación abierta diseñada por Anthropic para estandarizar la forma en que"
#             " las aplicaciones conectan con fuentes de datos y herramientas de desarrollo de manera segura y eficiente."
#         }
#     )

#     print("Resultado del resumen devuelto por el servidor:")
#     print(summary_result.content[0].text)
