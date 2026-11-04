import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def generate_analysis_excel(df, analysis_data, output_file="تحلیل_نهایی_نظریه_داده_بنیاد.xlsx"):
    # تبدیل اطلاعات به دیتافریم
    reviews = pd.DataFrame(analysis_data["concept_reviews"])
    reviews = reviews.rename(columns={
        "concept_id": "شناسه مفهوم",
        "original_concept": "مفهوم اولیه",
        "original_code": "کد اولیه",
        "code_correct": "صحت کدگذاری اولیه",
        "suggested_code": "کد پیشنهادی",
        "revised_concept": "مفهوم اصلاح‌شده",
        "explanation": "دلیل پیشنهاد",
        "confidence": "میزان اطمینان"
    })
    
    # شبیه‌سازی منطق ترکیب با داده‌های اصلی
    main_df = df.copy()
    main_df = main_df.rename(columns={
        "شناسه مفهوم": "شناسه مفهوم",
        "متن مصاحبه": "متن پاراگراف",
        "مفاهیم معنادار": "مفهوم اولیه",
        "کد": "کد اولیه"
    })
    
    final_df = main_df.merge(reviews, on="شناسه مفهوم", how="left", suffixes=("_source", "_analysis"))
    
    # ساخت فایل اکسل چندبرگه
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        final_df.to_excel(writer, sheet_name="بررسی مفاهیم", index=False)
        
    # زیباسازی و استایل‌دهی اکسل در اینجا پیاده‌سازی می‌شود (مانند کد نوت‌بوک)
    wb = load_workbook(output_file)
    for sheet in wb.worksheets:
        sheet.sheet_view.rightToLeft = True
        # تنظیمات فونت و فیلترها...
    wb.save(output_file)
    return output_file
