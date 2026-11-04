import streamlit as st
import pandas as pd
import os
import json
from src.data_processor import process_uploaded_file
from src.excel_generator import generate_analysis_excel

st.set_page_config(
    page_title="سامانه تحلیل کیفی نظریه داده‌بنیاد",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل CSS برای راست‌چین سازی و زیباسازی صفحات
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, span, button, input, select, textarea, div, table, th, td {
        font-family: 'Vazirmatn', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f4e78;
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2c6aa0;
        color: white;
    }
    </style>
''', unsafe_allow_html=True)

st.title("📊 سامانه خودکار تحلیل کیفی (نظریه داده‌بنیاد)")
st.write("به کمک این ابزار می‌توانید مصاحبه‌ها را پردازش کرده، پرامپت تحلیل یکپارچه تولید کنید و نتایج را به فایل اکسل استاندارد و نمودار پارادایمی تبدیل کنید.")

# منوی کناری راهنما
with st.sidebar:
    st.header("راهنمای مراحل پژوهش")
    st.info("1. آپلود فایل مصاحبه (.docx یا .xlsx)
2. کپی پرامپت تولید شده برای هوش مصنوعی
3. دریافت پاسخ از هوش مصنوعی
4. آپلود فایل پاسخ (.json) و دانلود خروجی نهایی اکسل")

# مرحله اول: آپلود فایل مصاحبه
st.subheader("گام اول: آپلود فایل مصاحبه")
uploaded_file = st.file_uploader("فایل Word (.docx) یا Excel (.xlsx) خود را انتخاب کنید:", type=["docx", "xlsx"])

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    try:
        df = process_uploaded_file(uploaded_file.name, file_bytes)
        st.success(f"فایل '{uploaded_file.name}' با موفقیت پردازش شد!")
        st.write(f"تعداد کل مفاهیم استخراج شده: {len(df)}")
        st.dataframe(df.head(10), use_container_width=True)

        # ساخت پرامپت
        st.subheader("گام دوم: دریافت پرامپت برای ارسال به هوش مصنوعی")
        st.write("پرامپت زیر را کپی کرده و در ChatGPT یا Gemini برای تحلیل ارسال کنید:")

        research_data = ""
        for idx, row in df.iterrows():
            research_data += f"\n- شناسه مفهوم: {idx+1}\n  متن: {row.get('متن مصاحبه', '')}\n  مفهوم اولیه: {row.get('مفاهیم معنادار', '')}\n  کد اولیه: {row.get('کد', '')}\n"

        prompt_text = f"نقش شما: متخصص روش تحقیق کیفی و نظریه داده‌بنیاد با رویکرد اشتراوس و کوربین است. داده‌های زیر را تحلیل کنید...\n\n{research_data}"
        st.text_area("متن پرامپت آماده کپی:", value=prompt_text, height=250)

    except Exception as e:
        st.error(f"خطا در پردازش فایل: {e}")

# مرحله دوم: آپلود نتایج تحلیل
st.markdown("--- ")
st.subheader("گام سوم: آپلود فایل تحلیل (.json) و تولید خروجی")
analysis_file = st.file_uploader("فایل خروجی JSON تحلیل شده توسط هوش مصنوعی را در این بخش آپلود کنید:", type=["json"])

if analysis_file is not None:
    try:
        analysis_data = json.load(analysis_file)
        st.success("فایل تحلیل هوش مصنوعی با موفقیت خوانده شد!")
        st.write(f"مقوله محوری شناسایی شده: **{analysis_data.get('central_category', {}).get('name', 'ثبت نشده')}**")

        if st.button("تولید فایل نهایی اکسل"):
            # تولید فایل اکسل
            output_path = "تحلیل_نهایی_نظریه_داده_بنیاد.xlsx"
            generate_analysis_excel(df, analysis_data, output_path)

            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 دانلود فایل اکسل نهایی",
                    data=f,
                    file_name=output_path,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"خطا در پردازش فایل تحلیل: {e}")
