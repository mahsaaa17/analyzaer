# نظریه‌یار (Nazariye-Yar)

دستیار هوشمند تحلیل مصاحبه‌های کیفی و پیاده‌سازی متدولوژی داده‌بنیاد (Grounded Theory). این پروژه با فریمورک پرسرعت **FastAPI** و قالب‌های مدرن فرانت‌اند توسعه یافته است.

---

## ویژگی‌ها
* دریافت و پردازش متن مصاحبه‌های کیفی
* استخراج کدهای باز و مقوله مرکزی
* ساخت مدل پارادایمی و رسم نمودار مفهومی تعاملی (Grounded Theory Diagram) با استفاده از `Vis.js`
* طراحی رابط کاربری مینیمال، مدرن و سازگار با فونت Vazirmatn

---

## ساختار پروژه
```text
nazariye-yar/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── analysis_service.py
│   └── templates/
│       ├── index.html
│       └── analysis_result.html
├── requirements.txt
└── README.md