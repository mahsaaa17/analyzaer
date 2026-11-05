import os

# ساخت پوشه‌های ضروری
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# ۱. ساخت فایل templates/index.html
index_html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>نظریه‌یار | تحلیل کیفی</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="container">
<header class="topbar">
    <div class="brand">
        <div class="logo">ن</div>
        <div>
            <strong>نظریه‌یار</strong>
            <small>دستیار تحلیل کیفی داده‌بنیاد (اشتراوس و کوربین)</small>
        </div>
    </div>
    <span class="local">● اجرای محلی (SQLite)</span>
</header>
<section class="hero">
    <span>STRAUSS & CORBIN · GROUNDED THEORY</span>
    <h1>میز کار پژوهشگر</h1>
    <p>از داده خام مصاحبه تا بررسی مفاهیم، مقوله محوری و مدل پارادایمی.</p>
</section>
<div class="steps">
    <div>۱ ـ ورود داده</div>
    <div>۲ ـ تحلیل با ChatGPT</div>
    <div>۳ ـ بررسی و خروجی</div>
</div>
<div class="grid">
<section class="panel">
    <h2>۱. ورود اطلاعات مصاحبه</h2>
    <p>فایل Word مصاحبه یا Excel مفاهیم خود را انتخاب کنید.</p>
    <form action="/upload-source" method="post" enctype="multipart/form-data">
        <label class="filebox">
            <input type="file" name="file" accept=".docx,.xlsx,.xls" required>
            انتخاب فایل مصاحبه یا مفاهیم
        </label>
        <button class="btn" type="submit">بارگذاری اطلاعات</button>
    </form>
    {% if source is not none %}
    <div class="success">
        فایل {{source_name}} با موفقیت بارگذاری شد.<br>
        تعداد مفاهیم/پاراگراف‌ها: {{source|length}}
    </div>
    <a class="btn secondary" href="/prompt">دانلود دستور تحلیل برای ChatGPT</a>
    {% endif %}
</section>
<section class="panel">
    <h2>۲. ورود پاسخ هوش مصنوعی</h2>
    <p>فایل JSON تحلیل را که از ChatGPT دریافت کرده‌اید وارد کنید.</p>
    <form action="/upload-analysis" method="post" enctype="multipart/form-data">
        <label class="filebox">
            <input type="file" name="file" accept=".json,.txt" required>
            انتخاب فایل تحلیل JSON
        </label>
        <button class="btn" type="submit">بارگذاری تحلیل</button>
    </form>
    {% if analysis is not none %}
    <div class="success">فایل تحلیل با موفقیت دریافت و ذخیره شد.</div>
    <a class="btn secondary" href="/results">مشاهده نتایج تحلیل و مدل پارادایمی</a>
    {% endif %}
</section>
</div>
<footer>نظریه‌یار ـ ابزار محلی پژوهشگر کیفی</footer>
</div>
</body>
</html>"""

with open("templates/index.html", "w", encoding="utf-8") as f:
    f.write(index_html)

# ۲. ساخت فایل templates/results.html
results_html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>نتایج تحلیل | نظریه‌یار</title>
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<div class="container">
<header class="topbar">
    <a href="/">← بازگشت به صفحه اصلی</a>
    <strong>نتایج تحلیل کیفی داده‌بنیاد</strong>
</header>
<section class="hero">
    <span>ANALYSIS WORKSPACE</span>
    <h1>بررسی و ویرایش تحلیل</h1>
    <p>تصمیم نهایی درباره کدگذاری و مقوله محوری با پژوهشگر است.</p>
</section>
<section class="panel central">
    <h2>مقوله محوری</h2>
    <h3>{{central.get('name','')}}</h3>
    <p>{{central.get('explanation','')}}</p>
    <small>مفاهیم پشتیبان: {{central.get('supporting_concept_ids',[])|join('، ')}}</small>
</section>
<div class="downloads">
    <a class="btn" href="/download-excel">دانلود فایل Excel</a>
    <a class="btn secondary" href="/download-json">دانلود JSON ویرایش‌شده</a>
</div>
<section class="panel">
<h2>بررسی مفهوم به مفهوم</h2>
<form action="/save-review" method="post">
{% for r in reviews %}
{% set s = source_map.get(r.get('concept_id')|int, {}) %}
<article class="review">
<h3>مفهوم شماره {{r.get('concept_id')}}</h3>
<div class="evidence">
    <label>متن کامل پاراگراف</label>
    <p>{{s.get('متن مصاحبه','')}}</p>
</div>
<div class="twocol">
    <div>
        <label>مفهوم اولیه</label>
        <div class="readonly">{{s.get('مفاهیم معنادار','')}}</div>
    </div>
    <div>
        <label>کد اولیه</label>
        <div class="readonly">{{s.get('کد','')}}</div>
    </div>
</div>
<div class="twocol">
    <div>
        <label>مفهوم اصلاح‌شده</label>
        <input name="concept_{{r.get('concept_id')}}" value="{{r.get('revised_concept','')}}">
    </div>
    <div>
        <label>کد پیشنهادی</label>
        <select name="code_{{r.get('concept_id')}}">
            {% for option in ['شرایط علّی', 'شرایط زمینه‌ای', 'شرایط مداخله‌گر', 'راهبردهای کنش و تعامل', 'پیامدها', 'نیازمند بررسی پژوهشگر'] %}
            <option value="{{option}}" {% if r.get('suggested_code') == option %}selected{% endif %}>{{option}}</option>
            {% endfor %}
        </select>
    </div>
</div>
<label>دلیل پیشنهاد</label>
<textarea name="reason_{{r.get('concept_id')}}" rows="3">{{r.get('explanation','')}}</textarea>
<div class="meta">اطمینان: {{r.get('confidence','')}} | صحت کد اولیه: {{'درست' if r.get('code_correct') else 'نیازمند اصلاح'}}</div>
</article>
{% endfor %}
<button class="btn" type="submit">ذخیره اصلاحات پژوهشگر</button>
</form>
</section>
<section class="panel">
<h2>مدل پارادایمی</h2>
<div class="paradigm">
{% for key,title in paradigm_names.items() %}
<div class="paracard">
    <h3>{{title}}</h3>
    {% for item in paradigm.get(key,[]) %}
    <div class="paraitem">
        <b>{{item.get('name','')}}</b>
        <p>{{item.get('explanation','')}}</p>
    </div>
    {% endfor %}
</div>
{% endfor %}
</div>
</section>
<footer>نظریه‌یار ـ تحلیل کیفی داده‌بنیاد</footer>
</div>
</body>
</html>"""

