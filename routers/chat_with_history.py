from typing import List, Union
from fastapi import APIRouter
import mlflow
from pydantic import BaseModel
from features.rag_generation.rag_generation import (
    chat_openai_with_history, generation_main_workflow, start_openai_client
)
from features.monitoring.mlflow_setup import setup_mlflow


setup_mlflow()

chat_with_history_router = APIRouter()

class Message(BaseModel):
    role: str
    content: Union[str, list]


class ChatHistoryInput(BaseModel):
    chat_history: List[Message]


class ChatResponse(BaseModel):
    response: str


def get_user_query(historical_messages):
    user_content = historical_messages[-1].content
    if historical_messages[-1].role == "user":
        if isinstance(user_content, str):
            user_query = user_content
        elif isinstance(user_content, list):
            user_query = user_content[0]["text"]
    else:
        raise ValueError("Last message in history must be from the user")
    return user_query


@chat_with_history_router.post("/chat_with_history")
def chat_with_history(request: ChatHistoryInput) -> ChatResponse:
    system_prompt = """
    Eres un experto útil en Python. Responde la pregunta del usuario sobre programación en Python de la manera más precisa y concisa posible, utilizando solo tu propio conocimiento. Si no estás seguro de una respuesta, dilo claramente.

    Las preguntas son en español y pueden llegar procesadas por el modelo vosk vosk-model-small-es-0.42 y KaldiRecognizer, por lo que no entenderá "Python".
    Errores comunes detectados como Python: país son, faisán,...
    """
    user_query = get_user_query(request.chat_history)
    history_as_dicts = [m.model_dump() for m in request.chat_history]
    
    with mlflow.start_run(run_name="chat_with_history"):
        mlflow.log_param("endpoint", "/chat_with_history")
        mlflow.log_param("user_query_len", len(user_query) if user_query else 0)
        mlflow.log_param("chat_history_len", len(request.chat_history))

        if not user_query:
            print("---- Chat directly ----")
            openai_client = start_openai_client()
            
            chat_response = chat_openai_with_history(openai_client, history_as_dicts, system_prompt)
        else:
            host = "http://localhost:5080"
            index_name = "dense-index"
            print("---- RAG ----")
            chat_response = generation_main_workflow(user_query, host, index_name, history_as_dicts, system_prompt)

    return ChatResponse(response=chat_response)
