import os
import io
import json
import sqlite3
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from docx import Document

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_PLOT_LIBS = True
except ImportError:
    HAS_PLOT_LIBS = False

app = FastAPI(title="نظریه‌یار")

os.makedirs("static", exist_ok=True)
try:
    os.makedirs("templates", exist_ok=True)
except:
    pass

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DB_PATH = "nazariyeyar.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS concepts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paragraph_text TEXT,
            initial_concept TEXT,
            initial_code TEXT,
            revised_concept TEXT,
            suggested_code TEXT,
            explanation TEXT,
            confidence TEXT,
            code_correct BOOLEAN,
            researcher_decision TEXT,
            review_status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

PARADIGM_NAMES = {
    "causal_conditions": "شرایط علّی",
    "contextual_conditions": "شرایط زمینه‌ای",
    "intervening_conditions": "شرایط مداخله‌گر",
    "action_interaction_strategies": "راهبردهای کنش و تعامل",
    "consequences": "پیامدها"
}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM concepts")
    concepts = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT value FROM analysis_meta WHERE key='analysis'")
    row = cursor.fetchone()
    analysis = json.loads(row[0]) if row else None
    
    conn.close()
    
    source = concepts if len(concepts) > 0 else None
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "source": source,
        "source_name": "دیتابیس نظریه‌یار",
        "analysis": analysis
    })

@app.post("/upload-source")
async def upload_source(file: UploadFile = File(...)):
    contents = await file.read()
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    rows = []
    if ext == ".docx":
        doc = Document(io.BytesIO(contents))
        for table in doc.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if len(cells) >= 3:
                    rows.append((cells[0], cells[1], cells[2]))
    elif ext == ".xlsx":
        df_excel = pd.read_excel(io.BytesIO(contents))
        for _, r in df_excel.iterrows():
            rows.append((str(r.iloc[0]), str(r.iloc[1]), str(r.iloc[2])))
            
    if rows:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM concepts")
        for row_data in rows:
            cursor.execute('''
                INSERT INTO concepts (paragraph_text, initial_concept, initial_code, review_status)
                VALUES (?, ?, ?, 'pending')
            ''', (row_data[0], row_data[1], row_data[2]))
        conn.commit()
        conn.close()
        
    return RedirectResponse(url="/", status_code=303)

@app.post("/upload-analysis")
async def upload_analysis(file: UploadFile = File(...)):
    contents = await file.read()
    text = contents.decode("utf-8")
    
    if "JSON_DATA" in text:
        text = text.split("JSON_DATA", 1)[1].strip()
    text = text.replace("```json", "").replace("```", "").strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    
    if start != -1 and end > start:
        json_str = text[start:end]
        try:
            analysis_data = json.loads(json_str)
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO analysis_meta (key, value) VALUES ('analysis', ?)", (json.dumps(analysis_data, ensure_ascii=False),))
            
            reviews = analysis_data.get("concept_reviews", [])
            for rev in reviews:
                cursor.execute('''
                    UPDATE concepts 
                    SET revised_concept = ?, suggested_code = ?, explanation = ?, confidence = ?, code_correct = ?
                    WHERE id = ?
                ''', (
                    rev.get("revised_concept"), 
                    rev.get("suggested_code"),
                    rev.get("explanation"),
                    rev.get("confidence"),
                    1 if rev.get("code_correct") else 0,
                    rev.get("concept_id")
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error saving JSON:", e)
            
    return RedirectResponse(url="/", status_code=303)

@app.get("/prompt")
async def get_prompt():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, paragraph_text, initial_concept, initial_code FROM concepts")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    records = []
    for r in rows:
        records.append({
            "شناسه مفهوم": r["id"],
            "متن پاراگراف": r["paragraph_text"],
            "مفهوم اولیه": r["initial_concept"],
            "کدگذاری اولیه": r["initial_code"]
        })
    
    research_data = json.dumps(records, ensure_ascii=False, indent=2)
    
    prompt_template = """نقش شما: متخصص روش تحقیق کیفی و نظریه داده‌بنیاد با رویکرد اشتراوس و کوربین است.

داده‌های زیر شامل متن مصاحبه، مفاهیم معنادار استخراج‌‌شده توسط پژوهشگر و کدگذاری اولیه است. وظیفه شما تحلیل دقیق و ارائه خروجی به شکل فایل JSON است.

داده‌های مصاحبه:
[RESEARCH_DATA]

ساختار الزامی خروجی JSON در پایان پاسخ با عنوان JSON_DATA:

{
  "concept_reviews": [
    {
      "concept_id": 1,
      "original_concept": "...",
      "original_code": "...",
      "code_correct": true,
      "suggested_code": "...",
      "revised_concept": "...",
      "explanation": "...",
      "confidence": "زیاد/متوسط/کم"
    }
  ],
  "central_category": {
    "name": "...",
    "explanation": "...",
    "supporting_concept_ids": []
  },
  "paradigm": {
    "causal_conditions": [],
    "contextual_conditions": [],
    "intervening_conditions": [],
    "action_interaction_strategies": [],
    "consequences": []
  },
  "relationships": [
    {
      "from": "...",
      "to": "...",
      "explanation": "..."
    }
  ],
  "researcher_review_items": []
}"""
    
    master_prompt = prompt_template.replace("[RESEARCH_DATA]", research_data)
    return StreamingResponse(
        io.BytesIO(master_prompt.encode("utf-8")),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=master_prompt.txt"}
    )

@app.get("/download-excel")
async def download_excel():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM concepts")
    concepts_list = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT value FROM analysis_meta WHERE key='analysis'")
    row = cursor.fetchone()
    analysis_data = json.loads(row[0]) if row else {}
    conn.close()
    
    if not concepts_list:
        return HTMLResponse("داده‌ای برای خروجی وجود ندارد.")
        
    df_main = pd.DataFrame(concepts_list)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_main.to_excel(writer, sheet_name="بررسی مفاهیم", index=False)
        if "paradigm" in analysis_data:
            pd.DataFrame(analysis_data.get("relationships", [])).to_excel(writer, sheet_name="روابط", index=False)
            
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Grounded_Theory_Analysis.xlsx"}
    )
