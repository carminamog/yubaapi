from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
import openai
import graphviz

# 🔐 Clave de API de OpenAI
openai.api_key = "OPENAI_API_KEY"

app = FastAPI()

class TextInput(BaseModel):
    text: str

def texto_a_mapa_mental(texto: str, filename="mapa_mental"):
    dot = graphviz.Digraph(format='png')
    lines = texto.strip().split('\n')

    node_stack = []
    indent_stack = []

    for line in lines:
        indent = len(line) - len(line.lstrip(' '))
        content = line.strip('- ').strip()

        node_id = str(len(dot.body))  # ID único

        dot.node(node_id, content)

        while indent_stack and indent_stack[-1] >= indent:
            node_stack.pop()
            indent_stack.pop()

        if node_stack:
            dot.edge(node_stack[-1], node_id)

        node_stack.append(node_id)
        indent_stack.append(indent)

    output_path = dot.render(filename, cleanup=True)
    return output_path

@app.post("/generate-image")
async def generar_imagen(data: TextInput):
    prompt = f"""
    Resume y organiza el siguiente texto como un mapa mental jerárquico, en formato de lista tipo esquema:

    \"\"\"{data.text}\"\"\"

    Usa guiones y sangrías para los niveles.
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    estructura = response["choices"][0]["message"]["content"]

    path = texto_a_mapa_mental(estructura)
    return FileResponse(path, media_type="image/png", filename="mapa_mental.png")
