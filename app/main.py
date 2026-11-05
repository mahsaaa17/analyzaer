from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.analysis_service import perform_grounded_theory_analysis

app = FastAPI(
    title="نظریه‌یار",
    description="دستیار هوشمند تحلیل مصاحبه‌های کیفی با روش داده‌بنیاد (Grounded Theory)"
)

# تنظیم مسیر قالب‌های HTML (Jinja2)
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """نمایش صفحه اصلی برای ورود متن مصاحبه توسط کاربر"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze_interview(request: Request, interview_text: str = Form(...)):
    """دریافت متن مصاحبه، اجرای تحلیل داده‌بنیاد و ارسال نتایج به صفحه گراف"""
    
    # اجرای سرویس تحلیل داده‌بنیاد
    analysis_result = perform_grounded_theory_analysis(interview_text)
    
    return templates.TemplateResponse("analysis_result.html", {
        "request": request,
        "interview_text": interview_text,
        "open_codes": analysis_result["open_codes"],
        "axial_codes": analysis_result["axial_codes"],
        "core_category": analysis_result["core_category"],
        "categories": analysis_result["categories"],
        "relations": analysis_result["relations"]
    })
