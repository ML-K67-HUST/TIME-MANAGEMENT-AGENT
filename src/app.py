
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routers import (
    chat,
)
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


templates = Jinja2Templates(directory="templates")

@app.get("/test-agent", response_class=HTMLResponse)
async def render_test_agent(request: Request):
    return templates.TemplateResponse("test_agent.html", {"request": request})

app.include_router(chat.router)