with open("templates/results.html", "w", encoding="utf-8") as f:
    f.write(results_html)

# ۳. ساخت فایل static/style.css
style_css = """@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800&display=swap');
:root { --bg: #f3f5fa; --ink: #19243a; --muted: #718096; --blue: #3157d5; --green: #15977e; --line: #e5e9f1; --white: #ffffff; }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: 'Vazirmatn', Tahoma, sans-serif; line-height: 1.9; }
.container { max-width: 1150px; margin: auto; padding: 25px; }
.topbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 25px; }
.brand { display: flex; align-items: center; gap: 12px; }
.logo { width: 45px; height: 45px; border-radius: 14px; background: var(--blue); color: white; display: grid; place-items: center; font-size: 23px; font-weight: 800; }
.brand small { display: block; color: var(--muted); }
.local { color: var(--green); background: #e3f6ef; border-radius: 20px; padding: 5px 14px; font-size: 12px; }
.hero { background: linear-gradient(120deg, #182c58, #3157d5); color: white; padding: 40px; border-radius: 23px; margin-bottom: 25px; box-shadow: 0 12px 30px #233f8b22; }
.hero span { color: #c2d0ff; font-size: 11px; letter-spacing: 1px; }
.hero h1 { font-size: 32px; margin: 8px 0; }
.hero p { color: #e2e9ff; margin: 0; }
.steps { display: flex; justify-content: space-around; background: white; padding: 18px; border-radius: 15px; margin-bottom: 22px; font-size: 13px; font-weight: 600; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.panel { background: var(--white); border: 1px solid var(--line); border-radius: 19px; padding: 25px; margin-bottom: 20px; box-shadow: 0 5px 18px #1c315008; }
.panel h2 { font-size: 19px; margin-top: 0; }
.panel p { color: var(--muted); font-size: 13px; }
.filebox { display: block; border: 2px dashed #cbd4e6; border-radius: 14px; padding: 25px; text-align: center; margin: 20px 0; background: #fafbfe; cursor: pointer; }
.filebox input { display: block; width: 100%; margin-top: 12px; }
.btn { display: inline-block; background: var(--blue); color: white; border: none; border-radius: 11px; padding: 11px 20px; text-decoration: none; font-family: inherit; font-size: 13px; font-weight: 600; cursor: pointer; margin-top: 10px; }
.btn:hover { opacity: 0.88; }
.secondary { background: #e9eeff; color: var(--blue); }
.success { background: #e7f7f0; color: #16836e; padding: 12px; border-radius: 11px; margin-top: 15px; font-size: 13px; }
footer { text-align: center; color: #929bad; font-size: 12px; padding: 25px; }
.central { border-right: 5px solid var(--green); }
.central h3 { font-size: 22px; }
.downloads { display: flex; gap: 12px; margin-bottom: 20px; }
.review { border: 1px solid var(--line); border-radius: 15px; padding: 18px; margin: 18px 0; }
.review h3 { font-size: 15px; }
.evidence { background: #f5f7fb; padding: 13px; border-radius: 11px; margin: 12px 0; }
.evidence p { color: var(--ink); }
.twocol { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 13px 0; }
label { display: block; color: var(--muted); font-size: 12px; margin-bottom: 5px; }
input, textarea, select { width: 100%; padding: 11px; border: 1px solid var(--line); border-radius: 9px; font-family: inherit; font-size: 13px; background: white; color: var(--ink); }
textarea { resize: vertical; }
.readonly { background: #f5f7fb; border-radius: 9px; padding: 10px; font-size: 13px; }
.meta { color: var(--muted); font-size: 11px; margin-top: 10px; }
.paradigm { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
.paracard { border: 1px solid var(--line); border-radius: 14px; padding: 16px; }
.paracard h3 { color: var(--blue); font-size: 15px; }
.paraitem { border-top: 1px solid var(--line); pading: 10px 0; }
.paraitem b { font-size: 13px; }
.paraitem p { margin: 5px 0; }
@media(max-width: 750px) { .container { padding: 12px; } .grid, .paradigm, .twocol { grid-template-columns: 1fr; } }"""

with open("static/style.css", "w", encoding="utf-8") as f:
    f.write(style_css)

print("تمام فایل‌ها و پوشه‌ها با موفقیت ساخته شدند!")