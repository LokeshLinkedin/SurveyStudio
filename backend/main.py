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
# 📦 PATH SETUP
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend/dist"))
ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")

print("📁 FRONTEND_DIR:", FRONTEND_DIR)
print("📁 ASSETS_DIR:", ASSETS_DIR)

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
# 🔹 GENERATE API
# =============================
@app.post("/generate")
async def generate(payload: List[Dict]):
    try:
        if not payload:
            return JSONResponse(
                status_code=400,
                content={"error": "Empty payload", "xml": ""}
            )

        xml = generate_xml(payload)
        return {"xml": xml}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "xml": ""}
        )


# =============================
# 🌐 STATIC FILES (CRITICAL)
# =============================
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
else:
    print("❌ ERROR: assets folder NOT found:", ASSETS_DIR)


# =============================
# 🌐 ROOT (React entry)
# =============================
@app.get("/")
def serve_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(status_code=500, content={"error": "index.html not found"})


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
# 🌐 HEALTH CHECK
# =============================
@app.get("/health")
def health():
    return {"status": "ok"}


# =============================
# 🌐 SPA FALLBACK (SAFE)
# =============================
@app.get("/{full_path:path}")
def serve_spa(full_path: str):

    # ❌ Never override API routes
    if full_path.startswith("preview") or full_path.startswith("generate"):
        return JSONResponse(status_code=404, content={"error": "API route not found"})

    # ❌ Never override static files
    if full_path.startswith("assets") or "." in full_path:
        return JSONResponse(status_code=404, content={"error": "Static file not found"})

    # ✅ Serve React app
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)

    return JSONResponse(status_code=500, content={"error": "Frontend build missing"})