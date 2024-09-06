from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import json
from time import sleep

from services import NaverAPI, CompletionExecutor, scale_down_coordinates


from services import NaverAPI, CompletionExecutor, scale_down_coordinates
from utils import (
    process_search_results, 
    extract_item_data, 
    process_blog_result, 
    get_text_summary, 
    process_blog_posts, 
    get_text_summary_with_params,
    NAVER_CLIENT_ID,
    NAVER_CLIENT_SECRET,
    CLOVA_HOST,
    CLOVA_API_KEY,
    CLOVA_API_KEY_PRIMARY,
    CLOVA_REQUEST_ID
)

router = APIRouter()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "summary": None})

@app.get("/recommend", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("request.html", {"request": request, "summary": None})

@app.post("/recommend", response_class=HTMLResponse)
async def search(request: Request, location: str = Form(...), food: str = Form(...)):
    naver = get_naver_api()
    query = f"{location} {food} 맛집"
    result_json = naver.search_local(query, 10, 1)
    result_response = process_search_results(result_json, naver)
    return templates.TemplateResponse("request.html", {"request": request, "summary": result_response})

@app.post("/", response_class=HTMLResponse)
async def search(
    request: Request, 
    query: str = Form(...),
    display: int = Form(3), 
    start: int = Form(1),
    topP: float = Form(0.9), 
    topK: int = Form(50), 
    maxTokens: int = Form(256),
    temperature: float = Form(0.7), 
    repeatPenalty: float = Form(1.0)
):
    naver = get_naver_api()
    cleaned_texts = naver.search_blog_posts(query, display, start)
    summaries = process_blog_posts(cleaned_texts, topP, topK, maxTokens, temperature, repeatPenalty)
    return templates.TemplateResponse("index.html", {"request": request, "summary": json.dumps(summaries)})
