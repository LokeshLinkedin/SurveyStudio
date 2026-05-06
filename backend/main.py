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
# 📦 PATH SETUP (ROBUST)
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, "frontend", "dist"),
    os.path.join(BASE_DIR, "../frontend/dist"),
    os.path.abspath("frontend/dist"),
]

FRONTEND_DIR = None
for path in POSSIBLE_PATHS:
    if os.path.exists(path):
        FRONTEND_DIR = path
        break

if not FRONTEND_DIR:
    raise RuntimeError("❌ frontend/dist not found. Run `npm run build`")

ASSETS_DIR = os.path.join(FRONTEND_DIR, "assets")

print("✅ USING FRONTEND_DIR:", FRONTEND_DIR)
print("✅ USING ASSETS_DIR:", ASSETS_DIR)

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
# 🌐 STATIC FILES
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
# 🌐 SPA FALLBACK (FIXED)
# =============================
@app.get("/{full_path:path}")
def serve_spa(full_path: str):

    # ❌ Never override API routes
    if full_path.startswith("preview") or full_path.startswith("generate"):
        return JSONResponse(status_code=404, content={"error": "API route not found"})

    # ❌ Never override static assets
    if full_path.startswith("assets"):
        return JSONResponse(status_code=404, content={"error": "Static file not found"})

    # ✅ Serve React app (SPA routing)
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)

    return JSONResponse(status_code=500, content={"error": "Frontend build missing"})