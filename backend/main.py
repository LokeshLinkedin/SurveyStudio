from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, List
from pydantic import BaseModel
import os

from backend.parser_service import smart_block_parser
from backend.xml_generator import generate_xml

# =============================
# 🚀 APP INIT
# =============================
app = FastAPI(title="SurveyStudio API")


# =============================
# 🔐 CORS (safe for Darwin)
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
# 📦 PATH SETUP (robust)
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend/dist"))
ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")


# =============================
# 🔹 REQUEST MODEL
# =============================
class TextRequest(BaseModel):
    text: str


# =============================
# 🔹 PREVIEW API
# =============================
@app.post("/preview")
async def preview(req: TextRequest):
    try:
        questions = smart_block_parser(req.text)
        return {"questions": questions}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "questions": []}
        )


# =============================
# 🔹 GENERATE XML API
# =============================
@app.post("/generate")
async def generate(payload: List[Dict]):
    try:
        if not payload:
            raise Exception("Empty payload")

        xml = generate_xml(payload)
        return {"xml": xml}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "xml": ""}
        )


# =============================
# 🌐 STATIC FILES (React build)
# =============================
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
else:
    print("⚠️ WARNING: assets folder not found:", ASSETS_DIR)


# =============================
# 🌐 FAVICON
# =============================
@app.get("/favicon.svg")
def favicon():
    path = os.path.join(FRONTEND_DIR, "favicon.svg")
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"error": "favicon not found"})


# =============================
# 🌐 HEALTH CHECK (IMPORTANT)
# =============================
@app.get("/health")
def health():
    return {"status": "ok"}


# =============================
# 🌐 REACT ROUTING (CATCH ALL)
# =============================
@app.get("/{full_path:path}")
def serve_react(full_path: str):
    index_file = os.path.join(FRONTEND_DIR, "index.html")

    if not os.path.exists(index_file):
        return JSONResponse(
            status_code=500,
            content={"error": "Frontend build not found"}
        )

    return FileResponse(index_file)