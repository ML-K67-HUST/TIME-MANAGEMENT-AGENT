
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routers import (
    chat,
)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




app.include_router(chat.router)
