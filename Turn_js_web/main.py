# 🐍 AutoCrawler/webapp/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import subprocess
import glob
import base64

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

# 정적 파일 서빙
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

@app.get("/crawl")
def crawl(query: str):
    query = query.strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": "빈 키워드"})

    # keywords.txt에 저장
    keyword_path = os.path.join(BASE_DIR, "keywords.txt")
    print("[DEBUG] keyword_path:", keyword_path)

    with open(keyword_path, "w", encoding="utf-8") as f:
        f.write(query)

    # AutoCrawler 실행
    try:
        subprocess.run([
            "python3", "main.py",
            "--skip", "false",
            "--limit", "5",
            "--google", "true",
            "--naver", "true"
        ],
        cwd=os.path.join(BASE_DIR),
        check=True)
    except subprocess.CalledProcessError:
        return JSONResponse(status_code=500, content={"error": "크롤링 실패"})

    # 이미지 경로 탐색
    folder = os.path.join("..", "download", query)
    files = sorted(glob.glob(os.path.join(folder, "*.jpg")))[:5]

    if not files:
        return JSONResponse(status_code=404, content={"error": "이미지 없음"})

    # base64로 인코딩해서 전달
    images = []
    for path in files:
        with open(path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            images.append(f"data:image/jpeg;base64,{encoded}")

    return {"images": images}
