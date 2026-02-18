from fastapi import FastAPI
from dotenv import load_dotenv
from routers.chat_with_history import chat_with_history_router
from routers.transcribe import transcribe_router


load_dotenv()

app = FastAPI(title="Python assistant API", version="0.0.1")

app.include_router(chat_with_history_router)
app.include_router(transcribe_router)