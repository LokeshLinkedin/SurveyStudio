from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, List
from pydantic import BaseModel
import os

from backend.parser_service import smart_block_parser
from backend.xml_generator import generate_xml

# =============================
# 🚀 APP INIT
# =============================
app = FastAPI()

# =============================
# 🔐 CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        return {"error": str(e), "questions": []}

# =============================
# 🔹 GENERATE API (NO AUTH)
# =============================
@app.post("/generate")
async def generate(payload: List[Dict]):
    try:
        if not payload:
            return {"error": "Empty payload", "xml": ""}

        xml = generate_xml(payload)
        return {"xml": xml}

    except Exception as e:
        return {"error": str(e), "xml": ""}

# =============================
# 🌐 FRONTEND PATH
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_PATH = os.path.abspath("frontend/dist")

# =============================
# 🌐 ROOT
# =============================
@app.get("/")
def serve_root():
    return FileResponse(os.path.join(FRONTEND_PATH, "index.html"))

# =============================
# 🌐 STATIC FILES
# =============================
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(FRONTEND_PATH, "assets")),
    name="assets"
)