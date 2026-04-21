from dotenv import load_dotenv
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from concurrent.futures import ThreadPoolExecutor
import asyncio

from crew import generate_exam_section

load_dotenv()

app = FastAPI(title="UNEB Exam Generator")
templates = Jinja2Templates(directory="templates")

# CrewAI is synchronous — run it in a thread pool so FastAPI stays non-blocking
executor = ThreadPoolExecutor(max_workers=4)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
    request,
    "index.html"
)


@app.post("/generate")
async def generate(
    subject: str = Form(...),
    topic: str = Form(...),
    level: str = Form(...),
    num_questions: int = Form(...),
):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            generate_exam_section,
            subject, topic, level, num_questions,
        )
        return JSONResponse({"result": result})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)