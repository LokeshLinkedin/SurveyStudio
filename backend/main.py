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
# 🔹 APP INIT
# =============================
app = FastAPI()

# =============================
# 🔐 CORS (Darwin friendly)
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# 🔹 REQUEST MODELS
# =============================
class TextRequest(BaseModel):
    text: str


# =============================
# 🔹 PREVIEW
# =============================
@app.post("/preview")
async def preview(req: TextRequest):
    try:
        questions = smart_block_parser(req.text)
        return {"questions": questions}
    except Exception as e:
        return {"error": str(e), "questions": []}


# =============================
# 🔓 GENERATE (NO AUTH)
# =============================
@app.post("/generate")
async def generate(payload: List[Dict]):
    try:
        if not payload:
            raise Exception("Empty payload")

        xml = generate_xml(payload)

        return {
            "xml": xml
        }

    except Exception as e:
        return {"error": str(e), "xml": ""}


# =============================
# 🌐 FRONTEND SERVING
# =============================
frontend_path = os.path.join(
    os.path.dirname(__file__),
    "../frontend/dist"
)

# Static assets
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(frontend_path, "assets")),
    name="assets"
)

# Favicon
@app.get("/favicon.svg")
def favicon():
    return FileResponse(os.path.join(frontend_path, "favicon.svg"))

# React app
@app.get("/{full_path:path}")
def serve_react(full_path: str):
    return FileResponse(os.path.join(frontend_path, "index.html"))